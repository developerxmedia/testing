# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from odoo.exceptions import ValidationError
from datetime import date
import re
from dateutil.relativedelta import relativedelta
from datetime import datetime, date, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import  UserError
import pytz


class Model(models.Model):
    _name = 'check.type'
    _rec_name = 'typename'

    typename = fields.Char(string='Check List Type', required=True)


class Modeltypecheck(models.Model):
    _name = 'check.type.line'

    name = fields.Many2one('check.type', string='Sub category Type')
    category = fields.Many2one('check.category', string='Types') 


class inherit_ir_attachment(models.Model):
    _inherit = 'ir.attachment'	