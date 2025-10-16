# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError,  UserError
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import pytz
import re

class ModelequimentType(models.Model):
    _name = 'equiment.type'
    _rec_name = 'name'

    name = fields.Char(string='Asset Type')


class ModelequimentCategory(models.Model):
    _name = 'equiment.category'
    _rec_name = 'name'

    name = fields.Char(string='Asset Category')
