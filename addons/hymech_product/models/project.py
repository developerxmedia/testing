from odoo import fields, models, api, tools, _ 
from odoo.exceptions import ValidationError
from datetime import datetime
from io import BytesIO
import qrcode
import base64

class inherit_project_new(models.Model):
    _inherit = 'project.project'

    price = fields.Float(string='Spent Amount',readonly=False, compute='amount_price' ,store='True')
    doc_count=fields.Char(string='doc count')

    man_custom_lines = fields.One2many('project.man.power.custom.line', 'project_man_power_id', string='Custom Lines')
    project_fabrication_lines= fields.One2many('project.fabrication.cost.line', 'fabrication_id_name', string='Fabrication')
    project_material_lines= fields.One2many('project.material.cost.line', 'material_id', string='Material')
    project_tools_lines= fields.One2many('project.main.tools.cost.line', 'main_tools_project_id', string='tool')
    project_equipment_lines= fields.One2many('project.equipment.cost.line', 'equipment_id', string='equipment')
    project_transport_lines= fields.One2many('project.transport.cost.line', 'transport_id', string='transport')


    project_sum_of_total=fields.Float(string='Man Sub Total' ,compute='onchan_func_lab')
    sum_of_total_fabrication=fields.Float(string='Fabrication Sub Total' ,compute='fabrication_lines_func_lab')
    sum_of_total_material=fields.Float(string='Material Sub Total' ,compute='material_lines_func_lab')
    sum_of_total_tools=fields.Float(string='Tools Sub Total' ,compute='tools_lines_func_lab')
    sum_of_total_equipment=fields.Float(string='Equipment Sub Total' ,compute='equipment_lines_func_lab')
    sum_of_total_transport=fields.Float(string='Transport Sub Total' ,compute='transport_lines_func_lab')

    end_date= fields.Date(string='End Date')
    
    @api.depends('project_sum_of_total','sum_of_total_fabrication','sum_of_total_material','sum_of_total_tools','sum_of_total_equipment','sum_of_total_transport')
    def amount_price(self):
        for rec in self:
            rec.price = (rec.project_sum_of_total + rec.sum_of_total_fabrication + rec.sum_of_total_material + rec.sum_of_total_tools + rec.sum_of_total_equipment + rec.sum_of_total_transport)

    @api.depends('man_custom_lines')
    def onchan_func_lab(self):
        for i in self:
            sums = 0.00
            for k in i.man_custom_lines:
                sums += k.project_total_cost
            i.update({
                'project_sum_of_total':sums,
            })

    @api.depends('project_fabrication_lines')
    def fabrication_lines_func_lab(self):
        for i in self:
            sums = 0.00
            for k in i.project_fabrication_lines:
                sums += k.amount
            i.update({
                'sum_of_total_fabrication':sums,
            })

    @api.depends('project_material_lines')
    def material_lines_func_lab(self):
        for i in self:
            sums = 0.00
            for k in i.project_material_lines:
                sums += k.amount
            i.update({
                'sum_of_total_material':sums,
            })

    @api.depends('project_tools_lines')
    def tools_lines_func_lab(self):
        for i in self:
            sums = 0.00
            for k in i.project_tools_lines:
                sums += k.cost
            i.update({
                'sum_of_total_tools':sums,
            })

    @api.depends('project_equipment_lines')
    def equipment_lines_func_lab(self):
        for i in self:
            sums = 0.00
            for k in i.project_equipment_lines:
                sums += k.total_cost
            i.update({
                'sum_of_total_equipment':sums,
            })

    @api.depends('project_transport_lines')
    def transport_lines_func_lab(self):
        for i in self:
            sums = 0.00
            for k in i.project_transport_lines:
                sums += k.total_cost
            i.update({
                'sum_of_total_transport':sums,
            })

class ManPoweridnew(models.Model):
    _name = 'project.man.power.custom.line'
    _description = 'Custom Lines for Bills of Material'

    
    # name_man_power_rec= fields.Char(string='ff')
    project_process_man = fields.Many2one('process.product',string='Process')
    project_name1 = fields.Many2one('man.power.category',string='Category')
    project_quantity = fields.Float(string='Quantity')
    project_man_day = fields.Float(string='Man day')
    project_total = fields.Float(string='Total',readonly=False, compute='total_manpower')
    project_total_man_hours = fields.Float(string='Total Man Hour', readonly=False,compute='amount_manpower_hours')
    project_rate_hour = fields.Float(string='Rate/Hour', readonly=False, compute='man_product_one')
    project_total_cost = fields.Float(string='Total cost',readonly=False, compute='amount_manpower')


    project_man_power_id = fields.Many2one('project.project', ondelete='cascade', string='Bill of Material')

    @api.depends('project_total')
    def amount_manpower_hours(self):
        for rec in self:
            orm=self.env['man.power.category'].search([('man_power_category','=',rec.project_name1.man_power_category)], limit=1)
            a=orm.work_hourss
            rec.project_total_man_hours=(rec.project_total * a)

    @api.depends('project_total_man_hours','project_rate_hour')
    def amount_manpower(self):
        for rec in self:
            rec.project_total_cost=(rec.project_total_man_hours * rec.project_rate_hour)

    @api.depends('project_quantity','project_man_day')
    def total_manpower(self):
        for rec in self:
            rec.project_total=( rec.project_quantity * rec.project_man_day)

    @api.depends('project_name1')
    def man_product_one(self):
        for rec in self:
            orm=self.env['man.power.category'].search([('man_power_category','=',rec.project_name1.man_power_category)], limit=1)

            rec.project_rate_hour=orm.rate_hour

