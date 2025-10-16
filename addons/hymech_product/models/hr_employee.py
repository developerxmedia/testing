from odoo import fields, models, api, tools, _ 
from odoo.exceptions import ValidationError
from datetime import datetime
from io import BytesIO
import qrcode
import base64

class inherit_hr_employee_account_move_linesssss(models.Model):
    _inherit = 'hr.employee'

    sb_no=fields.Char('SB NO')
    children_ids = fields.One2many('hr.employee.line', 'emp_id', string='Details')
    received_dates = fields.Date(string='Received Date')

    def action_employee_documents(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Employee Document',
            'res_model': 'hr.employee.line',
            'domain': [('emp_id', '=', self.id)],
            'view_mode': 'tree,form',
        }

class employee(models.Model):
    _name='hr.employee.line' 
    _rec_name='operator'

    operator= fields.Many2one('operator.master',string='Operator')
    num=fields.Char(string='No.')
    attachment= fields.Many2many('ir.attachment', string="Attachment",attachment=True)
    file_name = fields.Char("File Name")
    expiry_date= fields.Date(string='Expiry Date')
    emp_id= fields.Many2one('hr.employee', string='EMP')

class operator(models.Model):
    _name='operator.master'
    _rec_name ='operator'

    operator= fields.Char(string='Operator')
    
