from odoo import fields, models, api, tools, _ 
from odoo.exceptions import ValidationError
from datetime import datetime
from io import BytesIO
import qrcode
import base64

class passModel(models.Model):
    _name = 'pass.model'
    _description = 'Pass Model'
    _rec_name ='employee_name'
    
    employee_name= fields.Many2one('hr.employee', string='Employee Name')
    expiry_date = fields.Date(string='Expiry Date')
    pass_name= fields.Char(string='Pass Name')
    site_name = fields.Many2one('site.model', string='Site Name')
    pass_type = fields.Many2one('pass.type', string='Pass Type')    