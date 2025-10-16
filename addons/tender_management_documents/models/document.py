from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import requests
import base64
import json




class TenderManagementDocument(models.Model):
    _name = 'tender.management.document'
    _description = 'Check List Document'
    _order = 'create_date desc'

    name = fields.Char('Name', required=True)
    description = fields.Text(string=" Description")
    
    # One2many relationship with Equipment
    equipment_ids = fields.One2many(
        'tender.equipment', 'tender_id', 
        string='Equipment'
    )
    
    attachment_ids = fields.One2many(
        'ir.attachment', 'res_id',
        domain=[('res_model', '=', 'tender.management.document')],
        string='Attachments'
    )
    upload_status = fields.Text('Upload Status', readonly=True)
    

    def upload_all_attachments_to_api(self):
        """Upload all attached files to external API"""
        self.ensure_one()

        if not self.attachment_ids:
            raise UserError("No attachments to upload.")

        for attachment in self.attachment_ids:
            try:
                # Decode the base64 file content
                decoded_file = base64.b64decode(attachment.datas or '')

                # Prepare file payload
                files = {
                    'file': (attachment.name or 'upload.bin', decoded_file, 'application/octet-stream')
                }

                # Try multiple endpoints and methods
                urls_to_try = [
                    'http://143.1.1.180:8000/v1/agents/upload/file',
                    'http://143.1.1.180:8000/v1/agents/upload',
                    'https://fastapi2.mo.vc/v1/agents/upload/file'
                ]
        
                success = False
                data = None
        
                for url in urls_to_try:
                    if success:
                        break
                
                    # Try POST method
                    try:
                        response = requests.post(url, files=files, timeout=120)
                        if response.status_code == 200:
                            success = True
                            data = response.json()
                            break
                    except:
                        pass

                # Check if we got successful response
                if success and data:
                    # Process the JSON data
                    equipment_count = 0
                    subtask_count = 0
                    interval_count = 0
                    task_count = 0
                    asset_count = 0
                
                    # Store created record IDs for updating the form
                    created_equipment_ids = []
                    created_asset_ids = []
                
                    # Process each equipment
                    for equipment_data in data:
                        equipment_name = equipment_data.get('Equipment Type', 'Unknown Equipment')
                        
                        # Create Equipment
                        equipment = self.env['tender.equipment'].create({
                            'tender_id': self.id,
                            'name': equipment_name,
                            'description': f"Equipment Type: {equipment_name}"
                        })
                        equipment_count += 1
                        created_equipment_ids.append(equipment.id)
                        
                        # AUTOMATICALLY CREATE ASSET FOR EACH EQUIPMENT
                        asset_vals = {
                            'names': equipment_name,  # Equipment name goes to asset name
                            'description': f"Asset auto-created from tender: {self.name}\nEquipment: {equipment_name}",
                            'model': '',
                            'serial': '',
                            'active': True,
                            'start_date': fields.Date.today(),
                            'purchase_date': fields.Date.today(),
                        }
                        
                        # Check if asset already exists
                        existing_asset = self.env['equipment.assets'].search([
                            ('names', '=', equipment_name)
                        ], limit=1)
                        
                        if not existing_asset:
                            new_asset = self.env['equipment.assets'].create(asset_vals)
                            created_asset_ids.append(new_asset.id)
                            asset_count += 1
                
                        # Process Sub-Types
                        for subtype in equipment_data.get('Sub-Types', []):
                            # Create Sub Task
                            subtask = self.env['tender.subtask'].create({
                                'equipment_id': equipment.id,
                                'name': subtype.get('Make/Model or Sub-Type', 'Unknown SubTask'),
                                'description': f"Make/Model: {subtype.get('Make/Model or Sub-Type', '')}",
                                'duration': '',
                                'dependencies': ''
                            })
                            subtask_count += 1
                    
                            # Process Intervals
                            for interval_data in subtype.get('Intervals', []):
                                # Create Interval
                                interval = self.env['tender.interval'].create({
                                    'subtask_id': subtask.id,
                                    'name': f"{interval_data.get('Service Type', '')} - {interval_data.get('Service No', '')}",
                                    'description': f"Service: {interval_data.get('Service Type', '')}\nService No: {interval_data.get('Service No', '')}\nInterval: {interval_data.get('Interval (Month)', '')} months\nEstimated Hours: {interval_data.get('Estimated Man Hours Required (TMC7)', '')}",
                                    'duration': f"{interval_data.get('Interval (Month)', '')} months",
                                    'dependencies': ''
                                })
                                interval_count += 1
                        
                                # Process Tasks (with auto question_type detection like checklist)
                                for task_data in interval_data.get('Tasks', []):
                                    # Detect question type from API data (like checklist logic)
                                    checklist_type = task_data.get('Checklist Type', '').strip().lower()
                                    raw_expected_output = task_data.get('Expected Output', '').strip().lower()
                                    
                                    # Initialize task values
                                    task_vals = {
                                        'interval_id': interval.id,
                                        'name': task_data.get('Task', 'Unknown Task')[:100],
                                        'description': task_data.get('Task', ''),
                                        'duration': f"{interval_data.get('Interval (Month)', '')} months",
                                        'dependencies': ''
                                    }
                                    
                                    # Set question_type and related fields based on API data
                                    if checklist_type == 'selection type':
                                        task_vals.update({
                                            'question_type': 'selection',
                                            'sel_attachment': 'no',  # Default
                                            'sel_expected_result': raw_expected_output if raw_expected_output in ['yes', 'no', 'not_applicable'] else 'yes',
                                            'sel_result': 'pass',
                                            'sel_result_color': 'yellow',
                                            'sel_weightage': 10
                                        })
                                    elif checklist_type == 'value type':
                                        # Determine statement type
                                        statement_type = 'numbervalue'
                                        if 'percent' in raw_expected_output:
                                            statement_type = 'percentage'
                                        elif 'number' in raw_expected_output:
                                            statement_type = 'numbervalue'
                                            
                                        task_vals.update({
                                            'question_type': 'value',
                                            'val_attachment': 'no',
                                            'val_statement_type': statement_type,
                                            'val_condition': 'Equal_To',
                                            'val_value': 100,
                                            'val_units': 'numbers',
                                            'val_result': 'pass',
                                            'val_result_color': 'yellow',
                                            'val_weightage': 10,
                                            'val_dangerous_if': 'higher',
                                            'val_compiled': 85.0,
                                            'val_obs': 70.0,
                                            'val_aoa': 60.0
                                        })
                                    else:
                                        # Default to selection type
                                        task_vals.update({
                                            'question_type': 'selection',
                                            'sel_attachment': 'no',
                                            'sel_expected_result': 'yes',
                                            'sel_result': 'pass',
                                            'sel_result_color': 'yellow',
                                            'sel_weightage': 10
                                        })
                                    
                                    # Create Task with pre-populated fields
                                    task = self.env['tender.task'].create(task_vals)
                                    task_count += 1
                
                    # Update the upload status with detailed info
                    self.upload_status = f"""Equipment data processed successfully!"""

                else:
                    # If all methods failed, show error
                    raise ValidationError(f"Failed to upload '{attachment.name}': All endpoints failed\nLast response: {response.status_code} - {response.text}")

            except ValidationError:
                raise  # Re-raise ValidationError
            except Exception as e:
                raise ValidationError(f"Error uploading attachment '{attachment.name}': {str(e)}")

    def test_api_connectivity(self):
        endpoints_to_test = [
            'http://143.1.1.180:8000/v1/agents/upload/file',
            'http://143.1.1.180:8000/v1/agents/upload',
            'http://fastapi2.mo.vc/v1/agents/upload/file',
            
        ]
        results = []
        for url in endpoints_to_test:
            try:
                response = requests.get(url, timeout=5)
                results.append(f"✓ {url} - Status: {response.status_code}")
            except requests.exceptions.ConnectionError:
                results.append(f"✗ {url} - Connection failed")
            except Exception as e:
                results.append(f"? {url} - {str(e)}")

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': "\n".join(results),
                'type': 'info',
                'sticky': True,
            }
        }


