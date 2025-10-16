# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from odoo.exceptions import ValidationError
from datetime import date
import re
from dateutil.relativedelta import relativedelta
import base64
import requests

        

class CheckList(models.Model):
    _name = 'check.list'
    _description = 'Check List'
    _rec_name = 'templatename'
    _order = 'create_date desc'

    

    name = fields.Char(string='Check List Name')  
    document_id = fields.Many2one('tender.management.document',string="Document")
    guideline = fields.Text(string='Guidelines')
    checkcategory = fields.Many2one('check.category', string='Check List Category')
    templatename = fields.Char(string='Check List Name')
    types = fields.Many2one('check.type.line', string='Sub Category')

    servicetype = fields.Many2one('service.providertype', string='Service Category')
    inspectiontype = fields.Selection([
        ('property', 'Property'),
        ('equipment', 'Equipment'),
        ('document', 'Document/Reports')
    ], string='Workmen camp facility')

    appointment_lines = fields.One2many('check.list.line', 'test_line_appointment', string="Question")
    totalpoint = fields.Integer(string='Total Score')
    equipment_id = fields.Many2one('equipment.assets', string='Project Name')

    project_name = fields.Char(string='Equipment Name')

    equipment_category_id = fields.Many2one('equipment.category', string='Project Category')

    # New attachment field
    attachment_ids = fields.One2many(
        'ir.attachment', 'res_id',
        domain=lambda self: [('res_model', '=', self._name)],
        string='Attachments'
    )

    upload_status = fields.Text('Upload Status')

    approval_date = fields.Datetime(string='Approval Date')
    
    tender_interval_id = fields.Many2one('tender.interval', string='Source Interval')
   # equipment_id = fields.Many2one('equipment.assets', string='Project Name')

    
    


    def upload_and_process_attachments(self):
        """Upload all attached files to external API and process the response"""
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
                    'http://fastapi2.mo.vc/v1/agents/upload/file',
                    # 'http://fastapi2.mo.vc/v1/agents/upload',
                   
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
                    # Process the JSON data and create checklist lines
                    self._process_api_response(data, attachment.name)
                else:
                    # If all methods failed, show error
                    raise ValidationError(f"Failed to upload '{attachment.name}': All endpoints failed\nLast response: {response.status_code} - {response.text}")

            except ValidationError:
                raise  # Re-raise ValidationError
            except Exception as e:
                raise ValidationError(f"Error uploading attachment '{attachment.name}': {str(e)}")


    def _process_api_response(self, data, filename):
        """Process API response and create checklist lines"""
        question_count = 0
        
        # Clear existing appointment lines if any
        self.appointment_lines.unlink()
        
        # Store created line IDs for updating the form
        created_line_ids = []
        
        # Process the data structure based on your API response format
        for item in data:
            if isinstance(item, dict):
                # Process equipment level data
                equipment_type = item.get('Equipment Type', item.get('name', 'Unknown'))
                
                # Process sub-types if they exist
                sub_types = item.get('Sub-Types', item.get('subtypes', []))
                if not sub_types:
                    sub_types = [item]
                
                for subtype in sub_types:
                    # Process intervals/services
                    intervals = subtype.get('Intervals', subtype.get('services', []))
                    if not intervals:
                        intervals = [subtype]
                    
                    for interval_data in intervals:
                        # Get service information
                        service_type = interval_data.get('Service Type', 'Unknown Service')
                        # FIXED: Don't modify the service_no variable, use API value directly
                        api_service_no = interval_data.get('Service No', 'N/A')
                        
                        # Process tasks
                        tasks = interval_data.get('Tasks', interval_data.get('tasks', []))
                        if not tasks:
                            tasks = [{'Task': service_type}]
                        
                        for task_data in tasks:
                            task_name = task_data.get('Task', task_data.get('name', 'Unknown Task'))
                            
                            
                            checklist_type = task_data.get('Checklist Type', '').strip().lower()
                            raw_expected_output = task_data.get('Expected Output', '').strip().lower()

                            # Initialize
                            checklistquestion = False
                            valuess = False
                            statement_type = False

                            # Logic
                            if checklist_type == 'selection type':
                                checklistquestion = 'checkbox'
                                # Accept only yes, no, Not_Applicable
                                if raw_expected_output in ['yes', 'no', 'not_applicable']:
                                    valuess = raw_expected_output
                                else:
                                    valuess = 'yes'  # Default to yes
                            elif checklist_type == 'value type':
                                checklistquestion = 'value'
                                valuess = False  # not used
                                # Normalize the value to valid options
                                if 'percent' in raw_expected_output:
                                    statement_type = 'percentage'
                                elif 'number' in raw_expected_output:
                                    statement_type = 'numbervalue'
                                else:
                                    statement_type = 'numbervalue'  # Default if unrecognized

                            # checklist_type = task_data.get('Checklist Type', '').strip().lower()
                            # if checklist_type =='selection type':
                            #     checklistquestion = 'checkbox'
                            # elif checklist_type == 'value type':
                            #     checklistquestion = 'value'
                            # else:
                            #     checklistquestion = False
                            


                            # Create checklist line
                            line_vals = {
                                'test_line_appointment': self.id,
                                'question_no': api_service_no,  # Use API service number directly
                                'name': task_name[:200],
                                'guidelines': f"Service: {service_type}\nEquipment: {equipment_type}",
                                'checklistquestion': checklistquestion,
                                #'valuess': task_data.get('Expected Output', 'yes').lower() if checklistquestion == 'checkbox' else False,
                                'valuess': valuess,
                                'descriptions': statement_type, 
                                'finalresult': 'pass',
                                'scores': 10,
                                'attachment_req': 'no',
                                'dangerous_if': 'higher',
                                'value_1': 85.0,
                                'value_2': 70.0,
                                'value_3': 60.0,
                                'result_colour': 'yellow'
                            }
                            
                            
                            
                            line = self.env['check.list.line'].create(line_vals)
                            created_line_ids.append(line.id)
                            question_count += 1
                            # REMOVED: service_no += 1  (This was causing the issue)
        
        # Update the upload status
        self.upload_status = f"""File processed successfully!
    File: {filename}
    Questions created: {question_count}"""
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }




    @api.model
    def create(self, vals):
        result = super(CheckList, self).create(vals)
        return result

