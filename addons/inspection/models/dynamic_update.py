from odoo import models, fields, api
from datetime import datetime


class dynamic_update(models.Model):
    _name = 'message.content'
    _rec_name = 'message'


    message = fields.Char(string='Message')
    status = fields.Char(string='Status')
    date_time = fields.Datetime(string='Date')
    event = fields.Char(string='Event')
    time=fields.Char(string="Time")
    select_type = fields.Selection([('interval','Interval'),('datetime','Datetime'),('time','Time')],string="Type")
    interval=fields.Char(string="Interval")

