# -*- coding: utf-8 -*-


from odoo import models, fields, api, exceptions
from odoo.exceptions import ValidationError
from datetime import date
import re
from dateutil.relativedelta import relativedelta


class propertytypes(models.Model):
    _name = 'property.types'


    name = fields.Char(string='Property Type')

class buildingarea(models.Model):
    _name = 'buildingarea.type'


    name = fields.Char(string='Building /Facility Type')
