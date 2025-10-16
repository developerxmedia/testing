# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import date
import string
import io
import random
import base64
import qrcode
import json
from odoo import tools


class newassets(models.Model):
    _name = 'equipment.assets'
    _rec_name = 'names'

    names = fields.Char(string='Asset Name', required=True)
    propertys = fields.Many2one('property.land', string='Property')
    floors = fields.Many2one('property.floors', string='Floor')
    buildings = fields.Many2one('property.building', string='Building')
    rooms = fields.Many2one('property.room', string='Unit')
    serviceprovider = fields.Many2one('res.partner', string='Service Provider', domain=[('serviceprovider', '=', True)])
    active = fields.Boolean('Active', default=True)
    asset_classfication = fields.Many2one('equipment.classification', string='Asset Classification')
    asset_number = fields.Char('Asset Number', size=64)
    _sql_constraints = [
        ('number_uniq', 'UNIQUE(asset_number)', 'Asset Number already exists !')
    ]
    description = fields.Text('O&M Reference')
    model = fields.Char('Model', size=64)
    image_small = fields.Binary("Small-sized image")
    serial = fields.Char('Serial no.', size=64)
    subarea = fields.Many2one('property.room', string='Sub Area')
    length = fields.Float('L')
    width = fields.Float('W')
    height = fields.Float('H')
    iotequipment = fields.Char(string='IOT Equipment')
    start_date = fields.Date('Installation Date')
    vendor_id = fields.Many2one('res.partner', 'Vendor')
    purchase_date = fields.Date('Purchase Date')
    warranty_start_date = fields.Date('Warranty Start')
    manufacturer_id = fields.Many2one('res.partner', 'Manufacturer')
    warranty_end_date = fields.Date('Warranty End')
    image = fields.Binary("Image")
    qrcodes = fields.Char(string='QR Code', copy=False, default=lambda s: s._default_secret())
    qr_code_image = fields.Binary('QR Code')
    project_id = fields.Many2one('project.project', 'Project')
    sensitivity_level = fields.Selection([
        ('0', 'Low'), ('1', 'Medium'), ('2', 'High'), ('3', 'Critical')
    ], string='Sensitivity Level')
    classification = fields.Selection([
        ('0', 'Public'), ('1', 'Internal'), ('2', 'Confidential'), ('3', 'High Confidential')
    ], string='Classification')

    category_ids = fields.Many2one('equipment.category', string='Asset Category')
    criticality = fields.Selection([
        ('0', 'General'), ('1', 'Important'), ('2', 'Very important'), ('3', 'Critical')
    ], string='Criticality')
    user_id = fields.Many2one('res.users', 'Assigned to')
    image_medium = fields.Binary("Medium-sized image")
    equipmentcat = fields.Many2one('equipment.categorytypes', string='Asset Type')
    doc_count = fields.Integer(string="Number of documents", compute='_get_attached_docs')
    risk_count = fields.Integer(string="Risk", compute='_get_risk_count', store=True)

    def _default_secret(self):
        alphabet = string.ascii_letters + string.digits
        qrcodes = ''.join(random.SystemRandom().choice(alphabet) for _ in range(15))
        return qrcodes

    @api.constrains('names')
    def _generate_qr_code(self):
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=20, border=4)
        if self.names:
            data = json.dumps({"type": "equipment", "id": self._origin.id})
            qr.add_data(data)
            qr.make(fit=True)
            img = qr.make_image()
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            qrcode_img = base64.b64encode(buffer.getvalue())
            self.update({'qr_code_image': qrcode_img})

    @api.onchange('category_ids')
    def constrains_equipmentcat(self):
        return {'domain': {'equipmentcat': [('categorytypes', '=', self.category_ids.name)]}}

    @api.onchange('propertys')
    def onchange_propertys_id(self):
        for rec in self:
            return {'domain': {'buildings': [('propertyname', '=', rec.propertys.id)]}}

    @api.onchange('buildings')
    def onchange_buildings_id(self):
        for rec in self:
            return {'domain': {'floors': [('building_id', '=', rec.buildings.id)]}}

    @api.onchange('floors')
    def onchange_floors_id(self):
        for rec in self:
            return {'domain': {'subarea': [('floors', '=', rec.floors.id), ('floor_type', '=', 'l')]}}

    @api.onchange('floors')
    def onchange_floors(self):
        for rec in self:
            return {'domain': {'rooms': [('floors', '=', rec.floors.id), ('floor_type', '!=', 'l')]}}

    @api.depends("risk_count")
    def _get_risk_count(self):
        for rec in self:
            risk_counts = self.env['risk.incident'].search([('project_id', '=', rec.project_id.id)])
            rec.risk_count = len(risk_counts)

#     @api.depends('_name')
#     def _get_attached_docs(self):
#         for record in self:
#             domain = [('res_model', '=', self._name), ('res_id', '=', record.id)]
#             record.doc_count = self.env['ir.attachment'].search_count(domain)

    def _get_attached_docs(self):
        for record in self:
            domain = [('res_model', '=', record._name), ('res_id', '=', record.id)]
            record.doc_count = self.env['ir.attachment'].search_count(domain)


    def attachment_tree_view(self):
        domain = [('res_model', '=', self._name), ('res_id', 'in', self.ids)]
        return {
            'name': 'Document',
            'domain': domain,
            'res_model': 'ir.attachment',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'view_type': 'form',
            'limit': 80,
            'context': "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id)
        }

    def button_risk_management_view(self):
        return {
            'name': 'Risk',
            'res_model': 'risk.incident',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'limit': 80,
            'domain': [('project_id', '=', self.project_id.id)]
        }


class equipment_category(models.Model):
    _description = 'equipment Tags'
    _name = 'equipment.category'

    name = fields.Char('Category', required=True, translate=True)
    tickets_count = fields.Integer('Tickets Count', compute='compute_tickets_count')
    active = fields.Boolean("Active", default=True)

    def compute_tickets_count(self):
        for record in self:
            record.tickets_count = self.env['inspectiontwo.check.twoline'].search_count(
                ['|', ('equipments.category_ids', '=', record.id),
                 ('equipment_category_id', '=', record.id),
                 ('checktwoline_insp', '!=', False)]
            )

    def tickets_view(self):
        for record in self:
            lines = self.env['inspectiontwo.check.twoline'].search(
                ['|', ('equipments.category_ids', '=', record.id), ('equipment_category_id', '=', record.id)]
            )
            tickets_ids = [line.checktwoline_insp.id for line in lines if line.checktwoline_insp.id]

            return {
                'name': 'Inspection Tickets',
                'type': 'ir.actions.act_window',
                'res_model': 'inspection.request',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', tickets_ids)],
                'context': "{'create': False}",
            }


class equipment_categorytypes(models.Model):
    _description = 'equipment cat'
    _name = 'equipment.categorytypes'

    name = fields.Char('Types', required=True, translate=True)
    categorytypes = fields.Many2one('equipment.category', 'Category')


class assetclassification(models.Model):
    _description = 'equipment classification'
    _name = 'equipment.classification'

    name = fields.Char('Classification', required=True, translate=True)