class TenderEquipment(models.Model):
    _name = 'tender.equipment'
    _description = 'Tender Equipment'

    name = fields.Char('Equipment Name', required=True)
    description = fields.Text('Equipment Description')
    
    tender_id = fields.Many2one(
        'tender.management.document', 
        string='Tender Document', 
        required=True, 
        ondelete='cascade'
    )
    
    subtask_ids = fields.One2many(
        'tender.subtask', 'equipment_id', 
        string='Sub Tasks'
    )


class TenderSubTask(models.Model):
    _name = 'tender.subtask'
    _description = 'Tender Sub Task'

    name = fields.Char('Sub Type', required=True)
    description = fields.Text('Sub Task Description')
    duration = fields.Char('Interval')
    dependencies = fields.Char('Dependencies')
    
    equipment_id = fields.Many2one(
        'tender.equipment', 
        string='Equipment', 
        required=True, 
        ondelete='cascade'
    )
    
    interval_ids = fields.One2many(
        'tender.interval', 'subtask_id', 
        string='Intervals'
    )


class TenderInterval(models.Model):
    _name = 'tender.interval'
    _description = 'Tender Interval'

    name = fields.Char('Service Type', required=True)
    description = fields.Text('Interval Description')
    duration = fields.Char('Interval')
    dependencies = fields.Char('Dependencies')
    
    subtask_id = fields.Many2one(
        'tender.subtask', 
        string='Sub Task', 
        required=True, 
        ondelete='cascade'
    )
    
    task_ids = fields.One2many(
        'tender.task', 'interval_id', 
        string='Tasks'
    )

    approval_status = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='pending', string='Approval Status')

    def approve_interval(self):
        """Approve interval and create checklist with questions from all tasks"""
        self.approval_status = 'approved'
        
        # Get current date and time
        current_datetime = fields.Datetime.now()
        current_user = self.env.user
        
        # Get the equipment name from the related equipment
        equipment_name = self.subtask_id.equipment_id.name
        
        # Find or create the asset
        asset = self.env['equipment.assets'].search([
            ('names', '=', equipment_name)
        ], limit=1)
        
        if not asset:
            # Create the asset record
            asset = self.env['equipment.assets'].create({
                'names': equipment_name,  # Equipment name goes to asset name
                'description': f"Asset created from tender: {self.subtask_id.equipment_id.tender_id.name}",
                'active': True,
                'start_date': fields.Date.today(),
                'purchase_date': fields.Date.today(),
            })
            asset_message = f'Asset "{asset.names}" created!'
        else:
            asset_message = f'Using existing asset "{asset.names}"'

        
        

        # Create checklist record with asset linked
        checklist = self.env['check.list'].create({
            'templatename': f"Checklist - {self.name}",
            'servicetype': False,
            'inspectiontype': 'equipment',            
            'equipment_category_id': False,
            'equipment_id': asset.id,  # Link the asset here
            'approval_date': current_datetime,
            'tender_interval_id': self.id,
        })
        
        # Create checklist questions from this interval's tasks
        question_count = 0
        
        for task in self.task_ids:
            question_count += 1
            
            # Create checklist line based on task's question_type
            if task.question_type == 'selection':
                line_vals = {
                    'test_line_appointment': checklist.id,
                    'question_no': f"Q{question_count:03d}",
                    'name': task.name[:200],
                    'guidelines': f"Equipment: {equipment_name}\nSubtask: {self.subtask_id.name}\nInterval: {self.name}",
                    'checklistquestion': 'checkbox',
                    'valuess': task.sel_expected_result,
                    'finalresult': task.sel_result,
                    'scores': task.sel_weightage,
                    'attachment_req': task.sel_attachment,
                    'dangerous_if': 'higher',
                    'value_1': 85.0,
                    'value_2': 70.0,
                    'value_3': 60.0,
                    'result_colour': task.sel_result_color
                }
            else:  # value type
                line_vals = {
                    'test_line_appointment': checklist.id,
                    'question_no': f"Q{question_count:03d}",
                    'name': task.name[:200],
                    'guidelines': f"Equipment: {equipment_name}\nSubtask: {self.subtask_id.name}\nInterval: {self.name}",
                    'checklistquestion': 'value',
                    'descriptions': task.val_statement_type,
                    'conditions': task.val_condition,
                    'conditionvalue': task.val_value,
                    'units': task.val_units,
                    'finalresult': task.val_result,
                    'scores': task.val_weightage,
                    'attachment_req': task.val_attachment,
                    'dangerous_if': task.val_dangerous_if,
                    'value_1': task.val_compiled,
                    'value_2': task.val_obs,
                    'value_3': task.val_aoa,
                    'result_colour': task.val_result_color
                }
            
            self.env['check.list.line'].create(line_vals)
        
        # Show success notification
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Interval Approved!',
                'message': f'Checklist created with {question_count} questions. {asset_message}',
                'type': 'success',
            }
        }


