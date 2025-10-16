# -*- coding: utf-8 -*-
# ©  2015-2019 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


from odoo import models, fields, tools, api
from datetime import datetime
from odoo.modules import get_module_resource
import base64

class PropertyLand(models.Model):
    _name = 'property.land'
    _description = "Land"
    _inherit = 'property.property'

#    location_type = fields.Selection([('I', 'Intravilan'), ('E', 'Extravilan')], default='E')

    propertytype = fields.Many2one('property.types',string="Property Type")  # required=True)
    property_name =fields.Char('Property Name') 
    new_property = fields.Char('New Property Name')
    priority = fields.Selection([('1', 'Low'), ('2', 'Medium'),('3', 'High')])


    space_count = fields.Integer(compute='compute_spacecount')
    count = fields.Integer()
    buildings_count = fields.Integer(compute='compute_buildingscount')
    floors_count = fields.Integer(compute='compute_floorscount')
    rooms_count = fields.Integer(compute='compute_roomscount')
    equipment_count = fields.Integer(compute='compute_count')

    # countfloor = fields.Integer(compute='compute_floor')
 
    # countroom = fields.Integer(compute='compute_room')       
    #propertyline = fields.One2many('master.property.line','propertyline',string="Property Name")
    propertyline = fields.One2many('master.property.line', 'property_id', string="Property Name")
    inspectionline = fields.One2many('inspection.land.line','inspectiontype',string="inspection Line")
    facilityline  = fields.One2many('property.land.line','facility',string="facility Line")# required=True)    
#    parcela = fields.Char(string="parcela cadastrală")
#    sector = fields.Char(string="Sector cadastral")
#    bloc_fizic = fields.Char(string="Nr bloc fizic")

#    carte = fields.Char(string="Carte funciară")
#    utr = fields.Char(string="UTR")
#    categ_id = fields.Many2one('property.land.categ', string="Category")


