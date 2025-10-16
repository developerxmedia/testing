from odoo import models, fields, api
from datetime import datetime
import requests
import json

class NotificationList(models.Model):
    _name = 'notification.list'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Notification"

    name = fields.Char(string="Name", required=True)
    description = fields.Html(string="Description", track_visibility='onchange')

    status_id = fields.Selection([
        ('assigned','Assigned'),
        ('new','New'),
        ('onhold','On Hold'),
        ('waiting','waiting for Spare'),
        ('complete','Completed'),
        ('cancel','Cancel')
    ], string='Status', track_visibility='onchange')

    read_status = fields.Selection([
        ('read','Readed'),
        ('un_read','Un Read')
    ], string='View', default='un_read', track_visibility='onchange')

    res_users = fields.Many2one('res.users', string='Users')
    res_partner_id = fields.Many2one('res.partner', string='Partner')
    project_id = fields.Many2one('project.project', string='Project')
    date = fields.Date(string="Date", default=datetime.now())
    image = fields.Image(string="Image")
    background_image = fields.Image(string="Background Image")

    # Boolean fields
    manager = fields.Boolean(string='Is Manager')
    user = fields.Boolean(string='Is User')
    worker = fields.Boolean(string='Is Worker')
    tech = fields.Boolean(string='Is Tech')

    assigned_user = fields.Many2one('res.users', string='Assigned Users')
    task_id = fields.Many2one("project.task", string="Task")
    inspection_task = fields.Many2one('inspection.request', string="Inspection Task")

    module_name = fields.Selection([
        ('sale','Sale'),('purchase','Purchase'),('leave','Leave'),
        ('activity','Activity'),('crm','CRM'),('account','Account'),
        ('fsm','FSM'),('services','Services'),('task','Task'),('project','Project')
    ], string="Module")

# class notification_list(models.Model):
#     _name='notification.list'
#     _rec_name='name'
#     _inherit = ['mail.thread', 'mail.activity.mixin',]
#     _description = "Notification"

#     name= fields.Char(string="Name",required=True)
#     description = fields.Html(string="Description",track_visibility='onchange')
#     status_id = fields.Selection([('assigned','Assigned'),
#                                   ('new','New'),
                                  
#                                   ('onhold','On Hold'),
#                                   ('waiting','waiting for Spare'),
#                                   ('complete','Completed'),
#                                   ('cancel','Cancel ')],string='Status',track_visibility='onchange')
    
#     read_status = fields.Selection([('read','Readed'),('un_read','Un Read')],string='View',default="un_read",track_visibility='onchange')
#     res_users = fields.Many2one('res.users',string='Users')
#     res_partner_id = fields.Many2one('res.partner',string='Partner')
#     project_id = fields.Many2one("project.project",string="Project")
    
#     #boolen field
#     manager = fields.Boolean(string='Is Manager')
#     user = fields.Boolean(string='Is User')
#     worker = fields.Boolean(string='Is Worker')
#     assigned_user = fields.Many2one('res.users',string='Assigned Users')
#     task_id = fields.Many2one("project.task",string="Task")
#     module_name = fields.Selection([('sale','Sale'),('purchase','Purchase'),('leave','Leave'),('activity','Activity'),('crm','CRM'),('account','Account'),('fsm','FSM'),('services','Services'),('task','Task'),('project','Project')],string="Module")


class signal_master(models.Model):

    _name = 'one.signal.master'
    _rec_name = 'user_id'

    user_id = fields.Many2one('res.users',string='User Name')
    signal_type= fields.Selection([('android',"Android"),('ios',"IOS")],string="Signal Type")
    key = fields.Char('Key ID')
    

    
class ProjectTaskInherit(models.Model):
    _inherit = "project.task"
    
    @api.constrains('user_id')
    def task_notification_user_assign(self):
        for rec in self:
            if self.user_id:
                vals={
                    'name':'Task',
                    'description':f"You have been assigned a new task({rec.name}) in {rec.project_id.name}. Check it out and start work on  it!.",
                    'res_users' : self.user_id.id,
                    'user':True,
                    'task_id': self.id
                }
                
                self.env['notification.list'].create(vals)
                                

    # @api.constrains("stage_id")
    # def complete_stage_notification(self):
    #     for rec in self:
    #         if rec.stage_id.is_closed == True:
    #             vals={
    #             'name':'Task',
    #             'description':f"Great Job! Task {rec.name} has been completed.",
    #             'res_users' : rec.user_id.id,
    #             'user':True,
    #             'task_id': rec.id
    #             }
    #             self.env['notification.list'].create(vals)
                

    # def deadline_notification(self):
    #     product_ids = self.search([])
    #     for rec in product_ids:
    #         if rec.date_deadline and rec.stage_id.is_closed == False:
    #             today = datetime.now().date()
            
    #             if rec.date_deadline == today:
    #                 vals={
    #                 'name':'Task',
    #                 'description':(f"Task {rec.name} is due today. Complete it on time"),
    #                 'res_users' : rec.user_id.id,
    #                 'user':True,
    #                 'task_id': rec.id
    #                 }
    #                 self.env['notification.list'].create(vals)
                    
            
    #             if rec.date_deadline < today:
    #                 vals={
    #                 'name':'Task',
    #                 'description':(f"Your task {rec.name} is overdue; please complete it."),
    #                 'res_users' : rec.user_id.id,
    #                 'user':True,
    #                 'task_id': rec.id
    #                 }
    #                 self.env['notification.list'].create(vals)
                    
                
class ProjectInherit(models.Model):
    _inherit = "project.project"
    
    @api.constrains('name')
    def project_stage_assign(self):
        project=self.env['project.project'].search([])
        pro = list(map(lambda pro: pro.id, project))
        
        stage=self.env['project.task.type'].search([('active','=',True)])
        for rec in stage:
            rec.project_ids = pro
            
        
        vals={
        'name':'Project',
        'description':(f"A new project, {self.name} has been created"),
        'manager':True,
        'res_users' : self.user_id.id
        }
        self.env['notification.list'].create(vals)