class TenderEquipment(models.Model):
    _name = 'tender.equipment'
    _description = 'Tender Equipment'

    name = fields.Char('Equipment Name', required=True)
    description = fields.Text('Equipment Description')
    
    tender_id = fields.Many2one(
        'tender.management.document', 
        string='Tender Document', 
        required=True, 
        ondelete='cascade'
    )
    
    subtask_ids = fields.One2many(
        'tender.subtask', 'equipment_id', 
        string='Sub Tasks'
    )

    @api.model
    def create(self, vals):
        """Override create to automatically create asset when equipment is created"""
        equipment = super(TenderEquipment, self).create(vals)
        
        # Automatically create asset for this equipment
        equipment_name = equipment.name
        
        # Check if asset already exists
        existing_asset = self.env['equipment.assets'].search([
            ('names', '=', equipment_name)
        ], limit=1)
        
        if not existing_asset:
            asset_vals = {
                'names': equipment_name,  # Equipment name goes to asset name
                'description': f"Asset auto-created from equipment: {equipment_name}",
                'active': True,
                'start_date': fields.Date.today(),
                'purchase_date': fields.Date.today(),
            }
            
            # Create the asset
            self.env['equipment.assets'].create(asset_vals)
        
        return equipment


class TenderSubTask(models.Model):
    _name = 'tender.subtask'
    _description = 'Tender Sub Task'

    name = fields.Char('Sub Type', required=True)
    description = fields.Text('Sub Task Description')
    duration = fields.Char('Interval')
    dependencies = fields.Char('Dependencies')
    
    equipment_id = fields.Many2one(
        'tender.equipment', 
        string='Equipment', 
        required=True, 
        ondelete='cascade'
    )
    
    interval_ids = fields.One2many(
        'tender.interval', 'subtask_id', 
        string='Intervals'
    )


