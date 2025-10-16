from odoo.http import request, route, Controller
from odoo import http


class InvoiceReplyController(http.Controller):

    @http.route('/api/invoice/reply', type='json', auth='public', methods=['POST'], csrf=False, cors='*')
    def invoice_reply(self, **kwargs):
        params = kwargs.get('params', {})
        invoice_no = request.params.get('invoice_no')
        mail_replied = request.params.get('mail_replied')

        if not invoice_no:
            return {'error': 'Missing invoice_no'}

        invoice = request.env['account.move'].sudo().search([('name', '=', invoice_no)], limit=1)

        if not invoice:
            return {'error': f"Invoice {invoice_no} not found"}

        invoice.mail_replied = bool(mail_replied)

        return {'status': 'success', 'updated_invoice': invoice_no}



class InvoiceMailLogController(http.Controller):

    @http.route('/api/invoice/mail-log', type='json', auth='public', methods=['POST'], csrf=False, cors='*')
    def create_mail_log(self, **kwargs):
        try:
            data = kwargs
            
            mail_values = {
                "subject": data.get("subject"),
                "email_from": data.get("email_from"),
                "email_to": data.get("email_to"),
                "email_cc": data.get("email_cc"),
                "reply_to": data.get("reply_to"),
                "scheduled_date": data.get("scheduled_date"),
                "body_html": data.get("body_html"),
            }

            # Add partner recipients if provided
            # if data.get("recipient_ids"):
            #     mail_values["recipient_ids"] = [(6, 0, data.get("recipient_ids"))]

            # Optional link to a model record
            # if data.get("model") and data.get("res_id"):
            #     mail_values.update({
            #         "model": data.get("model"),
            #         "res_id": data.get("res_id")
            #     })

            # Create the mail record
            mail = request.env["mail.mail"].sudo().create(mail_values)
            
            attachments = data.get("attachments", [])  # List of dicts: name, datas (base64), mimetype

            attachment_ids = []

            for attachment in attachments:
                name = attachment.get("name")
                datas = attachment.get("datas")  # base64 encoded string
                mimetype = attachment.get("mimetype", "application/octet-stream")

                if name and datas:
                    ir_attachment = request.env["ir.attachment"].sudo().create({
                        "name": name,
                        "datas": datas,
                        "res_model": "mail.mail",
                        "res_id": mail.id,
                        "mimetype": mimetype,
                        "type": "binary",
                    })
                    attachment_ids.append(ir_attachment.id)

            if attachment_ids:
                mail.sudo().write({
                    "attachment_ids": [(6, 0, attachment_ids)]
                })

            return {
                "status": "success",
                "mail_id": mail.id
            }

        except Exception as e:
            return {"error": str(e)}
