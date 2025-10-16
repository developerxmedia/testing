# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from odoo.exceptions import ValidationError
from datetime import date
import re
import passlib
from dateutil.relativedelta import relativedelta
from datetime import datetime, date, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError
# from odoo import babel
import pytz



def get_relativedelta(interval, step):
    if step == 'day':
        return relativedelta(days=interval)
    elif step == 'week':
        return relativedelta(weeks=interval)
    elif step == 'month':
        return relativedelta(months=interval)
    elif step == 'year':
        return relativedelta(years=interval)


class inspectionPlan(models.Model):
    _name = 'inspection.plan'
    _description = 'inspection Plan'

    name = fields.Char('Name', oldname='description', required=True)

    name_seq = fields.Char(
        string='Plan No',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: _('New')
    ) 

    def inspection_plan_cron(self):
        orm_search = self.search([])
        l = []
        for rec in orm_search:
            if rec.next_inspection_date:
                
                if rec.next_inspection_date == date.today():
                    questions = self.env['check.list'].search([('id', '=', rec.checklistcat.id)])   
                    
                    if rec.asset_type == 'property':
                        inspection_task_create = self.env['inspection.request'].create({
                            'asset_type': rec.asset_type,
                            'task_type': 'task',
                            'cron_task': True,
                            'servicecate': rec.servicecate.id,
                            'checklistcate': rec.checklistcat.id,
                            'created_by': rec.created_by.id,
                            'names': rec.name,
                            'manager_id': rec.assignto.id,
                            'propertys': rec.propertys.id
                        })
                        inspection_task_create['name_seq'] = "IR0000" + str(inspection_task_create.id)
                        
                        line_id = self.env['inspection.check.twoline'].create({
                             'checktwoline_inspection': inspection_task_create.id,
                             'building': rec.building.id,
                             'floor': rec.floor.id,
                             'room': rec.room.id,
                        })
                        line_id['name_seq'] = 'ST0000' + str(line_id.id)
                        
                        for question in questions.appointment_lines:
                            checklist = {
                                'names': question.id,
                                'checklistitems': line_id.id,
                                'question_no': question.question_no,
                                'domainchecklistquestion': "checkbox",
                                'score': question.scores,
                                'finding': 'yes'
                            }
                            self.env['check.list.item'].create(checklist)
                            
                        manager = self.env['hr.employee'].search([('id', '=', self.propertys.responsible_id.id)])
                        inspection_task_create.manager_id = manager.id 
                        
                        notification_create = self.env['notification.list'].create({
                            'name': f"Ticket {self.name_seq} is Created",
                            'read_status': 'un_read',
                            'date': date.today(),
                            'inspection_task': self.id,
                            'res_users': inspection_task_create.manager_id.user_id.id,
                            'res_partner_id': inspection_task_create.manager_id.user_id.partner_id.id,
                            'description': f"Ticket {inspection_task_create.name_seq} has Been Created Successfully !!!",
                            'manager': True if inspection_task_create.manager_id.user_id.type_users == 'manager' else False,
                            'user': True if inspection_task_create.manager_id.user_id.type_users == 'user' else False,
                            'tech': True if inspection_task_create.manager_id.user_id.type_users == 'tech' else False,
                        })

                        interval_timedelta = get_relativedelta(rec.interval, rec.interval_step)
                        rec.next_inspection_date = rec.next_inspection_date + interval_timedelta
                        
                    else:
                        inspection_task_create = self.env['inspection.request'].create({
                            'asset_type': rec.asset_type,
                            'cron_task': True,
                            'task_type': 'task',
                            'servicecate': rec.servicecate.id,
                            'checklistcate': rec.checklistcat.id,
                            'created_by': rec.created_by.id,
                            'names': rec.name,
                            'manager_id': rec.assignto.id,
                        })
                        inspection_task_create['name_seq'] = "IR0000" + str(inspection_task_create.id)
                        
                        line_id = self.env['inspectiontwo.check.twoline'].create({
                             'checktwoline_insp': inspection_task_create.id,
                             'building': rec.building.id,
                             'floor': rec.floor.id,
                             'room': rec.room.id,
                             'equipments': rec.equipment_id.id,
                             'equipment_category_id': rec.checklistcat.equipment_category_id.id
                        })
                        line_id['name_seq'] = 'ST0000' + str(line_id.id)
                        
                        for question in rec.checklistcat.appointment_lines:
                            checklist = {
                                'names': question.id,
                                'checklistitems': line_id.id,
                                'question_no_new': question.question_no,
                                'domainchecklistquestion': "checkbox",
                                'score': question.scores,
                                'finding': 'yes'
                            }
                            var = self.env['equip.list.item'].create(checklist)
                            
                        inspection_task_create.manager_id = rec.assignto.id 
                        
                        notification_create = self.env['notification.list'].create({
                            'name': f"Ticket {inspection_task_create.name_seq} is Created",
                            'read_status': 'un_read',
                            'date': date.today(),
                            'inspection_task': inspection_task_create.id,
                            'res_users': inspection_task_create.manager_id.user_id.id,
                            'res_partner_id': inspection_task_create.manager_id.user_id.partner_id.id,
                            'description': f"Ticket {inspection_task_create.name_seq} has Been Created Successfully !!!",
                            'manager': True if inspection_task_create.manager_id.user_id.type_users == 'manager' else False,
                            'user': True if inspection_task_create.manager_id.user_id.type_users == 'user' else False,
                            'tech': True if inspection_task_create.manager_id.user_id.type_users == 'tech' else False,
                        })
                        
                        interval_timedelta = get_relativedelta(rec.interval, rec.interval_step)
                        rec.next_inspection_date = rec.next_inspection_date + interval_timedelta
                else:
                    pass
            else:
                pass
    
    checklistcat = fields.Many2one('check.list', string="Checklist Name", required=True)
    
    @api.onchange('servicecate')
    def onchange_servicecate(self):
        res = {}
        if self.servicecate:
            res['domain'] = {'checklistcat': [('servicetype', '=', self.servicecate.ids)]}
        return res
        
    servicecate = fields.Many2one('service.providertype', string="Service Category", required=True)
    propertys = fields.Many2one('property.land', string="Property Name")

    building = fields.Many2one('property.building', string="Building /Area", domain="[('propertyname', '=', propertys)]")
    floor = fields.Many2one('property.floors', string="Floors", domain="[('building_id', '=', building)]")
    room = fields.Many2one('property.room', string="Rooms", domain="[('floors', '=', floor)]")
    equipment_id = fields.Many2one('equipment.assets', string='Tender Name')
    created_by = fields.Many2one('res.users', 'Created By', default=lambda self: self.env.user, readonly=True)

    date = fields.Datetime(string='Created date', default=fields.Datetime.now, readonly=True) 

    assignto = fields.Many2one('hr.employee', string="Assign To", required=True)

    start_inspection_date = fields.Date(
        string='Start Inspection date', 
        default=fields.Date.context_today,
        help='Date from which the maintenance will we active'
    )

    duration = fields.Float(
        string='Duration (hours)',
        help='Maintenance duration in hours'
    )  

    interval = fields.Integer(
        string='Frequency',
        default=1,
        help='Interval between each maintenance'
    )          

    interval_step = fields.Selection([
        ('day', 'Day(s)'),
        ('week', 'Week(s)'),
        ('month', 'Month(s)'),
        ('year', 'Year(s)')],
        string='Recurrence',
        default='year',
        help="Let the event automatically repeat at that interval step"
    )  

    inspection_plan_horizon = fields.Integer(
        string='Planning Horizon period',
        default=1,
        help='Maintenance planning horizon. Only the maintenance requests '
             'inside the horizon will be created.'
    )
    
    planning_step = fields.Selection([
        ('day', 'Day(s)'),
        ('week', 'Week(s)'),
        ('month', 'Month(s)'),
        ('year', 'Year(s)')],
        string='Planning Horizon step',
        default='year',
        help="Let the event automatically repeat at that interval"
    )                        

    next_inspection_date = fields.Date(
        'Next Inspection date',
        compute='_compute_next_inspection',
        store=True,
        readonly=False
    )                      

    count = fields.Integer(compute='compute_counts')

    asset_type = fields.Selection(
        string='Inspection Type',
        selection=[
            ('property', 'Property'), 
            ('equipment', 'Equipment'),
            ('document', 'Document/Report')
        ],
        default="property"
    )

    inspectionplan_lines = fields.One2many('inspection.plan.line', 'testline_inspectionplan', string="Inspection of Property") 
    inspectionplan_twolines = fields.One2many('inspection.plan.twoline', 'testtwoline_inspectionplan', string="Inspection of Equipment ")      
    inspectionplancheck_twolines = fields.One2many('inspectionplan.check.twoline', 'checktwoline_inspection', string="Inspection of Check ")
    inspcheck_twolines = fields.One2many('inspectiontwoplan.check.twoline', 'checktwoline_insp', string="Inspection of Check equipment ")
    
    def get_request(self):
        self.ensure_one()
        return {
               'type': 'ir.actions.act_window',
               'name': 'Requests',
               'view_type': 'form',
               'view_mode': 'tree,form',
               'res_model': 'inspection.request',
               'domain': [('names', '=', self.name)],
        }
        
    @api.constrains('start_inspection_date')
    def dates(self):
        if self.start_inspection_date < date.today():
            raise ValidationError('Scheduleddate date must be Present Date Or Future Date') 

    def compute_counts(self):
        for record in self:
            record.count = self.env['inspection.request'].search_count([('names', '=', self.name)])  
    
    @api.onchange('equipment_id')
    def checklist_create(self):
        for rec in self:
            if rec.equipment_id:
                checklist = self.env['check.list'].search([('equipment_id', '=', rec.equipment_id.id)], limit=1)
                if checklist:
                    rec.checklistcat = checklist.id
                else:
                    rec.checklistcat = False

    def _create_new_request(self, inspection_plan):
        horizon_date = fields.Date.from_string(fields.Date.today())
        furthest_inspection_todo = self.env['inspection.request'].search(
             [('inspection_plan_id', '=', inspection_plan.id)],
              order="request_date desc", limit=1)
              
        if furthest_inspection_todo:
             next_inspection_date = fields.Date.from_string(
                furthest_inspection_todo.request_date) + get_relativedelta(
                inspection_plan.interval, inspection_plan.interval_step)
        else:
            next_inspection_date = fields.Date.from_string(inspection_plan.next_inspection_date)
            
        requests = self.env['inspection.request']
        
        # Create maintenance request until we reach planning horizon
        while next_inspection_date <= horizon_date:
            if next_inspection_date >= fields.Date.from_string(fields.Date.today()):
                vals = self._prepare_request_from_plan(inspection_plan, next_inspection_date)
                
            requests |= self.env['inspection.request'].create(vals)

            search_var = self.env['inspection.request'].search([('id', '=', requests.id)])
            
            for record in self.inspectionplancheck_twolines:
                search_var.write({
                    'inspectioncheck_twolines': [(0, 0, {
                        'checklist': record.checklist.id,
                        'checklistitem': record.checklistitem.id,
                    })]
                })
                
            for record in self.inspcheck_twolines:
                search_var.write({
                    'inspcheck_twolines': [(0, 0, {
                        'checklist': record.checklist.id,
                        'checklistitem': record.checklistitem.id,
                    })]
                })
                
            next_inspection_date = next_inspection_date + get_relativedelta(
                inspection_plan.interval, inspection_plan.interval_step)
        return requests

    def _prepare_request_from_plan(self, inspection_plan, next_inspection_date):
        description = self.name if self else inspection_plan.name
        assignto = self.assignto.id                         
        scheduleddate = self.next_inspection_date  
        asset_type = self.asset_type
        created_by = self.created_by.id
        propertys = self.propertys.id
        building = self.building.id
        servicecate = self.servicecate.id
        checklistcat = self.checklistcat.id  
        
        return {
             'names': description,
            'assignto': assignto,
            'asset_type': asset_type,         
            'scheduleddate': scheduleddate,    
            'created_by': created_by,    
            'propertys': propertys,
            'building': building,
            'servicecate': servicecate, 
            'checklistcate': checklistcat,  
        }

    @api.model
    def create(self, vals):
        if vals.get('name_seq', _('New')) == _('New'):
            vals['name_seq'] = self.env['ir.sequence'].next_by_code('inspection.plan.sequence') or _('New')
            result = super(inspectionPlan, self).create(vals)
            return result   

    @api.depends('interval', 'interval_step') 
    def _compute_next_inspection(self):
        for plan in self.filtered(lambda x: x.interval > 0):
            interval_timedelta = get_relativedelta(plan.interval, plan.interval_step)
            next_date = plan.start_inspection_date
            while next_date <= fields.Date.today():
                next_date = next_date + interval_timedelta
                plan.next_inspection_date = next_date