class TenderInterval(models.Model):
    _name = 'tender.interval'
    _description = 'Tender Interval'

    name = fields.Char('Service Type', required=True)
    description = fields.Text('Interval Description')
    duration = fields.Char('Interval')
    dependencies = fields.Char('Dependencies')
    
    subtask_id = fields.Many2one(
        'tender.subtask', 
        string='Sub Task', 
        required=True, 
        ondelete='cascade'
    )
    
    task_ids = fields.One2many(
        'tender.task', 'interval_id', 
        string='Tasks'
    )

    approval_status = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='pending', string='Approval Status')

    def approve_interval(self):
        """Approve interval and create checklist with questions from all tasks"""
        self.approval_status = 'approved'
        
        # Get current date and time
        current_datetime = fields.Datetime.now()
        current_user = self.env.user
        
        # Get the equipment name from the related equipment
        equipment_name = self.subtask_id.equipment_id.name
        
        # Find the asset (should already exist from equipment creation)
        asset = self.env['equipment.assets'].search([
            ('names', '=', equipment_name)
        ], limit=1)
        
        if not asset:
            # Create asset if it doesn't exist (fallback)
            asset = self.env['equipment.assets'].create({
                'names': equipment_name,  # Equipment name goes to asset name
                'description': f"Asset created from tender: {self.subtask_id.equipment_id.tender_id.name}",
                'active': True,
                'start_date': fields.Date.today(),
                'purchase_date': fields.Date.today(),
            })
            asset_message = f'Asset "{asset.names}" created!'
        else:
            asset_message = f'Using asset "{asset.names}"'
        
        # Find related Tender Document (you need to decide how to link it)
        tender_document = self.env['tender.management.document'].search([], limit=1)
        
        # Create checklist record with asset linked
        checklist = self.env['check.list'].create({
            'templatename': f"Checklist - {self.name}",
            'servicetype': False,
            'document_id': tender_document.id, 
            'inspectiontype': 'equipment',            
            'equipment_category_id': False,
            'equipment_id': asset.id,  # Link the asset here
            'approval_date': current_datetime,
            'tender_interval_id': self.id,
        })
        
        # Create checklist questions from this interval's tasks
        question_count = 0
        
        for task in self.task_ids:
            question_count += 1
            
            # Create checklist line based on task's question_type
            if task.question_type == 'selection':
                line_vals = {
                    'test_line_appointment': checklist.id,
                    'question_no': f"Q{question_count:03d}",
                    'name': task.name[:200],
                    'guidelines': f"Equipment: {equipment_name}\nSubtask: {self.subtask_id.name}\nInterval: {self.name}",
                    'checklistquestion': 'checkbox',
                    'valuess': task.sel_expected_result,
                    'finalresult': task.sel_result,
                    'scores': task.sel_weightage,
                    'attachment_req': task.sel_attachment,
                    'dangerous_if': 'higher',
                    'value_1': 85.0,
                    'value_2': 70.0,
                    'value_3': 60.0,
                    'result_colour': task.sel_result_color
                }
            else:  # value type
                line_vals = {
                    'test_line_appointment': checklist.id,
                    'question_no': f"Q{question_count:03d}",
                    'name': task.name[:200],
                    'guidelines': f"Equipment: {equipment_name}\nSubtask: {self.subtask_id.name}\nInterval: {self.name}",
                    'checklistquestion': 'value',
                    'descriptions': task.val_statement_type,
                    'conditions': task.val_condition,
                    'conditionvalue': task.val_value,
                    'units': task.val_units,
                    'finalresult': task.val_result,
                    'scores': task.val_weightage,
                    'attachment_req': task.val_attachment,
                    'dangerous_if': task.val_dangerous_if,
                    'value_1': task.val_compiled,
                    'value_2': task.val_obs,
                    'value_3': task.val_aoa,
                    'result_colour': task.val_result_color
                }
            
            self.env['check.list.line'].create(line_vals)
        return True
       


