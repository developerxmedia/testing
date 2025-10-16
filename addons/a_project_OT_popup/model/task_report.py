from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, date, timedelta

class overTime(models.Model):
    _name = 'hr.over.time'
    _description = "OT Model"
    _rec_name ='date'
    # _inherit = ['mail.thread','mail.activity.mixin']

    user = fields.Many2one('res.users', string = 'User')
    employee = fields.Many2one('hr.employee', string = 'Employee')
    date = fields.Date(string = 'Date' , default=date.today())
    over_time = fields.Float(string = 'OT Time')
    status = fields.Selection([('requested', 'Requested'),('granted', 'Granted'),('rejected', 'Rejected')],string='Status',default='requested')

    # client_name= fields.Char( string="Client's Client name")

    def button_grant(self):
        for rec in self:
            rec.status = 'granted'

    def overtime_popup(self):
        orm_user= self.env['hr.attendance'].search([('check_in', '>=', date.today()),('check_in', '<', date.today() + timedelta(days=1)),('check_out', '=', False)])
        for record in orm_user:
            notification_list_obj = self.env['notification.list']
            new_notification_record = notification_list_obj.create({
                'name': 'OT Requesting', 
                'module_name': 'task',
                'user': True,
                'assigned_user': record.employee_id.user_id.id,
                'description': 'Are you going to work? Over time'
            })

            

class overTimeAttendanc(models.Model):
    _inherit = 'hr.attendance'

    over_time = fields.Float(string = 'OT Time')

            