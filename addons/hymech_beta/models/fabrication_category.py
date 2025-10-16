from odoo import fields, models, api, tools, _ 
from odoo.exceptions import ValidationError
from datetime import datetime
from io import BytesIO
import qrcode
import base64

class fabricationProcess(models.Model):
    _name = 'fabrication.process.category'
    _description = 'Fabrication Process'

    fabrication_category= fields.Char(string='Category-Fabrication')
    rate_hour= fields.Float(string='Rate per Hour')

class Material(models.Model):
    _name = 'material.desription'
    _description = 'Material Description'

    material_description= fields.Char(string='Description')
    cost= fields.Float(string='Cost')

class Tools(models.Model):
    _name = 'tools.desription'
    _description = 'Tools Description'
    _rec_name ='tools_description'

    tools_description= fields.Char(string='Description')
    cost= fields.Float(string='Cost')

class Equipment(models.Model):
    _name = 'equipment.desription'
    _description = 'Tools Description'

    types_of_equipment= fields.Char(string='Equipment')
    rate_hour= fields.Float(string='Rate per Hour')

class Transport(models.Model):
    _name = 'transport.desription'
    _description = 'Transport Description'

    types_of_transport= fields.Char(string='Equipment')
    rate_hour= fields.Float(string='Rate per Hour')