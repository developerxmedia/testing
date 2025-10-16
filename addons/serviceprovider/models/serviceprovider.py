# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date
import re
from dateutil.relativedelta import relativedelta
from datetime import datetime, date, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import  UserError
import pytz


class Model(models.Model):
    _name = 'service.provider'
    _rec_name = 'names'
    # _inherit = ['mail.thread', 'mail.activity.mixin', 'utm.mixin']

    names = fields.Many2one(
        'res.partner', string='Company Name', required=True,
        domain=[('serviceprovider', '=', True)]
    )
    Servicetype = fields.Many2one(
        'service.providertype', string='Service Type', required=True
    )
    contracttypes = fields.Many2one(
        'hr.contract', string='Contract type', required=True
    )
    mob_no = fields.Char(string="Mobile Number")
    address = fields.Text(string="Address")
    state_id = fields.Many2one('res.country.state', string='State')
    country_id = fields.Many2one('res.country', string='Country')
    active_available = fields.Boolean(string="Active", default=True)