class CustomFabricationProductnew(models.Model):
    _name = 'project.fabrication.cost.line'
    _description = 'Custom Lines for Bills of Material og fabrication cost'

    process_fab = fields.Many2one('process.product',string='Process')
    process_fabrication= fields.Many2one('fabrication.process.category',string='Fabrication Process')
    process = fields.Many2one('fabrication.process.category',string='Process')
    quantity = fields.Float(string='Quantity')
    time = fields.Float(string='Time')
    cost = fields.Float(string='Cost', readonly=False, compute='fabrication_product_one')
    amount = fields.Float(string='Amount', readonly=False, compute='amount_fabrication')

    fabrication_id_name = fields.Many2one('project.project',ondelete='cascade', string='Bill of Material')

    @api.depends('time','cost')
    def amount_fabrication(self):
        for rec in self:
            rec.amount=( rec.cost * rec.time)

    @api.depends('process')
    def fabrication_product_one(self):
        for rec in self:
            orm=self.env['fabrication.process.category'].search([('fabrication_category','=',rec.process.fabrication_category)], limit=1)

            rec.cost=orm.rate_hour

class ProductMaterialLinenew(models.Model):
    _name = 'project.material.cost.line'
    _description = 'Custom Lines for Bills of Material og material cost'

    process_mat = fields.Many2one('process.product',string='Process')
    description = fields.Many2one('material.desription',string='Description')
    quantity = fields.Float(string='Quantity')
    weight_No = fields.Float(string='Weight/No')
    weight = fields.Float(string='Weight', readonly=False, compute='amount_material_weight')
    cost_no = fields.Float(string='Cost/No',readonly=False, compute='material_product_one')
    amount = fields.Float(string='Amount',readonly=False, compute='amount_material')


    material_id = fields.Many2one('project.project', ondelete='cascade', string='Bill of Material')

    @api.depends('quantity','weight_No')
    def amount_material_weight(self):
        for rec in self:
            rec.weight=( rec.quantity * rec.weight_No)

    @api.depends('quantity','weight_No','cost_no')
    def amount_material(self):
        for rec in self:
            rec.amount=( rec.quantity * rec.cost_no)

    @api.depends('description')
    def material_product_one(self):
        for rec in self:
            orm=self.env['material.desription'].search([('material_description','=',rec.description.material_description)], limit=1)

            rec.cost_no=orm.cost

class MaintoolsLinenew(models.Model):
    _name = 'project.main.tools.cost.line'
    _description = 'Custom Lines for Bills of Material og tools cost'

    process_tool = fields.Many2one('process.product',string='Process')
    description = fields.Many2one('tools.desription',string='Description')
    cost = fields.Float(string='Cost',readonly=False, compute='tool_product_one')

    main_tools_project_id = fields.Many2one('project.project', ondelete='cascade', string='Bill of Material')

    @api.depends('description')
    def tool_product_one(self):
        for rec in self:
            orm=self.env['tools.desription'].search([('tools_description','=',rec.description.tools_description)], limit=1)
            rec.cost=orm.cost

class ProductequipmentLinenew(models.Model):
    _name = 'project.equipment.cost.line'
    _description = 'Custom Lines for Bills of Material og equipment cost'

    process_equ = fields.Many2one('process.product',string='Process')
    types_of_equipment = fields.Many2one('equipment.desription',string='Types Of Equipment')
    # quantity = fields.Float(string='Quantity')
    man_day = fields.Float(string='Man day')
    rate_man_day = fields.Float(string='Rate/Man Day', readonly=False, compute='equipment_product_one')
    total_cost = fields.Float(string='Total Cost', readonly=False, compute='amount_equipment')

    equipment_id = fields.Many2one('project.project', ondelete='cascade',  string='Bill of Material')

    @api.depends('man_day','rate_man_day')
    def amount_equipment(self):
        for rec in self:
            rec.total_cost=( rec.man_day * rec.rate_man_day)

    @api.depends('types_of_equipment')
    def equipment_product_one(self):
        for rec in self:
            orm=self.env['equipment.desription'].search([('types_of_equipment','=',rec.types_of_equipment.types_of_equipment)], limit=1)

            rec.rate_man_day=orm.rate_hour

class ProducttransportLinenew(models.Model):
    _name = 'project.transport.cost.line'
    _description = 'Custom Lines for Bills of Material og transport cost'

    process_trans = fields.Many2one('process.product',string='Process')
    types_of_transport = fields.Many2one('transport.desription',string='Types Of Transport')
    # quantity = fields.Float(string='Quantity')
    man_day = fields.Float(string='Man day')
    rate_man_day = fields.Float(string='Rate/Man Day', readonly=False, compute='transport_product_one')
    total_cost = fields.Float(string='Total Cost', readonly=False, compute='amount_transport')



    transport_id = fields.Many2one('project.project', ondelete='cascade', string='Bill of Material')

    @api.depends('man_day','rate_man_day')
    def amount_transport(self):
        for rec in self:
            rec.total_cost=( rec.man_day * rec.rate_man_day)

    @api.depends('types_of_transport')
    def transport_product_one(self):
        for rec in self:
            orm=self.env['transport.desription'].search([('types_of_transport','=',rec.types_of_transport.types_of_transport)], limit=1)

            rec.rate_man_day=orm.rate_hour


