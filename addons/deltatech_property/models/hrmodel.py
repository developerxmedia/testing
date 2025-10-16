# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from odoo.exceptions import ValidationError
from datetime import date
import re
from dateutil.relativedelta import relativedelta
from datetime import datetime, date, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import  UserError





class hremployeein(models.Model):
    _inherit = 'hr.employee'


    buildingmanager = fields.Selection( [ 
                    ('propertyowner', 'Property Owner'), 
                    ('administrativemanager', 'Administrative Manager'),
                    ('propertymanager', 'Property Manager '),
                    ('Buildingmanager', 'Building Manager'),
                    ('floormanager', 'Floor Manager'),
                    ('Supervisor', 'Supervisor'),
                    ('inspector', 'Inspector'),],default="propertyowner" ,required=True,
                    string='Job Role') 

    work_address_id = fields.Char(string='Work Address') 
    #equipment_count = fields.Integer(string='Equipment Count')
    private_address_id = fields.Char(string='Private address') 


    # Your existing fields...
    equipment_count = fields.Integer(string='Equipment Count', compute='_compute_equipment_count')
    # @api.depends()
    # def _compute_equipment_count(self):
    #     for employee in self:
    #         count = self.env['equipment.assets'].search_count([
    #             ('responsible_user_id', '=', employee.user_id.id)  # ✅ correct
    #         ])
    #         employee.equipment_count = count


    # @api.depends()
    # def _compute_equipment_count(self):
    #     for employee in self:
    #         count = self.env['equipment.assets'].search_count([
    #             ('responsible_user_id', '=', employee.user_id.id)  # Adjust field name as needed
    #         ])
    #         employee.equipment_count = count