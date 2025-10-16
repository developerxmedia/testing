import requests
import json
import base64
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class TenderManagement(models.Model):
    _name = 'tender.management'
    _description = 'Tender Management'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(string='Tender Name', required=True, tracking=True)
    description = fields.Text(string='Tender Description')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date', required=True, tracking=True)
    document_upload = fields.Binary(string='Document Upload', required=True, attachment=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('evaluated', 'Evaluated'),
        ('success', 'Success'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'tender_ir_attachments_rel',
        'tender_id', 'attachment_id',
        string='Attachments'
    )
    evaluate_json = fields.Text(string='Evaluate Json')
    evaluate_result = fields.Html(string='Evaluation Result')


    channel_id = fields.Many2one('discuss.channel', string='Chat Channel', readonly=True)

    @api.model
    def create(self, vals):
        record = super(TenderManagement, self).create(vals)

        # ✅ Create a new Discuss channel
        channel = self.env['discuss.channel'].create({
            'name': f"Tender Chat - {record.name}",
            'channel_type': 'channel',  # could be 'chat', 'channel' or 'livechat'
            # 'public': 'private',  # or 'public' if you want open visibility
            'channel_partner_ids': [(4, self.env.user.partner_id.id)],
        })

        # ✅ Link the channel to the tender record
        record.channel_id = channel.id

        return record
    
    def action_open_channel(self):
        """Redirect user to the Discuss app focused on this tender's channel."""
        self.ensure_one()
        if not self.channel_id:
            raise ValidationError("No chat channel linked to this tender.")

        # Use correct menu_id and action ID from your system
        menu_id = 70
        action_id = 107
        channel_xml_id = f"discuss.channel_{self.channel_id.id}"

        return {
            'type': 'ir.actions.act_url',
            'url': f"/web#action={action_id}&menu_id={menu_id}&active_id={channel_xml_id}",
            'target': 'self',
        }

    def action_evaluate_document(self):
        """Send all attached documents to FastAPI for evaluation (as JSON per file)"""
        self.ensure_one()

        if not self.attachment_ids:
            raise UserError("Please attach at least one document to evaluate.")

        session_id = str(self.id)
        user_id = str(self.id)
        result_json_dict = {}

        for attachment in self.attachment_ids:
            if not attachment.datas:
                continue

            try:
                decoded_file = base64.b64decode(attachment.datas)
                files = {
                    'file': (attachment.name or 'document.pdf', decoded_file, 'application/pdf'),
                }

                data = {
                    'session_id': session_id,
                    'user_id': user_id,
                    'message': '',
                    'tender_id': self.id,  # ✅ Added new parameter
                }

                fastapi_url = 'http://143.1.1.180:8700/v1/agents/uploadfile'  # ✅ Updated URL

                response = requests.post(
                    fastapi_url,
                    files=files,
                    data=data,
                    timeout=120
                )

                if response.status_code == 200:
                    result = response.json()
                    # raise ValidationError(result)
                    result_json_dict[attachment.name] = result
                else:
                    raise UserError(f"FastAPI error on '{attachment.name}': {response.status_code} - {response.text}")

            except Exception as e:
                raise UserError(f"Failed to evaluate '{attachment.name}': {str(e)}")

        # Save the raw JSON results
        self.evaluate_json = json.dumps(result_json_dict, indent=2)
        self.state = 'evaluated'

        # Call the button_evaluate_result to format the results
        return self.button_evaluate_result()



    # def action_evaluate_document(self):
    #     """Send all attached documents to FastAPI for evaluation (as JSON per file)"""
    #     self.ensure_one()

    #     if not self.attachment_ids:
    #         raise UserError("Please attach at least one document to evaluate.")

    #     session_id = str(self.id)
    #     user_id = str(self.id)
    #     result_json_dict = {}

    #     for attachment in self.attachment_ids:
    #         if not attachment.datas:
    #             continue

    #         try:
    #             decoded_file = base64.b64decode(attachment.datas)
    #             files = {
    #                 'file': (attachment.name or 'document.pdf', decoded_file, 'application/pdf'),
    #             }

    #             data = {
    #                 'session_id': session_id,
    #                 'user_id': user_id,
    #                 'message': '',
    #             }

    #             fastapi_url = 'http://143.1.1.180:8000/v1/agents/uploadfile'

    #             response = requests.post(
    #                 fastapi_url,
    #                 files=files,
    #                 data=data,
    #                 timeout=120
    #             )

    #             if response.status_code == 200:
    #                 result = response.json()
    #                 # raise ValidationError(result)
    #                 result_json_dict[attachment.name] = result
    #             else:
    #                 raise UserError(f"FastAPI error on '{attachment.name}': {response.status_code} - {response.text}")

    #         except Exception as e:
    #             raise UserError(f"Failed to evaluate '{attachment.name}': {str(e)}")

    #     # Save the raw JSON results
    #     self.evaluate_json = json.dumps(result_json_dict, indent=2)
    #     self.state = 'evaluated'

    #     # Call the button_evaluate_result to format the results
    #     return self.button_evaluate_result()


    def button_evaluate_result(self):
        """Format the evaluation results into HTML tables"""
        self.ensure_one()
        self.state = 'success'
        
        if not self.evaluate_json:
            self.evaluate_result = "<p>No evaluation data available. Please evaluate the documents first.</p>"
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Info',
                    'message': 'No evaluation data available. Please evaluate the documents first.',
                    'type': 'warning',
                    'sticky': False,
                }
            }

        try:
            parsed_data = json.loads(self.evaluate_json)
            
            if isinstance(parsed_data, dict):
                all_tables = ""
                for filename, data_list in parsed_data.items():
                    if isinstance(data_list, list) and data_list:
                        # Section Title
                        all_tables += f"<h4>{filename}</h4>"
                        all_tables += "<table border='1' style='width:100%; border-collapse: collapse;'>"
                        
                        # Headers
                        headers = data_list[0].keys()
                        all_tables += "<thead><tr>"
                        for header in headers:
                            all_tables += f"<th>{header.replace('_', ' ').title()}</th>"
                        all_tables += "</tr></thead><tbody>"

                        # Rows
                        for item in data_list:
                            all_tables += "<tr>"
                            for value in item.values():
                                all_tables += f"<td>{value}</td>"
                            all_tables += "</tr>"
                        all_tables += "</tbody></table><br/>"
                    else:
                        all_tables += f"<p>No data found in {filename}</p>"

                self.evaluate_result = all_tables
                success_message = "Documents evaluated and results formatted successfully!"
            else:
                self.evaluate_result = "<p>Invalid structure: Expected a dictionary per file</p>"
                success_message = "Evaluation completed with formatting issues."
                
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
                # 'params': {
                #     'title': 'Success',
                #     'message': success_message,
                #     'type': 'success',
                #     'sticky': False,
                # }
            }
                
        except json.JSONDecodeError:
            self.evaluate_result = "<p>Invalid JSON format in evaluation results</p>"
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error',
                    'message': 'Failed to parse evaluation results',
                    'type': 'danger',
                    'sticky': False,
                }
            }

    def action_reset_to_draft(self):
        """Reset tender to draft state"""
        self.state = 'draft'
        
    def action_cancel(self):
        """Cancel tender"""
        self.state = 'cancelled'

 