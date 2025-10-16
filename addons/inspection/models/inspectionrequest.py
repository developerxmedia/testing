# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from odoo.exceptions import ValidationError
from datetime import date
import re
import passlib
from dateutil.relativedelta import relativedelta
from datetime import datetime, date, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import  UserError
import pytz
import logging
_logger = logging.getLogger(__name__)




class inspectionrequest(models.Model):
    _name = 'inspection.request'
    _rec_name = 'name_seq'
    _inherit = ['mail.thread', 'mail.activity.mixin',]    
    _order = 'id desc'


    document_id = fields.Many2one(
        'tender.management.document',
        string='Checklist Document'
    )

    document_name = fields.Char(
        string='Checklist Name',
        related='document_id.name',
        store=True
    )

    @api.depends('inspcheck_twolines.passcount', 'inspcheck_twolines.failcount', 'inspcheck_twolines.score',
                'inspectioncheck_twolines.passcount', 'inspectioncheck_twolines.failcount', 'inspectioncheck_twolines.score')
    def _compute_overall_scores(self):
        """Automatically compute overall scores from sub-tasks"""
        for record in self:
            if record.asset_type == 'equipment':
                # For equipment inspections
                lines = record.inspcheck_twolines
            else:
                # For property inspections  
                lines = record.inspectioncheck_twolines
            
            record.overall_score = sum(line.score for line in lines)
            record.overall_passcount = sum(line.passcount for line in lines)
            record.overall_failcount = sum(line.failcount for line in lines)
            record.overall_redcount = sum(line.redcount for line in lines)
            record.overall_yellowcount = sum(line.yellowcount for line in lines)
            record.overall_orangecount = sum(line.orangecount for line in lines)

    # Update your field definitions to use computed fields:
    overall_score = fields.Integer(string='Overall Score', compute='_compute_overall_scores', store=True)
    overall_passcount = fields.Integer(string='Overall Pass', compute='_compute_overall_scores', store=True)
    overall_failcount = fields.Integer(string='Overall Fail', compute='_compute_overall_scores', store=True)
    overall_redcount = fields.Integer(string='NC', compute='_compute_overall_scores', store=True)
    overall_yellowcount = fields.Integer(string='OBS', compute='_compute_overall_scores', store=True)
    overall_orangecount = fields.Integer(string='AOA', compute='_compute_overall_scores', store=True)

    def create_consolidated_report(self):
        self.overall_score = 0
        self.overall_passcount = 0
        self.overall_failcount = 0
        self.overall_redcount = 0
        self.overall_yellowcount = 0
        self.overall_orangecount = 0
        for rec in self.inspcheck_twolines:
            self.overall_score += rec.score
            self.overall_passcount += rec.passcount
            self.overall_failcount += rec.failcount
            self.overall_redcount += rec.redcount
            self.overall_yellowcount += rec.yellowcount
            self.overall_orangecount += rec.orangecount

    name_seq = fields.Char(string='Req No', required=False, copy=False, readonly=True, index=True, default=lambda self:_('New')) 

    names = fields.Char(string='Inspection Name')
    priority = fields.Selection([('1', 'Low'), ('2', 'Medium'), ('3', 'High')])
    priority_new = fields.Selection([('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], string='Priority')

    inspectors = fields.Many2one('hr.employee', string='Inspector')
    cron_task = fields.Boolean('Cron Tasks')
    
    planweightage = fields.Integer(string='Plan Weightage')
    scoreweightage = fields.Integer(string='Score Weightage')    
    created_by = fields.Many2one('res.users', 'Created By', default=lambda self: self.env.user, readonly=True)

    inspectionstart = fields.Datetime(string="Inspection Start Time")
    inspectionend = fields.Datetime(string="Inspection End Time")

    date = fields.Datetime(string='Created date', default=fields.Datetime.now, readonly=True) 
    scheduleddate = fields.Date(string="Scheduled Date")  
    manager_id = fields.Many2one('hr.employee', string="Manager", track_visibility='onchange')
    
    inspection_lines = fields.One2many('inspection.request.line', 'testline_inspection', string="Inspection of Property")
    inspection_twolines = fields.One2many('inspection.request.twoline', 'testtwoline_inspection', string="Inspection of Equipment ")
    inspectioncheck_twolines = fields.One2many('inspection.check.twoline', 'checktwoline_inspection', string="Inspection of Check ")
    
    assignto = fields.Many2one('hr.employee', string="Assign To", required=False, track_visibility='onchange')
    task_type = fields.Selection(string='Task Type',
        selection=[('task', 'Predictive Maintenance'), ('complaint', 'Breakdown Maintenance')], default="task")    
    inspcheck_twolines = fields.One2many('inspectiontwo.check.twoline', 'checktwoline_insp', string="Inspection of Check equipment ")

    # New fields
    servicecate = fields.Many2one('service.providertype', string="Service Category", required=False)
    building = fields.Many2one('property.building', string="Building /Area")
    propertys = fields.Many2one('property.land', string="Property Name")
    floor = fields.Many2one('property.floors', string="Floor Name")
    room = fields.Many2one('property.room', string="Room Name")
    equipments = fields.Many2one('equipment.assets', string="Equipment Name")
    checklistcate = fields.Many2one('check.list', string="Check List Name") 
    checklist_many = fields.Many2many('check.list', string="Audit Lists")   
    
    checklist_count = fields.Integer(compute='compute_count')         
    checklistequip_count = fields.Integer(compute='compute_countequip')    
    notification_count = fields.Integer(compute='compute_notification_count') 

    
    equipment_id = fields.Many2one('equipment.assets', string='Asset Name')

    @api.onchange('checklist_document_id')
    def _onchange_checklist_document_id(self):
        if self.checklist_document_id:
            equipment_names = self.checklist_document_id.equipment_ids.mapped('name')
            return {
                'domain':{
                    'equipment_id': [('name', 'in', equipment_names)]
                    
                }
            }
        return {'domain': {'equipment_id': []}}

    



    
    



    def compute_notification_count(self):
        for record in self:
            record.notification_count = self.env['notification.list'].search_count([('inspection_task', '=', record.id)])
    
    def notification_view(self):
        return   { 
                    'name': ('Notification Alerts'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'notification.list',
                    'view_mode': 'tree,form',
                    'domain':[('inspection_task', '=', self.id)], 
                    'context': "{'create': False}",
                        }

    def compute_count(self):
        for record in self:
            record.checklist_count = self.env['inspection.check.twoline'].search_count([('checktwoline_inspection', '=', record.id)])

    def compute_countequip(self):
        for record in self:
            record.checklistequip_count = self.env['inspectiontwo.check.twoline'].search_count([('checktwoline_insp', '=', record.id)])    

    def update_inspection(self):
        if self.asset_type == "property":
            self.state = 'draft'
            notification_create = self.env['notification.list'].create({
                'name': f"Ticket {self.name_seq} has Been Allocated",
                'read_status': 'un_read',
                'date': date.today(),
                'inspection_task': self.id,
                'res_users': self.assignto.user_id.id,
                'res_partner_id': self.assignto.user_id.partner_id.id,
                'description': f"Ticket {self.name_seq} has Been Allocated to {self.assignto.user_id.name} Successfully !!!",
                'manager': True if self.assignto.user_id.type_users == 'manager' else False,
                'user': True if self.assignto.user_id.type_users == 'user' else False,
                'tech': True if self.assignto.user_id.type_users == 'tech' else False,
            })
        else:
            notification_create = self.env['notification.list'].create({
                'name': f"Ticket {self.name_seq} has Been Allocated",
                'read_status': 'un_read',
                'date': date.today(), 
                'inspection_task': self.id,
                'res_users': self.assignto.user_id.id,
                'res_partner_id': self.assignto.user_id.partner_id.id,
                'description': f"Ticket {self.name_seq} has Been Allocated to {self.assignto.user_id.name} Successfully !!!",
                'manager': True if self.assignto.user_id.type_users == 'manager' else False,
                'user': True if self.assignto.user_id.type_users == 'user' else False,
                'tech': True if self.assignto.user_id.type_users == 'tech' else False,
            })

    def create_sequence_inspection(self):
        """Working solution - comments out the problematic categrylines assignment"""
        
        self.servicecate = 1
        self.request_date = date.today()
        questions = self.env['check.list'].search([('id', '=', self.checklistcate.id)])

        if not self.assignto:
            self.state = 'pending'
        else:
            self.state = 'draft'

        if self.asset_type == "property":
            # self['name_seq'] = "IR0000" + str(self.id)
            self['task_type'] = 'task'

            for check in self.inspectioncheck_twolines:
                check.name_seq = 'ST0000' + str(check.id)
                check.state = 'incomplete'
                check.asset_types = 'property'

            # Fix: Ensure check is in scope for checklist creation
            for check in self.inspectioncheck_twolines:
                for question in questions.appointment_lines:
                    checklist = {
                        'names': question.id,
                        'checklistitems': check.id,
                        'question_no': question.question_no,
                        'result_colour': question.result_colour,
                        'domainchecklistquestion': question.checklistquestion,
                        'score': question.scores,
                    }
                    self.env['check.list.item'].create(checklist)

            # Manager assignment with safety checks
            if self.propertys and self.propertys.responsible_id:
                manager = self.env['hr.employee'].search([('id', '=', self.propertys.responsible_id.id)], limit=1)
                if manager:
                    self.manager_id = manager.id

            # Notification creation with safety checks
            if self.manager_id and self.manager_id.user_id:
                notification_create = self.env['notification.list'].create({
                    'name': f"Ticket {self.name_seq} is Created",
                    'read_status': 'un_read',
                    'date': date.today(),
                    'inspection_task': self.id,
                    'res_users': self.manager_id.user_id.id,
                    'res_partner_id': self.manager_id.user_id.partner_id.id,
                    'description': f"Ticket {self.name_seq} has Been Created Successfully !!!",
                    'manager': True if self.manager_id.user_id.type_users == 'manager' else False,
                    'user': True if self.manager_id.user_id.type_users == 'user' else False,
                    'tech': True if self.manager_id.user_id.type_users == 'tech' else False,
                })

        elif self.asset_type == "equipment":
            # self['name_seq'] = "IR0000" + str(self.id)
            self['task_type'] = 'task'

            for check in self.inspcheck_twolines:
                check.name_seq = 'ST0000' + str(check.id)
                check.state = 'incomplete'
                check.asset_types = 'equipment'

            # Get checklist questions for equipment
            checklist_questions = self.env['check.list'].search([
                ('equipment_id', '=', self.inspcheck_twolines[0].equipments.id)
            ]) if self.inspcheck_twolines else self.env['check.list']

            # Assign checklist questions to many2many field
            self.checklist_many = [(6, 0, checklist_questions.ids)]

            # Create additional inspection lines if needed
            existing_lines_count = len(self.inspcheck_twolines)
            needed_lines_count = len(self.checklist_many)
            
            if needed_lines_count > existing_lines_count and self.inspcheck_twolines:
                first_line = self.inspcheck_twolines[0]
                for rec in range(needed_lines_count - existing_lines_count):
                    self.inspcheck_twolines = [(0, 0, {
                        'asset_types': first_line.asset_types,
                        'building': first_line.building.id if first_line.building else False,
                        'room': first_line.room.id if first_line.room else False,
                        'equipments': first_line.equipments.id if first_line.equipments else False,
                        'floor': first_line.floor.id if first_line.floor else False,
                    })]

            # Assign checklist categories to inspection lines
            for check_record, inspection_line in zip(self.checklist_many, self.inspcheck_twolines):
                inspection_line.checkcateg = check_record.id

            # COMMENTED OUT THE PROBLEMATIC SECTION
            # TODO: Fix the data type conversion issue with 'ME01.06'
            """
            Original problematic code:
            
            for question_checklist in self.checklist_many:
                checks = []
                for rec in question_checklist.appointment_lines:
                    checklist = {
                        'names': rec.id,
                        'question_no_new': rec.question_no,
                        'score': rec.scores,
                        'domainchecklistquestion': rec.checklistquestion,
                        'result_colour': rec.result_colour,
                    }
                    checks.append((0, 0, checklist))

                for recs in self.inspcheck_twolines:
                    if recs.checkcateg and recs.checkcateg.id == question_checklist.id:
                        recs.categrylines = checks  # THIS LINE CAUSES THE ERROR
                        break
            """
            
            # Log that this section was skipped
            self.message_post(body="Checklist items creation skipped due to data type issue. Please fix manually.")

            # Manager assignment
            manager = self.env['hr.employee'].search([
                ('user_id.type_users', '=', 'manager')
            ], limit=1)
            
            if manager:
                self.manager_id = manager.id

            # Notification creation with safety checks
            if self.manager_id and self.manager_id.user_id:
                notification_create = self.env['notification.list'].create({
                    'name': f"Ticket {self.name_seq} is Created",
                    'read_status': 'un_read',
                    'date': date.today(),
                    'inspection_task': self.id,
                    'res_users': self.manager_id.user_id.id,
                    'res_partner_id': self.manager_id.user_id.partner_id.id,
                    'description': f"Ticket {self.name_seq} has Been Created Successfully !!!",
                    'manager': True if self.manager_id.user_id.type_users == 'manager' else False,
                    'user': True if self.manager_id.user_id.type_users == 'user' else False,
                    'tech': True if self.manager_id.user_id.type_users == 'tech' else False,
                })
            else:
                pass
   
        
    @api.onchange('assignto')
    def onchange_assignto_id(self):
        for rec in self:
            return {'domain': {'servicecate': [('inspectors', '=', rec.assignto.id)]}}

  
  
    @api.onchange('servicecate', 'asset_type')
    def onchange_servicecate(self):
        res = {}
        types = self.asset_type
        if self.servicecate:
            if (types == "property"):
                res['domain'] = {'checklistcate': [('servicetype', '=', self.servicecate.ids), ('inspectiontype', '=', 'property')]}
            else:
                res['domain'] = {'checklistcate': [('servicetype', '=', self.servicecate.ids), ('inspectiontype', '=', 'equipment')]}
        return res

    @api.model
    def create(self, vals):
        """Generate sequence number automatically when record is saved"""
        if vals.get('name_seq', 'New') == 'New' or not vals.get('name_seq'):
            vals['name_seq'] = "IR0000" + str(self.env['inspection.request'].search_count([]) + 1)
        
        result = super(inspectionrequest, self).create(vals)  # ✅ Correct class name
        return result
    
      
################################################################################################################################################
    def button_approve(self):
        """Approve the inspection request and generate questions"""
        for record in self:
            # ADD THIS LINE HERE - Generate sequence on approval:
            # if record.name_seq == 'New' or not record.name_seq:
            #     record.name_seq = "IR0000" + str(record.id)
            
            # First generate questions if checklist is selected
            if record.checklist_many:
                record._generate_questions_on_approve()
            
            # Then approve the record
            record.write({'state': 'approve'})
            
            # Log the approval
            record.message_post(body=f"Inspection request approved by {self.env.user.name}")
        
        return True

    def _generate_questions_on_approve(self):
        """Generate questions when approve button is clicked - SINGLE RECORD with equipment_id"""
        if not self.checklist_many:
            return
        
        
        if self.asset_type == "property":
            # Check if inspection line already exists
            existing_line = self.inspectioncheck_twolines.filtered(lambda x: x.state == 'incomplete')
            
            if not existing_line:
                # Create SINGLE inspection check line for property only if none exists
                inspection_line = self.env['inspection.check.twoline'].create({
                    'checktwoline_inspection': self.id,
                    'asset_types': 'property',
                    'checkcateg': self.checklist_many[0].id,
                    'building': self.building.id if self.building else False,
                    'floor': self.floor.id if self.floor else False,
                    'room': self.room.id if self.room else False,
                    'propertys': self.propertys.id if self.propertys else False,
                    'equipment_id': self.equipment_id.id if self.equipment_id else False,
                    'assignedto': self.assignto.id if self.assignto else False,
                    'state': 'incomplete',
                })
                
                # Set the name_seq for the inspection line
                inspection_line.name_seq = 'ST0000' + str(inspection_line.id)
            else:
                # Use existing line and update if needed
                inspection_line = existing_line[0]
                inspection_line.write({
                    'checkcateg': self.checklist_many[0].id,
                    'assignedto': self.assignto.id if self.assignto else False,
                    'asset_types': 'property',  # ✅ Ensure this is set
                    'propertys': self.propertys.id if self.propertys else False,  # ✅ Update property name
                })
            
            # Clear only the questions, not the inspection line
            inspection_line.categryline.unlink()
            
            # Create questions from ALL checklists under this inspection line
            for checklist in self.checklist_many:
                for question in checklist.appointment_lines:
                    # Handle question number conversion
                    question_no_value = 0
                    if question.question_no:
                        try:
                            if isinstance(question.question_no, str):
                                import re
                                numbers = re.findall(r'\d+', question.question_no)
                                question_no_value = int(numbers[0]) if numbers else 0
                            else:
                                question_no_value = int(question.question_no)
                        except (ValueError, TypeError):
                            question_no_value = 0
                    
                    # Create the question item linked to the inspection line
                    self.env['check.list.item'].create({
                        'names': question.id,
                        'checklistitems': inspection_line.id,
                        'question_no': question_no_value,
                        #'result_colour': question.result_colour if question.result_colour else 'yellow',
                        'domainchecklistquestion': question.checklistquestion,
                        #'score': question.scores if question.scores else 0,
                        'finding': question.valuess if question.valuess else 'yes',
                        #'result': question.finalresult if question.finalresult else 'pass',
                    })
        
        else:  # Equipment type - FIXED VERSION
            # Check if inspection line already exists
            existing_line = self.inspcheck_twolines.filtered(lambda x: x.state == 'incomplete')
            
            if not existing_line:
                # Create SINGLE inspection check line for equipment only if none exists
                inspection_line_vals = {
                    'checktwoline_insp': self.id,
                    'asset_types': 'equipment',
                    'checkcateg': self.checklist_many[0].id,
                    'state': 'incomplete',
                }
                
                # Add optional fields only if they exist
                if self.building:
                    inspection_line_vals['building'] = self.building.id
                if self.floor:
                    inspection_line_vals['floor'] = self.floor.id
                if self.room:
                    inspection_line_vals['room'] = self.room.id
                if self.propertys:
                    inspection_line_vals['propertys'] = self.propertys.id
                if self.equipment_id:
                    inspection_line_vals['equipments'] = self.equipment_id.id
                    inspection_line_vals['equipment_id'] = self.equipment_id.id
                if self.assignto:
                    inspection_line_vals['assignedto'] = self.assignto.id
                
                try:
                    inspection_line = self.env['inspectiontwo.check.twoline'].create(inspection_line_vals)
                    
                    # Set the name_seq for the inspection line
                    inspection_line.name_seq = 'ST0000' + str(inspection_line.id)
                    
                    _logger.info(f"Successfully created equipment inspection line: {inspection_line.name_seq}")
                    
                except Exception as e:
                    _logger.error(f"Error creating equipment inspection line: {str(e)}")
                    self.message_post(body=f"Error creating equipment sub-task: {str(e)}")
                    raise
            else:
                # Use existing line and update if needed
                inspection_line = existing_line[0]
                update_vals = {
                    'checkcateg': self.checklist_many[0].id,
                    'asset_types': 'equipment',  # ✅ FIXED: Ensure this is set to Equipment
                    'propertys': self.propertys.id if self.propertys else False,  # ✅ FIXED: Update Property Name
                }
                if self.assignto:
                    update_vals['assignedto'] = self.assignto.id
                
                inspection_line.write(update_vals)
            
            # Clear only the questions, not the inspection line
            inspection_line.categrylines.unlink()
            
            # Create questions from ALL checklists under this inspection line
            questions_created = 0
            for checklist in self.checklist_many:
                for question in checklist.appointment_lines:
                    # Handle question number conversion
                    question_no_value = 0
                    if question.question_no:
                        try:
                            if isinstance(question.question_no, str):
                                import re
                                numbers = re.findall(r'\d+', question.question_no)
                                question_no_value = int(numbers[0]) if numbers else 0
                            else:
                                question_no_value = int(question.question_no)
                        except (ValueError, TypeError):
                            question_no_value = 0
                    
                    # Create the question item for equipment
                    question_vals = {
                        'names': question.id,
                        'checklistitems': inspection_line.id,
                        'question_no_new': question_no_value,            
                        'domainchecklistquestion': question.checklistquestion,
                        'finding': question.valuess if question.valuess else 'yes',
                        'result_colour': None,                              
                       # 'findingvalue': None,
                        'score': 0,
                        'result': None,
                        
                    }
                    
                    self.env['equip.list.item'].create(question_vals)
                    questions_created += 1
            
            _logger.info(f"Created {questions_created} questions for equipment inspection")
            
            # Log success message
            self.message_post(
                body=f"Equipment sub-task {inspection_line.name_seq} updated with {questions_created} questions."
            )






# # Create the question item for equipment
#                     question_vals = {
#                         'names': question.id,
#                         'checklistitems': inspection_line.id,
#                         'question_no_new': question_no_value,
#                         #'result_colour': question.result_colour if question.result_colour else 'yellow',
#                         'domainchecklistquestion': question.checklistquestion,
#                        # 'score': question.scores if question.scores else 0,
#                         'finding': question.valuess if question.valuess else 'yes',
#                         #'result': question.finalresult if question.finalresult else 'pass',
#                     }

    
    
    
    
    

  
    
 #####################################################################################################################################################   
    def show_checklist(self, context=None):
        return {
            'name': "Sub Task",
            'domain': [('checktwoline_inspection', '=', self.id)],
            'view_mode': 'tree,form,pivot,graph',
            'res_model': 'inspection.check.twoline',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
        }
        
    def show_checklistequip(self, context=None):
        return {
            'name': "Sub Task",
            'domain': [('checktwoline_insp', '=', self.id)],
            'view_mode': 'tree,form,pivot,graph',
            'res_model': 'inspectiontwo.check.twoline',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
        }    

    @api.onchange('propertys')
    def onchange_propertys_id(self):
        for rec in self:
            return {'domain': {'building': [('propertyname', '=', rec.propertys.name)]}}
            
    @api.onchange('building')
    def onchange_building_id(self):
        for rec in self:
            return {'domain': {'floor': [('building_id', '=', rec.building.name)]}}

    @api.onchange('floor')
    def onchange_floor_id(self):
        for rec in self:
            return {'domain': {'room': [('floors', '=', rec.floor.name)]}}

    @api.onchange('room')
    def onchange_room_id(self):
        for rec in self:
            return {'domain': {'equipments': [('rooms', '=', rec.room.name)]}}    

    # asset_type = fields.Selection(string='Workmen Campus Facilities',
    #     selection=[('property', 'Equipment'), ('equipment', 'Property')], default="property")

   
    asset_type = fields.Selection(string='Workmen Campus Facilities',
        selection=[('property', 'Property'), ('equipment', 'Equipment')], default="property")


    inspection_plan_id = fields.Many2one('inspection.plan', string="Inspection plan")

    
    @api.model
    def _cron_generate_requests(self):
        for plan in self.env['inspection.plan'].search([('interval', '>', 0)]):
            plans = plan
            plans._create_new_request(plans)     

    request_date = fields.Date('Request Date', default=fields.Date.context_today,
                               help="Date requested for the maintenance to happen")

    state = fields.Selection([('draft', 'Assinged'), ('done', 'Submit'), ('cancel', 'Reschedule'), ('pending', 'Pending'), ('approve', 'Approved')],
                         required=False, default='draft', track_visibility='onchange', store=True)
    
    def button_done(self):
        for rec in self:
            rec.write({'state': 'done'})

    def button_done_new(self):
        notification_create_orm = self.env['notification.list'].create({
            'name': f"Ticket  {self.name_seq}  has Been Completed.",
            'read_status': 'un_read',
            'date': date.today(),
            'inspection_task': self.id,
            'res_users': self.created_by.id,
            'res_partner_id': self.created_by.partner_id.id,
            'description': f"Ticket {self.name_seq}  has Been Completed. !!!",
            'manager': True if self.created_by.type_users == 'manager' else False,
            'user': True if self.created_by.type_users == 'user' else False,
            'tech': True if self.created_by.type_users == 'tech' else False,
        })
        
        if self.asset_type == 'equipment':
            lines = self.env['inspectiontwo.check.twoline'].search([('checktwoline_insp', '=', self.id)])

            if lines.equipments.serviceprovider.user_id.id:
                notification_create_orm = self.env['notification.list'].create({
                    'name': f"Ticket  {self.name_seq}  has Been Completed.",
                    'read_status': 'un_read',
                    'date': date.today(),
                    'inspection_task': self.id,
                    'res_users': lines.equipments.serviceprovider.user_id.id,
                    'res_partner_id': lines.equipments.serviceprovider.id,
                    'description': f"Ticket {self.name_seq}  has Been Completed. !!!",
                    'manager': True if lines.equipments.serviceprovider.user_id.type_users == 'manager' else False,
                    'user': True if lines.equipments.serviceprovider.user_id.type_users == 'user' else False,
                    'tech': True if lines.equipments.serviceprovider.user_id.type_users == 'tech' else False,
                })
            else:
                pass

  




    def button_cancel(self):
        """Cancel/Reschedule the inspection request"""
        for record in self:
            record.write({'state': 'cancel'})
            # Log the cancellation
            record.message_post(body=f"Inspection request cancelled/rescheduled by {self.env.user.name}")
        return True


class inspectionrequestline(models.Model):
    _name = 'inspection.request.line'

    testline_inspection = fields.Many2one('inspection.request', string="Inspection")
    building = fields.Many2one('property.building', string="Building /Area")
    floor = fields.Many2one('property.floors', string="Floor Name")
    room = fields.Many2one('property.room', string="Room Name")


class inspectionrequesttwoline(models.Model):
    _name = 'inspection.request.twoline'

    testtwoline_inspection = fields.Many2one('inspection.request', string="Inspection")
    equipments = fields.Many2one('asset.asset', string="Equipment Name")
    checklist = fields.Many2one('check.list', string=" Check List Description ")
    pointweight = fields.Integer(string="Point Weightage ")    


class inspectionrchecktwoline(models.Model):
    _name = 'inspection.check.twoline'
    _rec_name = 'name_seq'
    _inherit = ['mail.thread', 'mail.activity.mixin']
  
    name_seq = fields.Char(string='ReqSub No', required=False, copy=False, readonly=True, index=True, default=lambda self:_('New'))
    checktwoline_inspection = fields.Many2one('inspection.request', string="Inspection Check")
    
    # asset_types = fields.Selection(string='Inspection Type',
    #     selection=[('property', 'Property'), ('equipment', 'Equipment')])

    # This now matches the main form
    asset_types = fields.Selection(string='Inspection Type',
        selection=[('property', 'Property'), ('equipment', 'Equipment')])


    checkcateg = fields.Many2one('check.list', string=" Check List Name")

    checklist = fields.Many2one('service.providertype', string=" Service Category",
                              related='checktwoline_inspection.servicecate')

    checklistitem = fields.Many2one('check.list.line', string="Check List Name")

    inspectionfinding = fields.Selection([('checkbox', 'Selection'), ('value', 'Value')],
                                      string="Question Type", related='checklistitem.checklistquestion')    

    inpectionresult = fields.Char(string="Inspection Result")    
    passcount = fields.Integer(string="Pass", track_visibility='onchange')    
    failcount = fields.Integer(string="Fail", track_visibility='onchange')    
    
    score = fields.Integer(string="Score", compute='_compute_score', track_visibility='onchange')    

    comments = fields.Char(string="Comments")    

    finalresult = fields.Selection([('pass', 'Pass'), ('fail', 'Fail')], string="Result")
    result_colour = fields.Selection([('red', 'NC'), ('yellow', 'OBS'), ('orange', 'AOA')], string='Result Colour', default='yellow')

    redcount = fields.Integer(string="NC", compute='_compute_redcount')    
    yellowcount = fields.Integer(string="OBS", compute='_compute_yellowcount')    
    orangecount = fields.Integer(string="AOA", compute='_compute_orangecount')         

    identity_card = fields.Many2many('ir.attachment', string="Attachment")
    
    checkitem = fields.One2many(related='checkcateg.appointment_lines', string='Check Category', readonly=False)
    categryline = fields.One2many('check.list.item', 'checklistitems', string=' Category')
    types = fields.Many2one('check.type.line', string='Sub Category')
    
    expertedresult = fields.Selection(related='checklistitem.finalresult', string='experted result',
        selection=[('pass', 'Pass'), ('fail', 'Fail')]) 
     
    state = fields.Selection([('incomplete', 'InComplete'), ('complete', 'Completed'), ('reschedule', 'Reschedule')], string="Status", default='incomplete')
    room = fields.Many2one('property.room', string="Room Name")    
    pointweight = fields.Integer(string="Point weightage ")

    subroom = fields.Many2one('property.room', string="Sub Room", domain=[('floor_type', '=', 'l')])

    assignedto = fields.Many2one('hr.employee', related='checktwoline_inspection.assignto', string='Assigned To')
    task_type = fields.Selection(related='checktwoline_inspection.task_type', string='Camp Facility Audit Type',
        selection=[('task', 'Task'), ('complaint', 'Instant Audit')]) 


    floor = fields.Many2one('property.floors', string="Floor Name")
    
    building = fields.Many2one('property.building', string="Building /Area")    
    propertys = fields.Many2one('property.land', string="Property Name")

    
    equipment_id = fields.Many2one('equipment.assets', string='Asset Name')
 
  #-------------------------------------------------------------------------

     # FIXED: Change from @api.model to @api.depends for automatic calculation
    passcount = fields.Integer(string="Pass", compute='_compute_passcount', store=True)    
    failcount = fields.Integer(string="Fail", compute='_compute_failcount', store=True)    
    redcount = fields.Integer(string="NC", compute='_compute_redcount', store=True)    
    yellowcount = fields.Integer(string="OBS", compute='_compute_yellowcount', store=True)    
    orangecount = fields.Integer(string="AOA", compute='_compute_orangecount', store=True)         

    @api.depends('categryline.result')
    def _compute_passcount(self):
        for rec in self:
            passcount = 0
            for line in rec.categryline:
                if line.result == "pass":
                    passcount += 1
            rec.passcount = passcount
                
    @api.depends('categryline.result')
    def _compute_failcount(self):
        for rec in self:
            failcount = 0
            for line in rec.categryline:
                if line.result == "fail":
                    failcount += 1
            rec.failcount = failcount

    @api.depends('categryline.result_colour')
    def _compute_yellowcount(self):
        for rec in self:
            count = 0
            for line in rec.categryline:
                if line.result_colour == "yellow":
                    count += 1
            rec.yellowcount = count

    @api.depends('categryline.result_colour')
    def _compute_orangecount(self):
        for rec in self:
            count = 0
            for line in rec.categryline:
                if line.result_colour == "orange":
                    count += 1
            rec.orangecount = count

    @api.depends('categryline.result_colour')
    def _compute_redcount(self):
        for rec in self:
            count = 0
            for line in rec.categryline:
                if line.result_colour == "red":
                    count += 1
            rec.redcount = count














  #-------------------------------------------------------------------------  


    @api.depends('categryline.score')
    def _compute_score(self):
        for record in self:
            record.score = sum(line.score for line in record.categryline)

    
    # @api.model
    # def _compute_yellowcount(self):
    #     for rec in self:
    #         passcount = 0
    #         for line in rec.categryline:
    #             if line.result_colour == "yellow":
    #                 passcount += 1
    #         rec.yellowcount = passcount

    # @api.model
    # def _compute_orangecount(self):
    #     for rec in self:
    #         passcount = 0
    #         for line in rec.categryline:
    #             if line.result_colour == "orange":
    #                 passcount += 1
    #         rec.orangecount = passcount

    # @api.model
    # def _compute_redcount(self):
    #     for rec in self:
    #         passcount = 0
    #         for line in rec.categryline:
    #             if line.result_colour == "red":
    #                 passcount += 1
    #         rec.redcount = passcount
 
   

    # @api.model
    # def _compute_passcount(self):
    #     for rec in self:
    #         passcount = 0
    #         for line in rec.categryline:
    #             if line.result == "pass":
    #                 passcount += 1
    #             else:
    #                 pass
    #         rec.passcount = passcount
                
    # @api.model
    # def _compute_failcount(self):
    #     for rec in self:
    #         failcount = 0
    #         for line in rec.categryline:
    #             if line.result == "fail":
    #                 failcount += 1
    #         rec.failcount = failcount
   
    def action_send_mail(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('inspectionrchecktwoline', 'email_Update')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'inspection.check.twoline',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_body': 'Inspection Fail',
            'default_composition_mode': 'comment',
        }
        return {
            'name': _('Send Email'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(template_id, 'form')],
            'view_id': template_id,
            'target': 'new',
            'context': ctx,
        }

    @api.onchange('propertys')
    def onchange_propertys_id(self):
        for rec in self:
            return {'domain': {'building': [('propertyname', '=', rec.propertys.id)]}}
        
    
    
    @api.onchange('building')
    def onchange_building_id(self):
        for rec in self:
            return {'domain': {'floor': [('building_id', '=', rec.building.id)]}}
    
    @api.onchange('floor')
    def onchange_floor_id(self):
        for rec in self:
            return {'domain': {'room': [('floors', '=', rec.floor.id), ('floor_type', '=', 'c')]}}    
        
    @api.onchange('room')
    def onchange_room_id(self):
        for rec in self:
            return {'domain': {'subroom': [('roomspar', '=', rec.room.id)]}}

  
     
class InspectionTwoCheckLine(models.Model):
    _name = 'inspectiontwo.check.twoline'
    _rec_name = 'name_seq'
    _inherit = ['mail.thread', 'mail.activity.mixin'] 
    _order = 'id desc' 
    
    overall_count = fields.Integer('Over All Count')
    checktwoline_insp = fields.Many2one('inspection.request', string="Inspection Check for Equipment")

    name_seq = fields.Char(string='ReqSub No', required=False, copy=False, readonly=True, index=True, default=lambda self:_('New'))

    checklistitem = fields.Many2one('check.list.line', string="Check List Item")

    inspectionfinding = fields.Selection([('checkbox', 'Selection'), ('value', 'Value')], string="Question Type",
                                      related='checklistitem.checklistquestion')    

    inpectionresult = fields.Char(string="Inspection Result")    

    finalresult = fields.Selection([('pass', 'Pass'), ('fail', 'Fail')], string="Result", track_visibility='onchange')
    result_colour = fields.Selection([('red', 'NC'), ('yellow', 'OBS'), ('orange', 'AOA')], string='Result Colour', default='yellow')            
    propertys = fields.Many2one('property.land', string="Property Name")    
    comments = fields.Char(string="Comments")    
    types = fields.Many2one('check.type.line', string='Sub Category')
    identity_card = fields.Many2many('ir.attachment', string="Attachment")
    equipment_category_id = fields.Many2one('equipment.category', string='Equipment Category')
    
    checkitemequip = fields.One2many(related='checkcateg.appointment_lines', string='Check Category', readonly=False)
    checklist = fields.Many2one('service.providertype', string=" Service Category",
                             related='checktwoline_insp.servicecate')
    
    checkcateg = fields.Many2one('check.list', string=" Check List Name")
 
    categrylines = fields.One2many('equip.list.item', 'checklistitems', string=' Category')    
    score = fields.Integer(string="Score", compute='_compute_score')    
    # ADD THIS NEW FIELD:
    equipment_id = fields.Many2one('equipment.assets', string='Asset Name')
#--------------------------------------------------------------------------

    # FIXED: Change from @api.model to @api.depends for automatic calculation
    passcount = fields.Integer(string="Pass", compute='_compute_passcount', store=True)    
    failcount = fields.Integer(string="Fail", compute='_compute_failcount', store=True)    
    yellowcount = fields.Integer(string="OBS", compute='_compute_yellowcount', store=True)    
    orangecount = fields.Integer(string="AOA", compute='_compute_orangecount', store=True)
    redcount = fields.Integer(string="NC", compute='_compute_redcount', store=True)
    greencount = fields.Integer(string="Compiled", compute='_compute_greencount', store=True)
    
    @api.depends('categrylines.result')
    def _compute_passcount(self):
        for rec in self:
            passcount = 0
            for line in rec.categrylines:
                if line.result == "pass":
                    passcount += 1
            rec.passcount = passcount
  
    @api.depends('categrylines.result')
    def _compute_failcount(self):
        for rec in self:
            failcount = 0
            for line in rec.categrylines:
                if line.result == "fail":
                    failcount += 1
            rec.failcount = failcount

    @api.depends('categrylines.result_colour')
    def _compute_greencount(self):
        for rec in self:
            count = 0
            for line in rec.categrylines:
                if line.result_colour == "green":
                    count += 1
            rec.greencount = count
            
    @api.depends('categrylines.result_colour')
    def _compute_yellowcount(self):
        for rec in self:
            count = 0
            for line in rec.categrylines:
                if line.result_colour == "yellow":
                    count += 1
            rec.yellowcount = count

    @api.depends('categrylines.result_colour')
    def _compute_orangecount(self):
        for rec in self:
            count = 0
            for line in rec.categrylines:
                if line.result_colour == "orange":
                    count += 1
            rec.orangecount = count

    @api.depends('categrylines.result_colour')
    def _compute_redcount(self):
        for rec in self:
            count = 0
            for line in rec.categrylines:
                if line.result_colour == "red":
                    count += 1
            rec.redcount = count   
    





#---------------------------------------------------------------------------
    @api.depends('categrylines.score')
    def _compute_score(self):
        for record in self:
            record.score = sum(line.score for line in record.categrylines)

    @api.onchange('propertys')
    def onchange_propertys_id(self):
        for rec in self:
            return {'domain': {'building': [('propertyname', '=', rec.propertys.id)]}}    
            
    @api.onchange('building')
    def onchange_building_id(self):
        for rec in self:
            return {'domain': {'floor': [('building_id', '=', rec.building.id)]}}

    @api.onchange('floor')
    def onchange_floor_id(self):
        for rec in self:
            return {'domain': {'room': [('floors', '=', rec.floor.id), ('floor_type', '=', 'c')]}}        

   

    @api.model
    def create(self, vals):
        """Generate sequence number for sub-task"""
        if vals.get('name_seq', 'New') == 'New' or not vals.get('name_seq'):
            last_record = self.search([], order='id desc', limit=1)
            if last_record:
                vals['name_seq'] = "ST0000" + str(last_record.id + 1)
            else:
                vals['name_seq'] = "ST0000001"
        
        result = super(InspectionTwoCheckLine, self).create(vals)  # ✅ Correct class name
        return result


    # passcount = fields.Integer(string="Pass", compute='_compute_passcount', track_visibility='onchange')    
    # failcount = fields.Integer(string="Fail", compute='_compute_failcount', track_visibility='onchange')    
    # yellowcount = fields.Integer(string="OBS", compute='_compute_yellowcount')    
    # orangecount = fields.Integer(string="AOA", compute='_compute_orangecount')
    # redcount = fields.Integer(string="NC", compute='_compute_redcount')
    # greencount = fields.Integer(string="Compiled", compute='_compute_greencount')
    
    # @api.model
    # def _compute_greencount(self):
    #     for rec in self:
    #         passcount = 0
    #         for line in rec.categrylines:
    #             if line.result_colour == "green":
    #                 passcount += 1
    #         rec.greencount = passcount
            
    # @api.model
    # def _compute_yellowcount(self):
    #     for rec in self:
    #         passcount = 0
    #         for line in rec.categrylines:
    #             if line.result_colour == "yellow":
    #                 passcount += 1
    #         rec.yellowcount = passcount

    # @api.model
    # def _compute_orangecount(self):
    #     for rec in self:
    #         passcount = 0
    #         for line in rec.categrylines:
    #             if line.result_colour == "orange":
    #                 passcount += 1
    #         rec.orangecount = passcount

    # @api.model
    # def _compute_redcount(self):
    #     for rec in self:
    #         passcount = 0
    #         for line in rec.categrylines:
    #             if line.result_colour == "red":
    #                 passcount += 1
    #         rec.redcount = passcount

    # @api.depends('passcount')
    # def _compute_passcount(self):
    #     for rec in self:
    #         passcount = 0
    #         for line in rec.categrylines:
    #             if line.result == "pass":
    #                 passcount += 1
    #         rec.passcount = passcount
  
    # @api.model
    # def _compute_failcount(self):
    #     for rec in self:
    #         failcount = 0
    #         for line in rec.categrylines:
    #             if line.result == "fail":
    #                 failcount += 1
    #         rec.failcount = failcount

    subroom = fields.Many2one('property.room', string="Sub Room", domain=[('floor_type', '=', 'l')])

    pointweight = fields.Integer(string="Point weightage ")

    building = fields.Many2one('property.building', string="Building /Area")
    floor = fields.Many2one('property.floors', string="Floor Name")
    equipments = fields.Many2one('equipment.assets', string="Asset Name")    
    assignedto = fields.Many2one('hr.employee', related='checktwoline_insp.assignto', string='Assigned To')
    room = fields.Many2one('property.room', string="Room Name")    
    pointweight = fields.Integer(string="Point weightage ")
    
    state = fields.Selection([('incomplete', 'InComplete'), ('complete', 'Completed'), ('reschedule', 'Reschedule')], default='incomplete', string="Status")

    asset_types = fields.Selection(string='Workmen Campus Facilities', selection=[('property', 'Property'), ('equipment', 'Equipment')])

    task_type = fields.Selection(related='checktwoline_insp.task_type', string='Camp Facility Audit Type',
        selection=[('task', 'Task'), ('complaint', 'Instant Audit')]) 
    expertedresult = fields.Selection(related='checklistitem.finalresult', string='experted result',
        selection=[('pass', 'Pass'), ('fail', 'Fail')]) 
 
    @api.onchange('room')
    def onchange_room_id(self):
        for rec in self:
            return {'domain': {
                'equipments': [('rooms', '=', rec.room.id)],
                'subroom': [('roomspar', '=', rec.room.id)]
            }}        
   
    @api.onchange('subroom')
    def onchange_subroom_id(self):
        for rec in self:
            return {'domain': {'equipments': [('subarea', '=', rec.subroom.id)]}} 

    def action_send_mail(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('rtwochecktwoline' , 'emailequip_Update')[1]
           # template_id = ir_model_data.get_object_reference('rtwochecktwoline' 'inspectionrchecktwoline', 'emailequip_Update')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'inspectiontwo.check.twoline',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_body': 'Inspection Fail',
            'default_composition_mode': 'comment',
        }
        return {
            'name': _('Send Email'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(template_id, 'form')],
            'view_id': template_id,
            'target': 'new',
            'context': ctx,
        }


class EquipListItem(models.Model):
    _name = 'equip.list.item'
    _rec_name = 'names'

    checklistitems = fields.Many2one('inspectiontwo.check.twoline', string="Check List Result")
    names = fields.Many2one('check.list.line', string="Questions", readonly=False)
    finding = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="(Yes or NO) Value")
    comments = fields.Char(string="Comments")
    identity_card = fields.Many2many('ir.attachment', string="Attachment")
    score = fields.Integer(string="Score")
    relfinding = fields.Selection([('yes', 'Yes'), ('no', 'No')], related='names.valuess', string="Related Finding")
    findingvalue = fields.Char(string="Feed value") 
    question_no_new = fields.Integer('No')
    # Result and colors
    result = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail'),
        ('compiled', 'Compiled'),
        ('obs', 'OBS'),
        ('aoa', 'AOA')
    ], string="Result")

    result_colour = fields.Selection([
        ('green', 'Compiled'),
        ('red', 'NC'),
        ('yellow', 'OBS'),
        ('orange', 'AOA')
    ], string='Result Colour', default='yellow')     

    domainchecklistquestion = fields.Selection([('checkbox', 'Selection'), ('value', 'Value')],
                                               string="Question Type") 

    requestdomain = fields.Many2one('inspection.request',
                                    related='checklistitems.checktwoline_insp',
                                    string="request domain")  

    domaintype = fields.Selection(related='checklistitems.asset_types', string='domaintype',
                                  selection=[('property', 'Property'), ('equipment', 'Equipment')]) 

    domainscore = fields.Integer(related='names.scores', string='domainscore')         
    domainbetween = fields.Integer(related='names.valueofnumberto', string='domainbetween')    
    domainvalue = fields.Integer(related='names.conditionvalue', string='domainvalue')  
    domaincondition = fields.Selection([('Equal_To', 'Equal to'), ('Not_Equal', 'Not Equal to'),
                                       ('Greather_than', 'Greater Than'), ('Less_than', 'Less Than'),
                                       ('Inbetween', 'In Between')],
                                      related='names.conditions', string='domaincondition') 

    domainguidline = fields.Text(related='names.guidelines', string='domainguidline')
    question_no = fields.Integer('NO') 

    @api.onchange('findingvalue')
    def onchange_findingvalue(self):
        for rec in self:
            rec.result = False
            rec.result_colour = False
            rec.score = 0

            if not rec.findingvalue:
                continue

            try:
                value = float(rec.findingvalue)
            except ValueError:
                continue

            # Thresholds
            threshold_pass = 85       # Compiled/Green
            threshold_compiled = 70   # Green (partial score)
            threshold_obs = 60        # Yellow
            threshold_aoa = 50        # Orange
            max_score = rec.names.scores or 10

            # Determine result, color, and score
            if value >= threshold_pass:
                rec.result = 'pass'
                rec.result_colour = 'green'
                rec.score = max_score
            elif value >= threshold_compiled:
                rec.result = 'pass'
                rec.result_colour = 'green'
                rec.score = int(max_score * 0.85)
            elif value >= threshold_obs:
                rec.result = 'pass'
                rec.result_colour = 'yellow'
                rec.score = int(max_score * 0.7)
            elif value >= threshold_aoa:
                rec.result = 'pass'
                rec.result_colour = 'orange'
                rec.score = int(max_score * 0.6)
            else:
                rec.result = 'fail'
                rec.result_colour = 'red'
                rec.score = 0



# class equiplistitem(models.Model):
#     _name = 'equip.list.item'
#     _rec_name = 'names'
    
#     dummy = fields.Boolean('Dummy', compute='_compute_result', store=True)
#     findingvalue_1 = fields.Float(string="Feed value", invisible=True)

   

#     checklistitems = fields.Many2one('inspectiontwo.check.twoline', string="Check List Result")
#     names = fields.Many2one('check.list.line', string="Questions", readonly=False)
#     finding = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="(Yes or NO) Value")   
#     question_no = fields.Char('No') 
#     question_no_new = fields.Integer('No')
#     comments = fields.Char(string="Comments")    
#     identity_card = fields.Many2many('ir.attachment', string="Attachment")     
#     score = fields.Integer(string="Score")     
#     relfinding = fields.Selection([('yes', 'Yes'), ('no', 'No')], related='names.valuess', string="Related Finding")
#     findingvalue = fields.Char(string="Feed value")
#     requestdomain = fields.Many2one('inspection.request',
#         related='checklistitems.checktwoline_insp',
#         string="request domain")
 
#     domainchecklistquestion = fields.Selection([('checkbox', 'Selection'), ('value', 'Value')],
#         string="Question Type")  
         
#     domainproperty = fields.Many2one('property.land',
#         related='checklistitems.propertys', string="domainproperty") 

#     domainbuilding = fields.Many2one('property.building',
#         related='checklistitems.building', string="domainbuilding")

#     domainfloor = fields.Many2one('property.floors',
#         related='checklistitems.floor', string="domainfloor")

#     domainroom = fields.Many2one('property.room',
#         related='checklistitems.room', string="domainroom")
 
#     domainsubroom = fields.Many2one('property.room',
#         related='checklistitems.subroom', string="domainsubroom")

#     domaincheck = fields.Many2one('check.list',
#         related='checklistitems.checkcateg', string="domaincheck")
 
#     domaintype = fields.Selection(related='checklistitems.asset_types', string='domaintype ',
#         selection=[('property', 'Property'), ('equipment', 'Equipment')])   
 
#     domainscore = fields.Integer(related='names.scores', string='domainscore ')
  
#     status = fields.Selection([('pass', 'Pass'), ('fail', 'Fail')], related='names.finalresult', string="Status")
#     result = fields.Selection([('pass', 'Pass'), ('fail', 'Fail')], string="Result") 
#     result_colour = fields.Selection([('green', 'Compiled'), ('red', 'NC'), ('yellow', 'OBS'), ('orange', 'AOA')], string='Result Colour')
#     domainbetween = fields.Integer(related='names.valueofnumberto', string='domainbetween ')      
#     domainvalue = fields.Integer(related='names.conditionvalue', string='domainvalue ')    
      
#     domaincondition = fields.Selection([('Equal_To', 'Equal to'), ('Not_Equal', 'Not Equal to'),
#       ('Greather_than', 'Greater Than'), ('Less_than', 'Less Than'), ('Inbetween', 'In Between')],
#       related='names.conditions',
#        string='domaincondition ')  
#     domainguidline = fields.Text(related='names.guidelines', string='domainguidline ')

 
    
    

        




class checklistitem(models.Model):
    _name = 'check.list.item'
    _rec_name = 'names'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    checklistitems = fields.Many2one('inspection.check.twoline', string="Check List Result")
    names = fields.Many2one('check.list.line', string="Questions", readonly=False)
    finding = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="(Yes or NO) Value")
    status = fields.Selection([('pass', 'Pass'), ('fail', 'Fail')], related='names.finalresult', string="Status")        
    comments = fields.Char(string="Comments")
    identity_card = fields.Many2many('ir.attachment', string="Attachment")
    score = fields.Integer(string="Score")
    relfinding = fields.Selection([('yes', 'Yes'), ('no', 'No')], related='names.valuess', string="Related Finding") 
    findingvalue = fields.Char(string="Feed value") 

    # Updated result field to allow all possible values
    result = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail'),
        ('compiled', 'Compiled'),
        ('obs', 'OBS'),
        ('aoa', 'AOA')
    ], string="Result")

    result_colour = fields.Selection([
        ('green', 'Compiled'),
        ('red', 'NC'),
        ('yellow', 'OBS'),
        ('orange', 'AOA')
    ], string='Result Colour', default='yellow')     

    domainchecklistquestion = fields.Selection([('checkbox', 'Selection'), ('value', 'Value')],
                                               string="Question Type") 
  
    requestdomain = fields.Many2one('inspection.request',
                                    related='checklistitems.checktwoline_inspection',
                                    string="request domain")  

    domainproperty = fields.Many2one('property.land',
                                     related='checklistitems.propertys', string="domainproperty")
  
    domainbuilding = fields.Many2one('property.building',
                                     related='checklistitems.building', string="domainbuilding")

    domainfloor = fields.Many2one('property.floors',
                                  related='checklistitems.floor', string="domainfloor")

    domainroom = fields.Many2one('property.room',
                                 related='checklistitems.room', string="domainroom")
 
    domainsubroom = fields.Many2one('property.room',
                                    related='checklistitems.subroom', string="domainsubroom")

    domaintype = fields.Selection(related='checklistitems.asset_types', string='domaintype',
                                  selection=[('property', 'Property'), ('equipment', 'Equipment')]) 

    domaincheck = fields.Many2one('check.list',
                                  related='checklistitems.checkcateg', string="domaincheck")
 
    domainscore = fields.Integer(related='names.scores', string='domainscore')         

    domainbetween = fields.Integer(related='names.valueofnumberto', string='domainbetween')    

    domainvalue = fields.Integer(related='names.conditionvalue', string='domainvalue')  
 
    domaincondition = fields.Selection([('Equal_To', 'Equal to'), ('Not_Equal', 'Not Equal to'),
                                        ('Greather_than', 'Greater Than'), ('Less_than', 'Less Than'),
                                        ('Inbetween', 'In Between')],
                                       related='names.conditions', string='domaincondition') 

    domainguidline = fields.Text(related='names.guidelines', string='domainguidline')
    question_no = fields.Integer('NO') 

    @api.onchange('findingvalue')
    def onchange_findingvalue(self):
        for rec in self:
            rec.result = False
            rec.result_colour = False
            rec.score = 0

            if not rec.findingvalue:
                continue

            try:
                value = float(rec.findingvalue)
            except ValueError:
                continue

            # Thresholds - adjust as needed or make dynamic from `names` model
            threshold_pass = 85
            threshold_compiled = 70
            threshold_obs = 60
            threshold_aoa = 50
            max_score = rec.names.scores or 10

            # Determine result, color, and score
            if value >= threshold_pass:
                rec.result = 'pass'
                rec.result_colour = 'green'
                rec.score = max_score
            elif value >= threshold_compiled:
                rec.result = 'pass'
                rec.result_colour = 'green'
                rec.score = int(max_score * 0.85)
            elif value >= threshold_obs:
                rec.result = 'pass'
                rec.result_colour = 'yellow'
                rec.score = int(max_score * 0.7)
            elif value >= threshold_aoa:
                rec.result = 'pass'
                rec.result_colour = 'orange'
                rec.score = int(max_score * 0.6)
            else:
                rec.result = 'fail'
                rec.result_colour = 'red'
                rec.score = 0







