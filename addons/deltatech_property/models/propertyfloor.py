# -*- coding: utf-8 -*-


from odoo import models, fields, api, exceptions
from odoo.exceptions import ValidationError
from datetime import date
import re
from dateutil.relativedelta import relativedelta


class propertyfloors(models.Model):
	_name = 'property.floors'



	name = fields.Char(string='Floor Name', required=True)

	propertys = fields.Many2one('property.land', string='Property', required=True)

	floormanager = fields.Many2one('hr.employee', string='Floor Manager')
	building_id = fields.Many2one('property.building', string='Building', required=True)
	
	active = fields.Boolean(default=True)
 	
	internal_count = fields.Integer(compute='compute_internalcount')
 
	surface = fields.Float("Surface area")
	room_count = fields.Integer(compute='compute_roomcount')
	equipment_count = fields.Integer(compute='compute_count')
	def show_rooms(self):
		return {
                'name': "Rooms",
                'domain': [('floors', '=', self.id),('floor_type', '=', 'c')],
                'view_mode': 'kanban,tree,form',
                'res_model': 'property.room',
                'view_type': 'form',
               'type': 'ir.actions.act_window',
                'context': 
                        "{'search_default_building_id': 1}" ,
                             }
    
	@api.onchange('propertys')
	def onchange_propertys_id(self):
		for rec in self:
			return {'domain':{'building_id':[('propertyname', '=', rec.propertys.id)]}}      	

        
	roomslist = fields.One2many('property.rooms.list', 'roomlist', string="Room List ")
 	
	
	floorstypes = fields.Many2one('floor.types.list', string='Floor Type')	
	height = fields.Float()
	
	perimeter = fields.Float()
	
	heightfloor = fields.Float(string="Height")	
	
	widthfloor = fields.Float(string="Width")
	
	lengthfloor = fields.Float(string="Length")  	
	roomclean = fields.Float(string="Surface cleaning window")	
	
	doorclean = fields.Float(string="Surface cleaning doors")		
	surface_cleaning_floor = fields.Float(string="Surface cleaning floor")		
	floor_types = fields.Selection([('c', 'Carpet'), ('l', 'Linoleum'), ('w', 'Wood')],string="Floor Type")
	
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
    ], string="Floor usage", help="The purpose of using the room", default='bedroom')
    
	
	surfacedise = fields.Float(string="Area of disinsection",compute="_compute_surface",  store=True) 	   
	
	@api.depends('surface', 'height', 'perimeter')
	def _compute_surface(self):
		for room in self:
			room.surfacedise = 2 * room.surface + room.height * room.perimeter
	
	def compute_count(self):
         for record in self:
            record.equipment_count = self.env['equipment.assets'].search_count(
                [('floors', '=', record.id)])   
	def compute_roomcount(self):
         for record in self:
            record.room_count = self.env['property.room'].search_count(
                [('floors', '=', record.id),('floor_type', '=', 'c')])        
	def compute_internalcount(self):
         for record in self:
            record.internal_count = self.env['property.room'].search_count(
                [('floors', '=', record.id),('floor_type', '=', 'l')])  
        
            
                 
	def open_createroom(self):
    		return {
                'name': ('Create Room'),
                'view_mode': 'form',
                'res_model': 'property.room',
                'type': 'ir.actions.act_window',
                #'target': 'new',
                'context': {
                    'default_propertys':self.propertys.id ,
                    'default_building_id':self.building_id.id ,
                    'default_floors':self.id ,
                    
                        },

                             }
      
      
	def show_equipment(self):
    	    return {
                 'name': "Equipment",
                 'domain': [('floors', '=', self.id)],
                'view_mode': 'kanban,tree,form',
                'res_model': 'equipment.assets',
                'view_type': 'form',
               'type': 'ir.actions.act_window',
                # 'context': 
                #         "{'default_res_model': '%s','default_res_id': %d}" ,
                             }     
	def show_internal(self):
    	    return {
                'name': "Internal Area",
                'domain': [('floors', '=', self.id), ('floor_type', '=', 'l')],
                'view_mode': 'kanban,tree,form',
                'res_model': 'property.room',
                'view_type': 'form',
               'type': 'ir.actions.act_window',
                'context': 
                        "{'search_default_building_id': 1}" ,
                             } 
         
class propertyroomlist(models.Model):
	_name = 'property.rooms.list'



	facilityname = fields.Many2one('facility.master',string='Facility Name', )	

	servicetype = fields.Many2one('service.providertype',string='Service Type' ,required=True)	

#	servicecategory = fields.Many2one('service.providertype.category',string='Service Category' ,required=True)
	roomlist = fields.Many2one('property.floors', string="Floor")

	serviceprovider = fields.Many2one('res.partner',string='Service Provider', domain=[('serviceprovider', '=', True)])

	# @api.onchange('servicetype')

	# def constrains_servicetype(self):

	#     return {'domain':{'servicecategory':[('id', '=', self.servicetype.servicecategory.id)]}}  
            
        
        
            

 
class floortypes(models.Model):
    _name = 'floor.types.list'
    
    name = fields.Char(string='Floor Type', )	


	