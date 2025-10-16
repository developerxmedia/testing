# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date

class FacilityMaster(models.Model):
    _name = 'facility.master'
    _description = 'Facility Master'

    name = fields.Many2one('service.providertype', string='Service Type', required=True)
    servicecategory = fields.Many2one('service.providertype.category', string='Service Category')
