# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError,  UserError
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import pytz
import re

class AgreementType(models.Model):
    _name = 'agreement.type'
    _rec_name = 'name'

    name = fields.Char(string='Agreement Type')
