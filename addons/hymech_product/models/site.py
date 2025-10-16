from odoo import fields, models, api, tools, _ 
from odoo.exceptions import ValidationError
from datetime import datetime
from io import BytesIO
import qrcode
import base64

class siteModel(models.Model):
    _name = 'site.model'
    _description = 'site Model'
    _rec_name ='site_name'
    
    site_name= fields.Char( string='Site Name')

class passType(models.Model):
    _name = 'pass.type'
    _description = 'Pass Type'
    _rec_name ='pass_type'
    
    pass_type= fields.Char( string='Pass type')
# class TermsConditions(models.Model):
#     _name = 'terms.conditions'
#     _rec_name = 'conditions'

#     conditions = fields.Char("Name")
#     terms = fields.Text('Terms and Conditions')