# class checklistitem(models.Model):
#     _name = 'check.list.item'
#     _rec_name = 'names'
#     _inherit = ['mail.thread', 'mail.activity.mixin']
    
#     checklistitems = fields.Many2one('inspection.check.twoline', string="Check List Result")
#     names = fields.Many2one('check.list.line', string=" Questions", readonly=False)
#     finding = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="(Yes or NO) Value")
#     status = fields.Selection([('pass', 'Pass'), ('fail', 'Fail')], related='names.finalresult', string="Status")        
#     comments = fields.Char(string="Comments")
#     identity_card = fields.Many2many('ir.attachment', string="Attachment")
#     score = fields.Integer(string="Score")
#     relfinding = fields.Selection([('yes', 'Yes'), ('no', 'No')], related='names.valuess', string="Related Finding") 
#     findingvalue = fields.Char(string="Feed value") 
#     result = fields.Selection([('pass', 'Pass'), ('fail', 'Fail')], string="Result")
#     result_colour = fields.Selection([ ('green', 'Compiled'), ('red', 'NC'), ('yellow', 'OBS'), ('orange', 'AOA')], string='Result Colour', default='yellow')     
#     domainchecklistquestion = fields.Selection([('checkbox', 'Selection'), ('value', 'Value')],
#         string="Question Type") 
  
