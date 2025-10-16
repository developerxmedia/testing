from odoo import fields, models, api, tools, _ 
from odoo.exceptions import ValidationError
from datetime import datetime
from io import BytesIO
import qrcode
import base64

class ManPower(models.Model):
    _name = 'man.power.category'
    _description = 'Man Power'
    _rec_name ='man_power_category'

    man_power_category= fields.Char(string='category')
    rate_hour= fields.Float(string='Rate per Hour')
    work_hourss= fields.Float(string='Working hour')
    
    