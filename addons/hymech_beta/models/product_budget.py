from odoo import fields, models, api, tools, _ 
from odoo.exceptions import ValidationError
from datetime import datetime
from io import BytesIO
import qrcode
import base64

class ProductBudget(models.Model):
    _name = 'product.budget'
    _description = 'Product budget'
    _rec_name ='product_name'

    # product_id = fields.Many2one('product.product',string='Product',required=True)
    
    # product_name= fields.Char(string='Product Name')

    product_name = fields.Many2one('product.product',string='Product')
    price = fields.Float(string='Price', compute='amount_price')

    custom_liness = fields.One2many('man.power.custom.line', 'man_power_id', string='Custom Lines')
    fabrication_lines= fields.One2many('product.fabrication.cost.line', 'ttproduct_fabrication_id_name', string='Fabrication')
    material_lines= fields.One2many('product.material.cost.line', 'product_material_id', string='Material')
    tools_lines= fields.One2many('main.tools.cost.line', 'main_tools_id', string='tool')
    equipment_lines= fields.One2many('product.equipment.cost.line', 'product_equipment_id', string='equipment')
    transport_lines= fields.One2many('product.transport.cost.line', 'product_transport_id', string='transport')

    sum_of_total=fields.Float(string='Sub Total' ,compute='onchan_func_lab')
    sum_of_total_fabrication=fields.Float(string='Sub Total' ,compute='fabrication_lines_func_lab')
    sum_of_total_material=fields.Float(string='Sub Total' ,compute='material_lines_func_lab')
    sum_of_total_tools=fields.Float(string='Sub Total' ,compute='tools_lines_func_lab')
    sum_of_total_equipment=fields.Float(string='Sub Total' ,compute='equipment_lines_func_lab')
    sum_of_total_transport=fields.Float(string='Sub Total' ,compute='transport_lines_func_lab')

    @api.depends('sum_of_total','sum_of_total_fabrication','sum_of_total_material','sum_of_total_tools','sum_of_total_equipment','sum_of_total_transport')
    def amount_price(self):
        for rec in self:
            rec.price = (rec.sum_of_total + rec.sum_of_total_fabrication + rec.sum_of_total_material + rec.sum_of_total_tools + rec.sum_of_total_equipment + rec.sum_of_total_transport)


    @api.depends('custom_liness')
    def onchan_func_lab(self):
        for i in self:
            sums = 0.00
            for k in i.custom_liness:
                sums += k.total_cost
            i.update({
                'sum_of_total':sums,
            })

    @api.depends('fabrication_lines')
    def fabrication_lines_func_lab(self):
        for i in self:
            sums = 0.00
            for k in i.fabrication_lines:
                sums += k.amount
            i.update({
                'sum_of_total_fabrication':sums,
            })

    @api.depends('material_lines')
    def material_lines_func_lab(self):
        for i in self:
            sums = 0.00
            for k in i.material_lines:
                sums += k.amount
            i.update({
                'sum_of_total_material':sums,
            })

    @api.depends('tools_lines')
    def tools_lines_func_lab(self):
        for i in self:
            sums = 0.00
            for k in i.tools_lines:
                sums += k.cost
            i.update({
                'sum_of_total_tools':sums,
            })

    @api.depends('equipment_lines')
    def equipment_lines_func_lab(self):
        for i in self:
            sums = 0.00
            for k in i.equipment_lines:
                sums += k.total_cost
            i.update({
                'sum_of_total_equipment':sums,
            })

    @api.depends('transport_lines')
    def transport_lines_func_lab(self):
        for i in self:
            sums = 0.00
            for k in i.transport_lines:
                sums += k.total_cost
            i.update({
                'sum_of_total_transport':sums,
            })

class ManPowerid(models.Model):
    _name = 'man.power.custom.line'
    _description = 'Custom Lines for Bills of Material'

    name_man_power_rec= fields.Char(string='ff')
    name = fields.Many2one('man.power.category',string='Category')
    quantity = fields.Float(string='Quantity')
    man_day = fields.Float(string='Man day')
    total = fields.Float(string='Total')
    total_man_hours = fields.Float(string='Total Man Hour')
    rate_hour = fields.Float(string='Rate/Hour', compute='man_product_one')
    total_cost = fields.Float(string='Total cost', compute='amount_manpower')


    man_power_id = fields.Many2one('product.budget', string='Bill of Material')

    @api.depends('quantity','man_day','total_man_hours','rate_hour')
    def amount_manpower(self):
        for rec in self:
            rec.total_cost=( rec.quantity * rec.man_day * rec.total_man_hours * rec.rate_hour)

    @api.depends('name')
    def man_product_one(self):
        for rec in self:
            orm=self.env['man.power.category'].search([('man_power_category','=',rec.name.man_power_category)], limit=1)

            rec.rate_hour=orm.rate_hour