class TenderTask(models.Model):
    _name = 'tender.task'
    _description = 'Tender Task'

    name = fields.Char('Task Name', required=True)
    description = fields.Text('Task Description')
    duration = fields.Char('Interval')
    dependencies = fields.Char('Dependencies')
    
    interval_id = fields.Many2one(
        'tender.interval', 
        string='Service Type/Service No', 
        required=True, 
        ondelete='cascade'
    )

    # Core fields
    approval_status = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='pending', string='Approval Status')

    question_type = fields.Selection([
        ('selection', 'Selection Type'),
        ('value', 'Value Type')
    ], string='Question Type', default='selection')

    # Selection Type Fields
    sel_question_type = fields.Char('Question Type', default='Selection')
    sel_attachment = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Attachment', default='no')
    sel_expected_result = fields.Selection([('yes', 'Yes'), ('no', 'No'), ('not_applicable', 'Not Applicable')], string='Expected Result', default='yes')
    sel_result = fields.Selection([('pass', 'Pass'), ('fail', 'Fail')], string='Result', default='pass')
    sel_result_color = fields.Selection([('yellow', 'OBS'), ('red', 'NC'), ('orange', 'AOA')], string='Result Color', default='yellow')
    sel_weightage = fields.Integer('Weightage', default=10)

    # Value Type Fields
    val_question_type = fields.Char('Question Type', default='Value')
    val_attachment = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Attachment', default='no')
    val_statement_type = fields.Selection([('numbervalue', 'Number Value'), ('percentage', 'Percentage')], string='Statement Type', default='numbervalue')
    val_condition = fields.Selection([('Equal_To', 'Equal To'), ('Greater_than', 'Greater Than'), ('Less_than', 'Less Than')], string='Condition', default='Equal_To')
    val_value = fields.Integer('Value', default=100)
    val_units = fields.Selection([('numbers', 'Numbers'), ('liters', 'Liters'), ('celsius', 'Celsius')], string='Units', default='numbers')
    val_result = fields.Selection([('pass', 'Pass'), ('fail', 'Fail')], string='Result', default='pass')
    val_result_color = fields.Selection([('yellow', 'OBS'), ('red', 'NC'), ('orange', 'AOA')], string='Result Color', default='yellow')
    val_weightage = fields.Integer('Weightage', default=10)
    val_dangerous_if = fields.Selection([('higher', 'Higher Values Dangerous'), ('lower', 'Lower Values Dangerous')], string='Dangerous If', default='higher')
    val_compiled = fields.Float('Compiled', default=85.0)
    val_obs = fields.Float('OBS', default=70.0)
    val_aoa = fields.Float('AOA', default=60.0)

    def create_checklist_from_task(self):
        """Create checklist from task after form is filled"""
        self.approval_status = 'approved'
        
        checklist = self.env['check.list'].create({
            'templatename': f"Task - {self.name}",
            'servicetype': False,
            'inspectiontype': 'equipment',
        })
        
        if self.question_type == 'selection':
            line_vals = {
                'test_line_appointment': checklist.id,
                'question_no': "T001",
                'name': self.name[:200],
                'checklistquestion': 'checkbox',
                'attachment_req': self.sel_attachment,
                'valuess': self.sel_expected_result,
                'finalresult': self.sel_result,
                'result_colour': self.sel_result_color,
                'scores': self.sel_weightage,
                'dangerous_if': 'higher',
                'value_1': 85.0,
                'value_2': 70.0,
                'value_3': 60.0,
            }
        else:
            line_vals = {
                'test_line_appointment': checklist.id,
                'question_no': "T001",
                'name': self.name[:200],
                'checklistquestion': 'value',
                'attachment_req': self.val_attachment,
                'descriptions': self.val_statement_type,
                'conditions': self.val_condition,
                'conditionvalue': self.val_value,
                'units': self.val_units,
                'finalresult': self.val_result,
                'result_colour': self.val_result_color,
                'scores': self.val_weightage,
                'dangerous_if': self.val_dangerous_if,
                'value_1': self.val_compiled,
                'value_2': self.val_obs,
                'value_3': self.val_aoa,
            }
        
        self.env['check.list.line'].create(line_vals)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': f'Checklist created for task "{self.name}"!',
                'type': 'success',
            }
        }





















































# from odoo import models, fields, api
# from odoo.exceptions import UserError, ValidationError
# import requests
# import base64
# import json

# class TenderManagementDocument(models.Model):
#     _name = 'tender.management.document'
#     _description = 'Check List Document'
#     _order = 'create_date desc'

#     name = fields.Char('Name', required=True)
#     description = fields.Text(string=" Description")
    
#     # One2many relationship with Equipment
#     equipment_ids = fields.One2many(
#         'tender.equipment', 'tender_id', 
#         string='Equipment'
#     )
    
#     attachment_ids = fields.One2many(
#         'ir.attachment', 'res_id',
#         domain=[('res_model', '=', 'tender.management.document')],
#         string='Attachments'
#     )
#     upload_status = fields.Text('Upload Status', readonly=True)
    

#     def upload_all_attachments_to_api(self):
#         """Upload all attached files to external API"""
#         self.ensure_one()

#         if not self.attachment_ids:
#             raise UserError("No attachments to upload.")

#         for attachment in self.attachment_ids:
#             try:
#                 # Decode the base64 file content
#                 decoded_file = base64.b64decode(attachment.datas or '')

#                 # Prepare file payload
#                 files = {
#                     'file': (attachment.name or 'upload.bin', decoded_file, 'application/octet-stream')
#                 }

#                 # Try multiple endpoints and methods
#                 urls_to_try = [
#                     #'http://:8000/v1/agents/upload',
#                     'http://143.1.1.180:8000/v1/agents/upload/file',
#                     'http://143.1.1.180:8000/v1/agents/upload',
#                 ]
        
#                 success = False
#                 data = None
        
