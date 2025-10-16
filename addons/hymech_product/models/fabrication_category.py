from odoo import fields, models, api, tools, _ 
from odoo.exceptions import ValidationError
from datetime import datetime
from io import BytesIO
import qrcode
import base64

class fabricationProcess(models.Model):
    _name = 'fabrication.process.category'
    _description = 'Fabrication Process'
    _rec_name ='fabrication_category'

    fabrication_category= fields.Char(string='Category-Fabrication')
    rate_hour= fields.Float(string='Rate per Hour')


class Material(models.Model):
    _name = 'material.desription'
    _description = 'Material Description'
    _rec_name ='material_description'

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
    _rec_name ='types_of_equipment'

    types_of_equipment= fields.Char(string='Equipment')
    rate_hour= fields.Float(string='Rate per Hour')

class Transport(models.Model):
    _name = 'transport.desription'
    _description = 'Transport Description'
    _rec_name ='types_of_transport'

    types_of_transport= fields.Char(string='Equipment')
    rate_hour= fields.Float(string='Rate per Hour')

class Process(models.Model):
    _name = 'process.product'
    _description = 'Process Description'
    _rec_name ='process_product'

    process_product= fields.Char(string='Process')
    description = fields.Char(string='Description')
    # rate_hour= fields.Float(string='Rate per Hour')