class CheckListLine(models.Model):
    _name = 'check.list.line'
    _description = 'Check List Line'

    name = fields.Char(string='Question', required=True)

    descriptions = fields.Selection([
        ('numbervalue', 'NUMBER VALUE'), 
        ('percentage', 'PERCENTAGE VALUE')
    ], string='Statement Type')

    valuess = fields.Selection([
        ('yes', 'Yes'), 
        ('no', 'No'), 
        ('Not_Applicable', 'Not Applicable')
    ], string='Expected Result')

    selections = fields.Selection([
        ('yesorno', 'YES(or)NO')
    ], string='Statement Type')

    conditions = fields.Selection([
        ('Equal_To', 'Equal to'), 
        ('Not_Equal', 'Not Equal to'),
        ('Greather_than', 'Greater Than'),
        ('Less_than', 'Less Than'),
        ('Inbetween', 'In Between')
    ], string='Condition')

    expectedresult = fields.Char(
        string='Expected Result',
        compute='_compute_complete_name',
        store=True
    )

    valueofnumber = fields.Integer(string='Expected Result Range (From)')
    # question_no = fields.Integer(string='Service No')
    question_no = fields.Char(string='Service No')

    @api.depends('conditions', 'conditionvalue', 'valuess')
    def _compute_complete_name(self):
        for category in self:
            if category.conditionvalue:
                category.expectedresult = '%s %s' % (category.conditions or '', category.conditionvalue)
            else:
                category.expectedresult = category.valuess or ''

    valueofnumberto = fields.Integer(string='In Between')
    guidelines = fields.Text(string='Guidelines')

    units = fields.Selection([
        ('liters', 'Liter(s)'), 
        ('fahrenheit', 'Fahrenheit (°F)'),
        ('celsius', 'Celsius (°C)'),
        ('grams', 'Grams'),
        ('Kilogram', 'Kilogram'),
        ('numbers', 'NOs'),
        ('units', 'Unit(s)'),
        ('volt', 'Volt(V)'),
        ('ohm', 'Ohm (Ω)'),
        ('met', 'Met(M)'),
        ('sqm', 'SQM'),
        ('person', 'Person'),
        ('lux', 'Lux'),
        ('room', 'Room'),
        ('monthly', 'Monthly')
    ], string='Units')

    scores = fields.Integer(string='Weightage', required=True)

    subcategory = fields.Many2one(
        'check.type.line',
        related='test_line_appointment.types',
        string='Sub Category'
    )

    conditionvalue = fields.Integer(string='Value')
    test_line_appointment = fields.Many2one('check.list', string="Name of List")

    finalresult = fields.Selection([
        ('pass', 'Pass'), 
        ('fail', 'Fail')
    ], string='Result', required=True)

    checklistquestion = fields.Selection([
        ('checkbox', 'Selection'), 
        ('value', 'Value')
    ], string="Question Type", store=True)

    checkcategory = fields.Many2one(
        'check.category',
        related='test_line_appointment.checkcategory',
        string='Check Category'
    )

    result_colour = fields.Selection([
        ('red', 'NC'), 
        ('yellow', 'OBS'),
        ('orange', 'AOA')
    ], string='Result Colour', default='yellow')

    attachment_req = fields.Selection([
        ('yes', 'Yes'), 
        ('no', 'NO')
    ], string="Attachment", default='no')

    dangerous_if = fields.Selection([
        ('higher', 'Higher Values Dangerous'),
        ('lower', 'Lower Values Dangerous')
    ], string="Dangerous If", required=True)

    value_1 = fields.Float(string="Compiled", required=True, store=True)
    value_2 = fields.Float(string="OBS", required=True, store=True)
    value_3 = fields.Float(string="AOA", required=True, store=True)

class CheckCategory(models.Model):
    _name = 'check.category'
    _description = 'Check Category'

    name = fields.Char(string='Check List Category')
    checklisttypes = fields.One2many('check.type.line', 'category', string="Check List Line")