class CustomFabricationProduct(models.Model):
    _name = 'product.fabrication.cost.line'
    _description = 'Custom Lines for Bills of Material og fabrication cost'

    process_fabrication= fields.Many2one('fabrication.process.category',string='Process')
    process = fields.Many2one('fabrication.process.category',string='Process')
    quantity = fields.Float(string='Quantity')
    time = fields.Float(string='Time')
    cost = fields.Float(string='Cost', compute='fabrication_product_one')
    amount = fields.Float(string='Amount', compute='amount_fabrication')

    ttproduct_fabrication_id_name = fields.Many2one('product.budget', string='Bill of Material')

    @api.depends('quantity','time','cost')
    def amount_fabrication(self):
        for rec in self:
            rec.amount=( rec.quantity * rec.cost * rec.time)

    @api.depends('process')
    def fabrication_product_one(self):
        for rec in self:
            orm=self.env['fabrication.process.category'].search([('fabrication_category','=',rec.process.fabrication_category)], limit=1)

            rec.cost=orm.rate_hour

class ProductMaterialLine(models.Model):
    _name = 'product.material.cost.line'
    _description = 'Custom Lines for Bills of Material og material cost'

    description = fields.Many2one('material.desription',string='Description')
    quantity = fields.Float(string='Quantity')
    weight_No = fields.Float(string='Weight/No')
    weight = fields.Float(string='Weight')
    cost_no = fields.Float(string='Cost/No', compute='material_product_one')
    amount = fields.Float(string='Amount', compute='amount_material')


    product_material_id = fields.Many2one('product.budget', string='Bill of Material')

    @api.depends('quantity','weight_No','cost_no')
    def amount_material(self):
        for rec in self:
            rec.amount=( rec.quantity * rec.weight_No * rec.cost_no)

    @api.depends('description')
    def material_product_one(self):
        for rec in self:
            orm=self.env['material.desription'].search([('material_description','=',rec.description.material_description)], limit=1)

            rec.cost_no=orm.cost

class MaintoolsLine(models.Model):
    _name = 'main.tools.cost.line'
    _description = 'Custom Lines for Bills of Material og tools cost'

    description = fields.Many2one('tools.desription',string='Description')
    cost = fields.Float(string='Cost', compute='tool_product_one')

    main_tools_id = fields.Many2one('product.budget', string='Bill of Material')

    @api.depends('description')
    def tool_product_one(self):
        for rec in self:
            orm=self.env['tools.desription'].search([('tools_description','=',rec.description.tools_description)], limit=1)

            rec.cost=orm.cost




class ProductequipmentLine(models.Model):
    _name = 'product.equipment.cost.line'
    _description = 'Custom Lines for Bills of Material og equipment cost'

    types_of_equipment = fields.Many2one('equipment.desription',string='Types Of Equipment')
    # quantity = fields.Float(string='Quantity')
    man_day = fields.Float(string='Man day')
    rate_man_day = fields.Float(string='Rate/Man Day', compute='equipment_product_one')
    total_cost = fields.Float(string='Total Cost', compute='amount_equipment')

    product_equipment_id = fields.Many2one('product.budget', string='Bill of Material')

    @api.depends('man_day','rate_man_day')
    def amount_equipment(self):
        for rec in self:
            rec.total_cost=( rec.man_day * rec.rate_man_day)

    @api.depends('types_of_equipment')
    def equipment_product_one(self):
        for rec in self:
            orm=self.env['equipment.desription'].search([('types_of_equipment','=',rec.types_of_equipment.types_of_equipment)], limit=1)

            rec.rate_man_day=orm.rate_hour

class ProducttransportLine(models.Model):
    _name = 'product.transport.cost.line'
    _description = 'Custom Lines for Bills of Material og transport cost'

    types_of_transport = fields.Many2one('transport.desription',string='Types Of Transport')
    # quantity = fields.Float(string='Quantity')
    man_day = fields.Float(string='Man day')
    rate_man_day = fields.Float(string='Rate/Man Day', compute='transport_product_one')
    total_cost = fields.Float(string='Total Cost', compute='amount_transport')



    product_transport_id = fields.Many2one('product.budget', string='Bill of Material')

    @api.depends('man_day','rate_man_day')
    def amount_transport(self):
        for rec in self:
            rec.total_cost=( rec.man_day * rec.rate_man_day)

    @api.depends('types_of_transport')
    def transport_product_one(self):
        for rec in self:
            orm=self.env['transport.desription'].search([('types_of_transport','=',rec.types_of_transport.types_of_transport)], limit=1)

            rec.rate_man_day=orm.rate_hour




