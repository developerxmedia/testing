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
    _name = 'inspector.task'

    _rec_name = 'name'


    name = fields.Char(string='Inspection  Name')


    scheduleddate = fields.Date(string='Scheduled Date')


    created_by = fields.Many2one('hr.employee',string="Created By")

    date = fields.Datetime(string='Created date',default=fields.Datetime.now ,readonly=True) 

    assignto = fields.Many2one('hr.employee',string="Assign To")

    asset_type = fields.Selection(string='Inspection Type',
        selection=[('building', 'Property'), ('equipment', 'Equipment')],default="building")

    inspectionstart = fields.Datetime(string="Inspection Start Time ")    

    inspectionend = fields.Datetime(string="Inspection End Time")    



    inspector_lines = fields.One2many('inspector.request.line', 'testline_inspection', string="Inspection of Property")

class inspectiorrequestline(models.Model):
    _name = 'inspector.request.line'



    testline_inspection = fields.Many2one('inspector.task', string="Inspection")


    building = fields.Many2one('property.building', string="Building /Area")
    
    floor = fields.Many2one('property.floors', string="Floor Name")
    
    room = fields.Many2one('property.room', string="Room Name")


    checklistname = fields.Many2one('check.list', string="CheckList Name")

    checklistitem = fields.Char( string="CheckList Item") 
  

    inspectionfind = fields.Char( string="Inspection Finding")

        


    inspectionresult = fields.Char( string="Inspection Result")  

    comments = fields.Char( string="Comments")         


    identity_card= fields.Many2many(comodel_name="ir.attachment", 
                                    relation="m2m_ir_identity_card_rel", 
                                    column1="m2m_id",
                                    column2="attachment_id",
                                    string="Attachments ")    


    inspec = fields.Many2one('inspection.request', string="insp Name")
