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
    _name = 'service.providertype'
    _rec_name = 'complete_name'

    name = fields.Char(string='Service Type')

    servicescategorys = fields.Many2one('service.providertype', string='Parent Category')

    # servicecategory = fields.Many2one('service.providertype.category', string='Service Category')

    complete_name = fields.Char('Service Name', compute='_compute_complete_name', store=True)

    inspectors = fields.Many2many('hr.employee', string='Inspectors')

    @api.depends('name', 'servicescategorys.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.servicescategorys:
                category.complete_name = '%s / %s' % (category.servicescategorys.complete_name, category.name)
            else:
                category.complete_name = category.name


class subcategoryprov(models.Model):
    _name = 'service.providertype.category'
    _rec_name = 'category'

    category = fields.Char(string='Service category')

    name = fields.Char(string='Service Subcategory')

    @api.model
    def name_get(self):
        result = []
        for s in self:
            name = s.category + '/' + s.name
            result.append((s.id, name))
        return result

    # combination = fields.Char(string='Category', compute='_compute_fields_combination')

    # @api.depends('category', 'name')
    # def _compute_fields_combination(self):
    #     for test in self:
    #         test.combination = test.category + test.name
