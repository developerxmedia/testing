# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PropertyMaster(models.Model):
    _name = 'master.property'
    _description = 'Property Master'

    name = fields.Many2one('property.land', string='Property Name', required=True)


class PropertyMasterLine(models.Model):
    _name = 'master.property.line'
    _description = 'Property Master Line'

    name = fields.Many2one('property.building', string='Building Name', required=True)
    master_id = fields.Many2one('master.property', string="Property Master", required=True)

    # Property Name — ideally link to master property for consistency
    property_id = fields.Many2one('property.land', string='Property Name', related='master_id.name', store=True)

    floors = fields.Many2many('property.floors', string='Floor Name')
    rooms = fields.Many2many('property.room', string='Room No')