#                 for url in urls_to_try:
#                     if success:
#                         break
                
#                     # Try POST method
#                     try:
#                         response = requests.post(url, files=files, timeout=120)
#                         if response.status_code == 200:
#                             success = True
#                             data = response.json()
#                             break
#                     except:
#                         pass

#                 # Check if we got successful response
#                 if success and data:
#                     # Process the JSON data
#                     equipment_count = 0
#                     subtask_count = 0
#                     interval_count = 0
#                     task_count = 0
                
#                     # Store created record IDs for updating the form
#                     created_equipment_ids = []
                
#                     # Process each equipment
#                     for equipment_data in data:
#                         # Create Equipment
#                         equipment = self.env['tender.equipment'].create({
#                             'tender_id': self.id,
#                             'name': equipment_data.get('Equipment Type', 'Unknown Equipment'),
#                             'description': f"Equipment Type: {equipment_data.get('Equipment Type', '')}"
#                         })
#                         equipment_count += 1
#                         created_equipment_ids.append(equipment.id)
                
#                         # Process Sub-Types
#                         for subtype in equipment_data.get('Sub-Types', []):
#                             # Create Sub Task
#                             subtask = self.env['tender.subtask'].create({
#                                 'equipment_id': equipment.id,
#                                 'name': subtype.get('Make/Model or Sub-Type', 'Unknown SubTask'),
#                                 'description': f"Make/Model: {subtype.get('Make/Model or Sub-Type', '')}",
#                                 'duration': '',
#                                 'dependencies': ''
#                             })
#                             subtask_count += 1
                    
#                             # Process Intervals
#                             for interval_data in subtype.get('Intervals', []):
#                                 # Create Interval
#                                 interval = self.env['tender.interval'].create({
#                                     'subtask_id': subtask.id,
#                                     'name': f"{interval_data.get('Service Type', '')} - {interval_data.get('Service No', '')}",
#                                     'description': f"Service: {interval_data.get('Service Type', '')}\nService No: {interval_data.get('Service No', '')}\nInterval: {interval_data.get('Interval (Month)', '')} months\nEstimated Hours: {interval_data.get('Estimated Man Hours Required (TMC7)', '')}",
#                                     'duration': f"{interval_data.get('Interval (Month)', '')} months",
#                                     'dependencies': ''
#                                 })
#                                 interval_count += 1
                        
#                                 # Process Tasks (with auto question_type detection like checklist)
#                                 for task_data in interval_data.get('Tasks', []):
#                                     # Detect question type from API data (like checklist logic)
#                                     checklist_type = task_data.get('Checklist Type', '').strip().lower()
#                                     raw_expected_output = task_data.get('Expected Output', '').strip().lower()
                                    
#                                     # Initialize task values
#                                     task_vals = {
#                                         'interval_id': interval.id,
#                                         'name': task_data.get('Task', 'Unknown Task')[:100],
#                                         'description': task_data.get('Task', ''),
#                                         'duration': f"{interval_data.get('Interval (Month)', '')} months",
#                                         'dependencies': ''
#                                     }
                                    
#                                     # Set question_type and related fields based on API data
#                                     if checklist_type == 'selection type':
#                                         task_vals.update({
#                                             'question_type': 'selection',
#                                             'sel_attachment': 'no',  # Default
#                                             'sel_expected_result': raw_expected_output if raw_expected_output in ['yes', 'no', 'not_applicable'] else 'yes',
#                                             'sel_result': 'pass',
#                                             'sel_result_color': 'yellow',
#                                             'sel_weightage': 10
#                                         })
#                                     elif checklist_type == 'value type':
#                                         # Determine statement type
#                                         statement_type = 'numbervalue'
#                                         if 'percent' in raw_expected_output:
#                                             statement_type = 'percentage'
#                                         elif 'number' in raw_expected_output:
#                                             statement_type = 'numbervalue'
                                            
#                                         task_vals.update({
#                                             'question_type': 'value',
#                                             'val_attachment': 'no',
#                                             'val_statement_type': statement_type,
#                                             'val_condition': 'Equal_To',
#                                             'val_value': 100,
#                                             'val_units': 'numbers',
#                                             'val_result': 'pass',
#                                             'val_result_color': 'yellow',
#                                             'val_weightage': 10,
#                                             'val_dangerous_if': 'higher',
#                                             'val_compiled': 85.0,
#                                             'val_obs': 70.0,
#                                             'val_aoa': 60.0
#                                         })
#                                     else:
#                                         # Default to selection type
#                                         task_vals.update({
#                                             'question_type': 'selection',
#                                             'sel_attachment': 'no',
#                                             'sel_expected_result': 'yes',
#                                             'sel_result': 'pass',
#                                             'sel_result_color': 'yellow',
#                                             'sel_weightage': 10
#                                         })
                                    
#                                     # Create Task with pre-populated fields
#                                     task = self.env['tender.task'].create(task_vals)
#                                     task_count += 1
                
