# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date


class Modelagreement(models.Model):
    _name = 'service.agreement'
    _rec_name = 'name'

    name = fields.Many2one(
        'res.partner', string='Service Provider', required=True,
        domain=[('serviceprovider', '=', True)]
    )
    agreementtype = fields.Many2one('agreement.type', string='Agreement Type')
    servicetype = fields.Many2one('service.providertype', string='Service Type')
    #agreementdate = fields.Date(string='Agreement Date', required=True, default=date.today)
    # Option 2: String representation
    agreementdate = fields.Date(string='Agreement Date',required=True,default=fields.Date.today())
    agreementperiod = fields.Char(string='Agreement Period')
    servicestart = fields.Date(string='Service Start Date', required=True)
    serviceexpiry = fields.Date(string='Service Expiry Date', required=True)

    @api.constrains('servicestart', 'serviceexpiry')
    def dateservice(self):
        for record in self:
            if record.servicestart > record.serviceexpiry:
                raise ValidationError('End date must be greater than Start date')

    @api.constrains('agreementdate')
    def date(self):
        for record in self:
            if record.agreementdate < date.today():
                raise ValidationError('Agreement date must be Present Date Or Future Date')

\
    servicetypesline = fields.One2many(
        'property.list.line', 'test_lineservice', string="Service Type"
    )
    appointment_twolines = fields.One2many(
        'property.two.line', 'test_line_appointments', string="Equipment"
    )


class Propertylist(models.Model):
    _name = 'property.list.line'
    _rec_name = 'servicetype'

    servicetype = fields.Many2one('service.providertype', string='Service Type')
    test_lineservice = fields.Many2one('service.agreement', string="Service Type")


class Propertylisttwo(models.Model):
    _name = 'property.two.line'

    test_line_appointments = fields.Many2one('service.agreement', string="Name of Equipment")
    equipmenttypes = fields.Many2one('asset.category', string='Equipment Type')
    equipmentcategory = fields.Many2one('asset.categorytypes', string='Equipment Category')
    equipmentid = fields.Many2one('asset.asset', string='Equipment ID')
