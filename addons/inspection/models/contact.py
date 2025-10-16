# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from odoo.exceptions import ValidationError
from datetime import date
import re
from dateutil.relativedelta import relativedelta


class my_customize_contacts(models.Model):
    _inherit = 'res.partner'

    serviceprovider = fields.Boolean(string='Is a Service Provider') 
    count = fields.Integer(compute='compute_count')

    def get_vehicles(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Agreement',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'service.agreement',
            'domain': [('name', '=', self.id)],
        }

    def compute_count(self):
        for record in self:
            record.count = self.env['service.agreement'].search_count([('name', '=', self.id)])