class inspectionplanline(models.Model):
    _name = 'inspection.plan.line'

    testline_inspectionplan = fields.Many2one('inspection.plan', string="Inspection")
    building = fields.Many2one('property.building', string="Building /Area")
    floor = fields.Many2one('property.floors', string="Floor Name")
    room = fields.Many2one('property.room', string="Room Name")


class inspectionplantwoline(models.Model):
    _name = 'inspection.plan.twoline'

    testtwoline_inspectionplan = fields.Many2one('inspection.plan', string="Inspection")
    equipments = fields.Many2one('asset.asset', string="Equipment Name")
    checklist = fields.Many2one('check.list', string=" Check List Description ")


class inspectionplanchecktwoline(models.Model):
    _name = 'inspectionplan.check.twoline'

    checktwoline_inspection = fields.Many2one('inspection.plan', string="Inspection Check")
    checklistitem = fields.Many2one('check.list.line', string="Check List Item")
    inspectionfinding = fields.Char(string="Inspection Findings")    
    inpectionresult = fields.Char(string="Inspection Result")    
    comments = fields.Char(string="Comments")    
    identity_card = fields.Many2many('ir.attachment', string="Attachment") 
    checklist = fields.Many2one('check.list', string=" Check List Description For property")
    
    @api.onchange('checklist')
    def constrains_checklist(self):
        return {'domain': {'checklistitem': [('id', '=', self.checklist.appointment_lines.ids)]}}    

    propertys = fields.Many2one('property.land', string="Property Name ")
    building = fields.Many2one('property.building', string="Building /Area")
    floor = fields.Many2one('property.floors', string="Floor Name")
    room = fields.Many2one('property.room', string="Room Name")    
    pointweight = fields.Integer(string="Point Weightage ")


class inspectionrtwoplanchecktwoline(models.Model):
    _name = 'inspectiontwoplan.check.twoline'

    checktwoline_insp = fields.Many2one('inspection.plan', string="Inspection Check for Equipment")
    
    checklist = fields.Many2one('check.list', string=" Check List Description For Equipment")
    checklistitem = fields.Many2one('check.list.line', string="Check List Item")
    inspectionfinding = fields.Char(string="Inspection Findings")    
    inpectionresult = fields.Char(string="Inspection Result")    
    comments = fields.Char(string="Comments")    
    identity_card = fields.Many2many('ir.attachment', string="Attachment")  
    
    @api.onchange('checklist')
    def constrains_checklist(self):
        return {'domain': {'checklistitem': [('id', '=', self.checklist.appointment_lines.ids)]}}        
        
    pointweight = fields.Integer(string="Point Weightage ")  
    floor = fields.Many2one('property.floors', string="Floor Name")
    room = fields.Many2one('property.room', string="Room Name")
    equipments = fields.Many2one('asset.asset', string="Equipment Name")