#                     # Update the upload status with detailed info
#                     self.upload_status = f"""Equipment data processed successfully!"""

#                 else:
#                     # If all methods failed, show error
#                     raise ValidationError(f"Failed to upload '{attachment.name}': All endpoints failed\nLast response: {response.status_code} - {response.text}")

#             except ValidationError:
#                 raise  # Re-raise ValidationError
#             except Exception as e:
#                 raise ValidationError(f"Error uploading attachment '{attachment.name}': {str(e)}")


# class TenderEquipment(models.Model):
#     _name = 'tender.equipment'
#     _description = 'Tender Equipment'

#     name = fields.Char('Equipment Name', required=True)
#     description = fields.Text('Equipment Description')
    
#     tender_id = fields.Many2one(
#         'tender.management.document', 
#         string='Tender Document', 
#         required=True, 
#         ondelete='cascade'
#     )
    
#     subtask_ids = fields.One2many(
#         'tender.subtask', 'equipment_id', 
#         string='Sub Tasks'
#     )

#     # REMOVED approval_status and approve_equipment method


# class TenderSubTask(models.Model):
#     _name = 'tender.subtask'
#     _description = 'Tender Sub Task'

#     name = fields.Char('Sub Type', required=True)
#     description = fields.Text('Sub Task Description')
#     duration = fields.Char('Interval')
#     dependencies = fields.Char('Dependencies')
    
#     equipment_id = fields.Many2one(
#         'tender.equipment', 
#         string='Equipment', 
#         required=True, 
#         ondelete='cascade'
#     )
    
#     interval_ids = fields.One2many(
#         'tender.interval', 'subtask_id', 
#         string='Intervals'
#     )

#     # REMOVED approval_status and approve_subtask method


# class TenderInterval(models.Model):
#     _name = 'tender.interval'
#     _description = 'Tender Interval'

#     name = fields.Char('Service Type', required=True)
#     description = fields.Text('Interval Description')
#     duration = fields.Char('Interval')
#     dependencies = fields.Char('Dependencies')
    
#     subtask_id = fields.Many2one(
#         'tender.subtask', 
#         string='Sub Task', 
#         required=True, 
#         ondelete='cascade'
#     )
    
#     task_ids = fields.One2many(
#         'tender.task', 'interval_id', 
#         string='Tasks'
#     )

#     approval_status = fields.Selection([
#         ('pending', 'Pending'),
#         ('approved', 'Approved'),
#         ('rejected', 'Rejected')
#     ], default='pending', string='Approval Status')






 






#     def approve_interval(self):
#         """Approve interval and create checklist with questions from all tasks"""
#         self.approval_status = 'approved'
        

#         # Get current date and time
#         current_datetime = fields.Datetime.now()
#         current_user = self.env.user
        
#         # Create checklist record
#         checklist = self.env['check.list'].create({
#             'templatename': f"Checklist - {self.name}",
#             'servicetype': False,
#             'inspectiontype': 'equipment',            
#             'equipment_category_id': False,
#             'approval_date': current_datetime,
#             'tender_interval_id': self.id,
            
#         })
        
#         # Create checklist questions from this interval's tasks
#         question_count = 0
        
#         for task in self.task_ids:
#             question_count += 1
            
#             # Create checklist line based on task's question_type
#             if task.question_type == 'selection':
#                 line_vals = {
#                     'test_line_appointment': checklist.id,
#                     'question_no': f"Q{question_count:03d}",
#                     'name': task.name[:200],
#                     'guidelines': f"Equipment: {self.subtask_id.equipment_id.name}\nSubtask: {self.subtask_id.name}\nInterval: {self.name}",
#                     'checklistquestion': 'checkbox',
#                     'valuess': task.sel_expected_result,
#                     'finalresult': task.sel_result,
#                     'scores': task.sel_weightage,
#                     'attachment_req': task.sel_attachment,
#                     'dangerous_if': 'higher',
#                     'value_1': 85.0,
#                     'value_2': 70.0,
#                     'value_3': 60.0,
#                     'result_colour': task.sel_result_color
#                 }
#             else:  # value type
#                 line_vals = {
#                     'test_line_appointment': checklist.id,
#                     'question_no': f"Q{question_count:03d}",
#                     'name': task.name[:200],
#                     'guidelines': f"Equipment: {self.subtask_id.equipment_id.name}\nSubtask: {self.subtask_id.name}\nInterval: {self.name}",
#                     'checklistquestion': 'value',
#                     'descriptions': task.val_statement_type,
#                     'conditions': task.val_condition,
#                     'conditionvalue': task.val_value,
#                     'units': task.val_units,
#                     'finalresult': task.val_result,
#                     'scores': task.val_weightage,
#                     'attachment_req': task.val_attachment,
#                     'dangerous_if': task.val_dangerous_if,
#                     'value_1': task.val_compiled,
#                     'value_2': task.val_obs,
#                     'value_3': task.val_aoa,
#                     'result_colour': task.val_result_color
#                 }
            