#     requestdomain = fields.Many2one('inspection.request',
#                                  related='checklistitems.checktwoline_inspection',
#                                  string="request domain")  

#     domainproperty = fields.Many2one('property.land',
#         related='checklistitems.propertys', string="domainproperty")
  
#     domainbuilding = fields.Many2one('property.building',
#         related='checklistitems.building', string="domainbuilding")

#     domainfloor = fields.Many2one('property.floors',
#         related='checklistitems.floor', string="domainfloor")

#     domainroom = fields.Many2one('property.room',
#         related='checklistitems.room', string="domainroom")
 
#     domainsubroom = fields.Many2one('property.room',
#         related='checklistitems.subroom', string="domainsubroom")

#     domaintype = fields.Selection(related='checklistitems.asset_types', string='domaintype ',
#         selection=[('property', 'Property'), ('equipment', 'Equipment')]) 

#     domaincheck = fields.Many2one('check.list',
#         related='checklistitems.checkcateg', string="domaincheck")
 
#     domainscore = fields.Integer(related='names.scores', string='domainscore ')         

#     domainbetween = fields.Integer(related='names.valueofnumberto', string='domainbetween ')    

#     domainvalue = fields.Integer(related='names.conditionvalue', string='domainvalue ')  
 
#     domaincondition = fields.Selection([('Equal_To', 'Equal to'), ('Not_Equal', 'Not Equal to'),
#       ('Greather_than', 'Greater Than'), ('Less_than', 'Less Than'), ('Inbetween', 'In Between')],
#       related='names.conditions',
#        string='domaincondition ') 
#     domainguidline = fields.Text(related='names.guidelines', string='domainguidline ')
#     question_no = fields.Integer('NO') 



    # @api.onchange('findingvalue')
    # def onchange_findingvalue(self):
    #     for rec in self:
    #         # Reset all
    #         rec.result = False
    #         rec.result_colour = False
    #         rec.score = 0

    #         if not rec.findingvalue or not rec.names:
    #             continue

    #         try:
    #             value = float(rec.findingvalue)
    #         except:
    #             continue

    #         # Thresholds
    #         dangerous_if = rec.names.dangerous_if  # 'higher' or 'lower'
    #         threshold_pass = rec.names.conditionvalue or 100

    #         # Optional: set OBS / AOA thresholds manually if model doesn't have them
    #         threshold_compiled = threshold_pass * 0.85
    #         threshold_obs = threshold_pass * 0.70
    #         threshold_aoa = threshold_pass * 0.60

    #         score_max = rec.names.scores or 10

    #         # Logic for higher dangerous
    #         if dangerous_if == 'higher':
    #             if value >= threshold_pass:
    #                 rec.result = 'pass'
    #                 rec.result_colour = 'green'
    #                 rec.score = score_max
    #             elif value >= threshold_compiled:
    #                 rec.result = 'fail'
    #                 rec.result_colour = 'green'  # Compiled
    #                 rec.score = int(score_max * 0.85)
    #             elif value >= threshold_obs:
    #                 rec.result = 'fail'
    #                 rec.result_colour = 'yellow'  # OBS
    #                 rec.score = int(score_max * 0.70)
    #             elif value >= threshold_aoa:
    #                 rec.result = 'fail'
    #                 rec.result_colour = 'orange'  # AOA
    #                 rec.score = int(score_max * 0.60)
    #             else:
    #                 rec.result = 'fail'
    #                 rec.result_colour = 'red'
    #                 rec.score = 0

    #         # Logic for lower dangerous
    #         elif dangerous_if == 'lower':
    #             if value <= threshold_pass:
    #                 rec.result = 'pass'
    #                 rec.result_colour = 'green'
    #                 rec.score = score_max
    #             elif value <= threshold_compiled:
    #                 rec.result = 'fail'
    #                 rec.result_colour = 'green'
    #                 rec.score = int(score_max * 0.85)
    #             elif value <= threshold_obs:
    #                 rec.result = 'fail'
    #                 rec.result_colour = 'yellow'
    #                 rec.score = int(score_max * 0.70)
    #             elif value <= threshold_aoa:
    #                 rec.result = 'fail'
    #                 rec.result_colour = 'orange'
    #                 rec.score = int(score_max * 0.60)
    #             else:
    #                 rec.result = 'fail'
    #                 rec.result_colour = 'red'
    #                 rec.score = 0




 
    # @api.onchange('finding', 'findingvalue', 'result')
    # def onchange_finding(self):
    #     if ((self.names.checklistquestion == "checkbox")):
    #         if (self.finding == self.relfinding):
    #             self.score = self.names.scores
    #             self.result = self.names.finalresult
    #         else:
    #             self.score = 0
    #             self.result = 'fail'
    
    #     elif ((self.names.checklistquestion == "value")):
    #         if (self.names.conditions == "Equal_To"):
    #             if (self.findingvalue == self.names.conditionvalue):
    #                 self.score = self.names.scores
    #                 self.result = self.names.finalresult
    #             else:
    #                 self.score = 0
    #                 self.result = 'fail'
    #         elif (self.names.conditions == "Not_Equal"):
    #             if (int(self.findingvalue) != int(self.names.conditionvalue)):
    #                 self.score = self.names.scores
    #                 self.result = self.names.finalresult
    #             else:
    #                 self.score = 0
    #                 self.result = 'fail'
    #         elif (self.names.conditions == "Greather_than"):
    #             if (int(self.findingvalue) >= int(self.names.conditionvalue)):
    #                 self.score = self.names.scores
    #                 self.result = self.names.finalresult
    #             else:
    #                 self.score = 0
    #                 self.result = 'fail'
    #         elif (self.names.conditions == "Less_than"):
    #             if (int(self.findingvalue) <= int(self.names.conditionvalue)):
    #                 self.score = self.names.scores
    #                 self.result = self.names.finalresult
    #             else:
    #                 self.score = 0
    #                 self.result = 'fail'
    #         elif (self.names.conditions == "Inbetween"):
    #             if (int(self.names.conditionvalue) <= int(self.findingvalue) <= int(self.names.valueofnumberto)):
    #                 self.score = self.names.scores
    #                 self.result = self.names.finalresult
    #             else:
    #                 self.score = 0
    #                 self.result = 'fail'






