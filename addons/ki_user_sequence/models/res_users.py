# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file
# for full copyright and licensing details.

from odoo import models, fields, api
import random
from odoo.exceptions import ValidationError

class ResUsers(models.Model):
	_inherit = 'res.users'

	type_users= fields.Selection([('user', 'User'),('admin', 'Admin')],string='Type')

	