#             self.env['check.list.line'].create(line_vals)
#         return True
        


# class TenderTask(models.Model):
#     _name = 'tender.task'
#     _description = 'Tender Task'

#     name = fields.Char('Task Name', required=True)
#     description = fields.Text('Task Description')
#     duration = fields.Char('Interval')
#     dependencies = fields.Char('Dependencies')
    
#     interval_id = fields.Many2one(
#         'tender.interval', 
#         string='Service Type/Service No', 
#         required=True, 
#         ondelete='cascade'
#     )

#     # Core fields
#     approval_status = fields.Selection([
#         ('pending', 'Pending'),
#         ('approved', 'Approved'),
#         ('rejected', 'Rejected')
#     ], default='pending', string='Approval Status')

#     question_type = fields.Selection([
#         ('selection', 'Selection Type'),
#         ('value', 'Value Type')
#     ], string='Question Type', default='selection')

#     # Selection Type Fields
#     sel_question_type = fields.Char('Question Type', default='Selection')
#     sel_attachment = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Attachment', default='no')
#     sel_expected_result = fields.Selection([('yes', 'Yes'), ('no', 'No'), ('not_applicable', 'Not Applicable')], string='Expected Result', default='yes')
#     sel_result = fields.Selection([('pass', 'Pass'), ('fail', 'Fail')], string='Result', default='pass')
#     sel_result_color = fields.Selection([('yellow', 'OBS'), ('red', 'NC'), ('orange', 'AOA')], string='Result Color', default='yellow')
#     sel_weightage = fields.Integer('Weightage', default=10)

#     # Value Type Fields
#     val_question_type = fields.Char('Question Type', default='Value')
#     val_attachment = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Attachment', default='no')
#     val_statement_type = fields.Selection([('numbervalue', 'Number Value'), ('percentage', 'Percentage')], string='Statement Type', default='numbervalue')
#     val_condition = fields.Selection([('Equal_To', 'Equal To'), ('Greater_than', 'Greater Than'), ('Less_than', 'Less Than')], string='Condition', default='Equal_To')
#     val_value = fields.Integer('Value', default=100)
#     val_units = fields.Selection([('numbers', 'Numbers'), ('liters', 'Liters'), ('celsius', 'Celsius')], string='Units', default='numbers')
#     val_result = fields.Selection([('pass', 'Pass'), ('fail', 'Fail')], string='Result', default='pass')
#     val_result_color = fields.Selection([('yellow', 'OBS'), ('red', 'NC'), ('orange', 'AOA')], string='Result Color', default='yellow')
#     val_weightage = fields.Integer('Weightage', default=10)
#     val_dangerous_if = fields.Selection([('higher', 'Higher Values Dangerous'), ('lower', 'Lower Values Dangerous')], string='Dangerous If', default='higher')
#     val_compiled = fields.Float('Compiled', default=85.0)
#     val_obs = fields.Float('OBS', default=70.0)
#     val_aoa = fields.Float('AOA', default=60.0)

#     def create_checklist_from_task(self):
#         """Create checklist from task after form is filled"""
#         self.approval_status = 'approved'
        
#         checklist = self.env['check.list'].create({
#             'templatename': f"Task - {self.name}",
#             'servicetype': False,
#             'inspectiontype': 'equipment',
#         })
        
#         if self.question_type == 'selection':
#             line_vals = {
#                 'test_line_appointment': checklist.id,
#                 'question_no': "T001",
#                 'name': self.name[:200],
#                 'checklistquestion': 'checkbox',
#                 'attachment_req': self.sel_attachment,
#                 'valuess': self.sel_expected_result,
#                 'finalresult': self.sel_result,
#                 'result_colour': self.sel_result_color,
#                 'scores': self.sel_weightage,
#                 'dangerous_if': 'higher',
#                 'value_1': 85.0,
#                 'value_2': 70.0,
#                 'value_3': 60.0,
#             }
#         else:
#             line_vals = {
#                 'test_line_appointment': checklist.id,
#                 'question_no': "T001",
#                 'name': self.name[:200],
#                 'checklistquestion': 'value',
#                 'attachment_req': self.val_attachment,
#                 'descriptions': self.val_statement_type,
#                 'conditions': self.val_condition,
#                 'conditionvalue': self.val_value,
#                 'units': self.val_units,
#                 'finalresult': self.val_result,
#                 'result_colour': self.val_result_color,
#                 'scores': self.val_weightage,
#                 'dangerous_if': self.val_dangerous_if,
#                 'value_1': self.val_compiled,
#                 'value_2': self.val_obs,
#                 'value_3': self.val_aoa,
#             }
        
#         self.env['check.list.line'].create(line_vals)
        
#         return {
#             'type': 'ir.actions.client',
#             'tag': 'display_notification',
#             'params': {
#                 'message': f'Checklist created for task "{self.name}"!',
#                 'type': 'success',
#             }
#         }










