#    cod = fields.Char()

    # def compute_count(self):
    #     for record in self:
    #         record.count = self.env['master.property.line'].search_count([('propertyline', '=', self.id)]) 

    # def compute_floor(self):
    #     for record in self:
    #         record.countfloor = self.env['master.property.line'].search_count([('propertyline', '=', self.id)]) 

    # def compute_room(self):
    #     for record in self:
    #         record.countroom = self.env['master.property.line'].search_count([('propertyline', '=', self.id)]) 
    @api.model
    def create(self, vals):
        result = super(PropertyLand, self).create( vals) 
                       
        result.new_property = result.name
        
        return result
    @api.constrains('name')
    def save_new_name(self):
        if self.name:
            self.new_property = self.name
        else:
            pass                

    def compute_buildingscount(self):
        for record in self:
            record.buildings_count = self.env['property.building'].search_count(
                [('propertyname', '=', record.id)])       
    def compute_floorscount(self):
        for record in self:
            record.floors_count = self.env['property.floors'].search_count(
                [('propertys', '=', record.id)])         
    def compute_roomscount(self):
        for record in self:
            record.rooms_count = self.env['property.room'].search_count(
                [('propertys', '=', record.id),('floor_type', '=', 'c')])                   
    def compute_count(self):
        for record in self:
            record.equipment_count = self.env['equipment.assets'].search_count(
                [('propertys', '=', record.id)]) 
            
    def compute_spacecount(self):
        for record in self:
            record.space_count = self.env['property.room'].search_count(
                [('propertys', '=', record.id), ('floor_type', '=', 'l')])   
             
    def show_building(self):

        return {
                'name': "Buildings",
                'domain': [('propertyname', '=', self.id)],
                'view_mode': 'kanban,tree,form',
                'res_model': 'property.building',
                'view_type': 'form',
               'type': 'ir.actions.act_window',
                # 'context': 
                #         "{'default_res_model': '%s','default_res_id': %d}" ,
                             }
        

    def show_floor(self):

        return {
                'name': "Floors",
                'domain': [('propertys', '=', self.id)],
                'view_mode': 'kanban,tree,form',
                'res_model': 'property.floors',
                'view_type': 'form',
               'type': 'ir.actions.act_window',
                'context': 
                        "{'search_default_building_id':1}" ,
                             }
    def show_equipment(self):

        return {
                'name': "Equipment",
                 'domain': [('propertys', '=', self.id)],
                'view_mode': 'kanban,tree,form',
                'res_model': 'equipment.assets',
                'view_type': 'form',
               'type': 'ir.actions.act_window',
                # 'context': 
                #         "{'default_res_model': '%s','default_res_id': %d}" ,
                             }     

    def show_room(self):

        return {
                'name': "Rooms",
                 'domain': [('propertys', '=', self.id), ('floor_type', '=', 'c')],
                'view_mode': 'kanban,tree,form',
                'res_model': 'property.room',
                'view_type': 'form',
               'type': 'ir.actions.act_window',
                'context': 
                        "{'search_default_building_id': 1}" ,
                             }  
                 
    def show_space(self):
        domain = [('propertys', '=', self.id), ('floor_type', '=', 'l')]
    
        return {
                'name': "Space",
                 'domain': domain,
                'view_mode': 'kanban,tree,form',
                'res_model': 'property.room',
                'view_type': 'form',
               'type': 'ir.actions.act_window',
                'context': 
                        "{'search_default_building_id': 1}" ,
                             }  
                

    def open_create(self):
        view_id = self.env.ref('deltatech_property.view_property_building_form').id
        target = self.env['property.land'].browse(self.name)
        return {
                'name': ('Create Building'),
                'view_mode': 'form',
                'res_model': 'property.building',
                'views': [(view_id, 'form')],
                'view_id': view_id,
                'type': 'ir.actions.act_window',
               # 'target': 'new',
                'context': {
                    'default_propertyname':self.id ,
                    'default_street':self.street ,
                            
                        },

                             }    
   
                


    # @api.model_create_multi
    # def create(self, vals_list):
    #     if self.env.context.get('import_file'):
    #         self._check_import_consistency(vals_list)
    #     for vals in vals_list:
    #         if not vals.get('image'):
    #             vals['image'] = self._get_default_image()
    #         tools.image_resize_images(vals, sizes={'image': (1024, None)})

    #     buildings = super(PropertyLand, self).create(vals_list)

    #     return buildings


    # @api.model
    # def _get_default_image(self):
    #     if self._context.get('install_mode'):
    #         return False

    #     colorize, img_path, image = False, False, False

    #     img_path = get_module_resource('deltatech_property', 'static/src/img', 'land.png')
    #     colorize = True

    #     if img_path:
    #         with open(img_path, 'rb') as f:
    #             image = f.read()
    #     if image and colorize:
    #         image = tools.image_colorize(image)

    #     return tools.image_resize_image_big(base64.b64encode(image))

class PropertyLandlist(models.Model):
    _name = 'property.land.line'


    name = fields.Many2one('facility.master',string="Facility Name") 

    servicetype = fields.Many2one('service.providertype',string='Service Type', required=True)	

    # servicecategory = fields.Many2one('service.providertype.category',string='Service Category', required=True)

    facility = fields.Many2one('property.land',string="Property Name ")   
    # @api.onchange('servicetype')
    # def constrains_servicetype(self):
    #     return {'domain':{'servicecategory':[('id', '=', self.servicetype.servicecategory.id)]}}
    
class inspectionLandlist(models.Model):
    _name = 'inspection.land.line'


#    name = fields.Char(string="
# ") 
    checkcategory = fields.Char(string="Check List Category ")  
    checktypes = fields.Char(string="Check List Type") 
    inspectiontype = fields.Many2one('property.land',string="Property Name ")     
    
    # @api.onchange('checkcategory')
    # def constrains_checkcategory(self):
    #     return {'domain':{'checktypes':[('id', '=', self.checkcategory.checklisttypes.ids)]}}
	
	
			      