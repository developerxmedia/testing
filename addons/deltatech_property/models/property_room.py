# -*- coding: utf-8 -*-
# ©  2015-2019 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

import base64
import qrcode
import json
import string
import io

selection_level = [('p', 'P'), ('m', 'M'), ('s', 'S')] + [(str(num), str(num)) for num in range(1, 30)]


class PropertyRoom(models.Model):
    _name = 'property.room'
    _description = "Room"
    _rec_name  = 'complete_name'  

    name = fields.Char(string="Room No" , required=True)
    building_id = fields.Many2one('property.building', string='Building', required=True)
#new    
    propertys = fields.Many2one('property.land', string='Property', required=True)
    level = fields.Selection(selection_level)
    roomspar = fields.Many2one('property.room', string='Parent Room',domain=[('floor_type', '!=', 'l')])
    roomstypes = fields.Many2one('room.types', string='Room Usage Type',)
    height = fields.Float()
    perimeter = fields.Float()
    surface_disinsection = fields.Float(string="Area of disinsection", compute="_compute_surface_disinsection", store=True)

    surface = fields.Float("Surface area")
    surface_cleaning_floor = fields.Float(string="Surface cleaning floor")
    surface_cleaning_doors = fields.Float(string="Surface cleaning doors")
    surface_cleaning_windows = fields.Float(string="Surface cleaning window")

    floors = fields.Many2one('property.floors',string="Floor")

    supervisor = fields.Many2one('hr.employee',string="Area Representative",domain=[('buildingmanager', '=', 'Supervisor')])

    floor_type = fields.Selection([('c', 'Apartment'), ('r', 'Retail'),('o', 'Offices'),('g', 'General Service'),('l', 'Internal Area') ],string="Space Type" ,default="c")

    usage = fields.Selection([
        ('office', 'Office'),
        ('meeting', 'Meeting room'),
        ('kitchen', 'Kitchen'),
        ('laboratory','Laboratory'),
        ('garage','Garage'),
        ('archive', 'Archive'),
        ('warehouse', 'Warehouse'),
        ('log_warehouse', 'Logistics warehouse'),
        ('it_endowments', 'IT endowments (Ranks, Hall Servers)'),
        ('premises', 'Technical premises (thermal, air conditioning, post-transformer)'),
        ('cloakroom', 'Cloakroom'),
        ('sanitary', 'Sanitary group'),
        ('access', 'Access ways'),
        ('lobby', 'Lobby'),
        ('staircase', 'Staircase'),

        ('living', 'Living Room'),
        ('bedroom', 'Bedroom'),
        ('balcony', 'Balcony')
    ], string="Room usage Type", help="The purpose of using the room", default='bedroom')

#    rented_room = fields.Boolean()
 #   tenant_id = fields.Many2one('res.partner', string="Tenant")

    last_maintenance = fields.Date()
    technical_condition = fields.Selection([('0','Missing'),('1','Unsatisfactory'),('3','good'),('5','very good')],
                                           group_operator='avg')

    heightroom = fields.Float(string="Height ")

    widthroom = fields.Float(string="Width ")
    lengthroom = fields.Float(string="Length ")
    qr_code_image = fields.Binary('QR Code')

    @api.constrains('name')
    def _generate_qr_code(self):
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=20, border=4)
        if self.name :
            data = json.dumps({"type":"property", "id": self._origin.id})
            qr.add_data(data)
            qr.make(fit=True)
            img = qr.make_image()
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            qrcode_img = base64.b64encode(buffer.getvalue())
            self.update({'qr_code_image': qrcode_img,})



    @api.model
    @api.depends('surface', 'height', 'perimeter')
    def _compute_surface_disinsection(self):
        for room in self:
            room.surface_disinsection = 2 * room.surface + room.height * room.perimeter

    @api.constrains
    def _check_cleaning_surface(self):
        if self.cleaning_surface > self.surface:
            raise ValidationError(_('Cleaning surface most by lower that surface area'))



    def show_equipment(self):
    
        return {
                'name': "Projects",
                 'domain': [('rooms', '=', self.id)],
                'view_mode': 'kanban,tree,form',
                'res_model': 'equipment.assets',
                'view_type': 'form',
               'type': 'ir.actions.act_window',
                # 'context': 
                #         "{'default_res_model': '%s','default_res_id': %d}" ,
                             }  
    def show_parentequip(self):
        
        return {
                'name': "Projects",
                 'domain': [('subarea', '=', self.complete_name)],
                'view_mode': 'kanban,tree,form',
                'res_model': 'equipment.assets',
                'view_type': 'form',
               'type': 'ir.actions.act_window',
                # 'context': 
                #         "{'default_res_model': '%s','default_res_id': %d}" ,
                             } 
    def show_subroom(self):
        domain = [('floor_type', '=', 'l'),('roomspar', '=', self.id)]
        return {
                'name': "Internal Area",
                 'domain': domain,
                'view_mode': 'kanban,tree,form',
                'res_model': 'property.room',
                'view_type': 'form',
               'type': 'ir.actions.act_window',
                'context': 
                        "{'search_default_roomspar': 1}" ,
                             } 
        
    parentequip_count = fields.Integer(
        compute='compute_parentequip'
        )
    
    subroom_count = fields.Integer(
        compute='compute_subroomcount'
        ) 
        
    def compute_parentequip(self):
        for record in self:
            record.parentequip_count = self.env['equipment.assets'].search_count(
                [('subarea', '=', record.complete_name)]) 
            
    def compute_subroomcount(self):
        for record in self:
            record.subroom_count = self.env['property.room'].search_count(
                [('floor_type', '=', 'l'),('roomspar', '=', record.id) ]) 
            

    active = fields.Boolean(default=True)
    equipment_count = fields.Integer(compute='compute_count')
    def compute_count(self):
        for record in self:
            record.equipment_count = self.env['equipment.assets'].search_count(
                [('rooms', '=', record.id)]) 
    complete_name = fields.Char('Room/Space', compute='_compute_complete_name',store=True)  
         
    @api.depends('name', 'roomspar.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.roomspar:
                category.complete_name = '%s / %s' % (category.roomspar.complete_name, category.name)
            else:
                category.complete_name = category.name  
    @api.onchange('propertys')
    def onchange_propertys_id(self):
        for rec in self:
            return {'domain':{'building_id':[('propertyname', '=', rec.propertys.id)]}} 
        
    @api.onchange('building_id')
    def onchange_building_id(self):
        for rec in self:
            return {'domain':{'floors':[('building_id', '=', rec.building_id.id)]}}  
        
    @api.onchange('floors')
    def onchange_floors_id(self):
        for rec in self:
            return {'domain':{'roomspar':[('floors', '=', rec.floors.id)]}}    


class Roomtypes(models.Model):
    _name = 'room.types'
    _description = "Roomtypes"

    name = fields.Char(string="Room Usage Type")