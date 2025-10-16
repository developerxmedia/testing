from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HREmployee(models.Model):
    _inherit = 'hr.employee'

    chat_id = fields.Char(string="Telegram Chat ID", required=True, unique=True)