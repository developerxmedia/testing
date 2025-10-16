from odoo import fields, models, api, tools, _ 
from odoo.exceptions import ValidationError
from datetime import datetime
from io import BytesIO
import qrcode
import base64


class ProcessClassList(models.Model):
    _name = 'process.model'
    _rec_name = 'process_name'
    
    budget_ids = fields.Many2one('product.budget',string="Budget Id")
    process_name = fields.Many2one('process.product',string="Process")
    custom_list = fields.One2many('man.power.custom.list', 'man_power_id', string='Custom Lines', ondelete='cascade')
    fabrication_list= fields.One2many('product.fabrication.cost.list', 'ttproduct_fabrication_id_name', string='Fabrication', ondelete='cascade')
    material_list= fields.One2many('product.material.cost.list', 'product_material_id', string='Material', ondelete='cascade')
    tools_list= fields.One2many('main.tools.cost.list', 'main_tools_id', string='tool' , ondelete='cascade')
    equipment_list= fields.One2many('product.equipment.cost.list', 'product_equipment_id', string='equipment', ondelete='cascade')
    transport_list= fields.One2many('product.transport.cost.list', 'product_transport_id', string='transport', ondelete='cascade')
    third_party_list= fields.One2many('third.party.list.cost', 'product_third_party_id', string='third party', ondelete='cascade')
    
    
    cost_total=fields.Float(string='Man Sub Total' ,compute='onchan_func_lab_sec',store=True)
    cost_total_fabrication=fields.Float(string='Fabrication Sub Total' ,compute='fabrication_lines_func_lab_sec')
    cost_total_material=fields.Float(string='Material Sub Total' ,compute='material_lines_func_lab_sec')
    cost_total_tools=fields.Float(string='Tools Sub Total' ,compute='tools_lines_func_lab1_sec',store=True)
    cost_total_equipment=fields.Float(string='Eqipment Sub Total' ,compute='equipment_lines_func_lab_sec')
    cost_total_transport=fields.Float(string='Transport Sub Total' ,compute='transport_lines_func_lab_sec')
    cost_total_third=fields.Float(string='Third Party Sub Total' ,compute='third_party_func')
    # total_margin_percentage= fields.Float(string='Total Margin Percentage (%)', compute ='total_per_margins_per')
    
 

    @api.depends('custom_list')
    def onchan_func_lab_sec(self):
        for i in self:
            sums = 0.00
            for k in i.custom_list:
                sums += k.total_cost_1
            i.update({
                'cost_total':sums,
            })

    @api.depends('fabrication_list')
    def fabrication_lines_func_lab_sec(self):
        for i in self:
            sums = 0.00
            for k in i.fabrication_list:
                sums += k.amount_1
            i.update({
                'cost_total_fabrication':sums,
            })

    @api.depends('material_list')
    def material_lines_func_lab_sec(self):
        for i in self:
            sums = 0.00
            for k in i.material_list:
                sums += k.amount_1
            i.update({
                'cost_total_material':sums,
            })

    @api.depends('tools_list')
    def tools_lines_func_lab1_sec(self):
        for i in self:
            sums = 0.00
            for k in i.tools_list:
                sums += k.cost_1
            self.cost_total_tools = sums
            # i.update({
            #     'cost_total_tools':sums,
            # })

    @api.depends('equipment_list')
    def equipment_lines_func_lab_sec(self):
        for i in self:
            sums = 0.00
            for k in i.equipment_list:
                sums += k.total_cost_1
            i.update({
                'cost_total_equipment':sums,
            })

    @api.depends('transport_list')
    def transport_lines_func_lab_sec(self):
        for i in self:
            sums = 0.00
            for k in i.transport_list:
                sums += k.total_cost_1
            i.update({
                'cost_total_transport':sums,
            })    

    @api.depends('third_party_list')
    def third_party_func(self):
        for i in self:
            sums = 0.00
            for k in i.third_party_list:
                sums += k.total_third
            i.update({
                'cost_total_third':sums,
            })  
    
    cost_total_per =fields.Float(string='Man Sub Total' ,compute='onchan_func_lab')
    cost_total_fabrication_per =fields.Float(string='Fabrication Sub Total' ,compute='fabrication_lines_func_lab')
    cost_total_material_per =fields.Float(string='Material Sub Total' ,compute='material_lines_func_lab')
    cost_total_tools_per =fields.Float(string='Tools Sub Total' ,compute='tools_lines_func_lab')
    cost_total_equipment_per =fields.Float(string='Eqipment Sub Total' ,compute='equipment_lines_func_lab')
    cost_total_transport_per =fields.Float(string='Transport Sub Total' ,compute='transport_lines_func_lab')
    cost_all = fields.Float(string='Sub Total of All' ,compute='amount_all')
    
    @api.depends('cost_total_per','cost_total_fabrication_per','cost_total_material_per','cost_total_tools_per','cost_total_equipment_per','cost_total_transport_per')
    def amount_all(self):
        for rec in self:
            rec.cost_all = (rec.cost_total_per + rec.cost_total_fabrication_per + rec.cost_total_material_per + rec.cost_total_tools_per + rec.cost_total_equipment_per + rec.cost_total_transport_per)

    @api.depends('custom_list')
    def onchan_func_lab(self):
        for i in self:
            sums = 0.00
            for k in i.custom_list:
                sums += k.total_cost_without_per_1
            i.update({
                'cost_total_per':sums,
            })

    @api.depends('fabrication_list')
    def fabrication_lines_func_lab(self):
        for i in self:
            sums = 0.00
            for k in i.fabrication_list:
                sums += k.amount_without_per_1
            i.update({
                'cost_total_fabrication_per':sums,
            })

    @api.depends('material_list')
    def material_lines_func_lab(self):
        for i in self:
            sums = 0.00
            for k in i.material_list:
                sums += k.amount_without_per_1
            i.update({
                'cost_total_material_per':sums,
            })

    @api.depends('tools_list')
    def tools_lines_func_lab(self):
        for i in self:
            sums = 0.00
            for k in i.tools_list:
                sums += k.cost_without_per_1
            i.update({
                'cost_total_tools_per':sums,
            })

    @api.depends('equipment_list')
    def equipment_lines_func_lab(self):
        for i in self:
            sums = 0.00
            for k in i.equipment_list:
                sums += k.total_cost_without_per_1
            i.update({
                'cost_total_equipment_per':sums,
            })

    @api.depends('transport_list')
    def transport_lines_func_lab(self):
        for i in self:
            sums = 0.00
            for k in i.transport_list:
                sums += k.total_cost_without_per_1
            i.update({
                'cost_total_transport_per':sums,
            })

    def action_save_close_button(self):
        orm_many=self.env['product.budget'].search([('id', '=', self.budget_ids.id)],limit=1)
        orm_many.write({'target_ids':  [(4, self.id)]})
        return {'type': 'ir.actions.act_window_close'}

    def action_save_new_button(self):
        orm_many=self.env['product.budget'].search([('id', '=', self.budget_ids.id)],limit=1)
        orm_many.write({'target_ids':  [(4, self.id)]})
        return {
            'name': 'Wizard',
            'type': 'ir.actions.act_window',
            'res_model': 'process.model',
            'view_mode': 'form',
            'view_type': 'form',
            "context" : {
            'default_budget_ids' : self.budget_ids.id
                },
            'target': 'new',
            }

class ManPoweridList(models.Model):
    _name = 'man.power.custom.list'
    _description = 'Custom Lines for Bills of Material'

    
    process_man_1 = fields.Many2one('process.product',string='Process',compute="_sequence_ref_s",store=True)
    name_1 = fields.Many2one('man.power.category',string='Category')
    quantity_1 = fields.Float(string='Quantity')
    man_day_1 = fields.Float(string='Man day')
    total_1 = fields.Float(string='Total',readonly=False, compute='total_manpower_s',store=True)
    working_hours_per_day = fields.Float(string='Working hours per day',store=True)
    total_man_hours_1 = fields.Float(string='Total Man Hour', readonly=False,compute='amount_manpower_hours_s',store=True)
    rate_hour_1 = fields.Float(string='Rate/Hour', readonly=False)
    total_cost_1 = fields.Float(string='Total cost',readonly=False, compute='amount_manpower_s',store=True)
    total_cost_without_per_1 = fields.Float(string='Total cost Per',readonly=False, compute='amount_manpower_per_s',store=True)
    margin_amount_1= fields.Float(string='Margin percentage (%)')

    man_power_id = fields.Many2one('process.model', string='Bill of Material')
    
    @api.onchange('name_1')
    def rate_get(self):
        for rec in self:
            orm=self.env['man.power.category'].search([('man_power_category','=',rec.name_1.man_power_category)], limit=1)
            rec.rate_hour_1=orm.rate_hour

    @api.depends('man_power_id.custom_list')
    def _sequence_ref_s(self):
        for line in self:
            line.process_man_1 = line.man_power_id.process_name.id


    @api.depends('total_1','working_hours_per_day')
    def amount_manpower_hours_s(self):
        for rec in self:
            rec.total_man_hours_1=(rec.total_1 * rec.working_hours_per_day)

    @api.depends('total_man_hours_1','rate_hour_1')
    def amount_manpower_per_s(self):
        for rec in self:
            rec.total_cost_without_per_1 =(rec.total_man_hours_1 * rec.rate_hour_1)

    @api.depends('total_man_hours_1','rate_hour_1','margin_amount_1')
    def amount_manpower_s(self):
        for rec in self:
            amount=(rec.total_man_hours_1 * rec.rate_hour_1)
            a = amount/100
            b = rec.margin_amount_1 * a
            rec.total_cost_1=amount + b

    @api.depends('quantity_1','man_day_1')
    def total_manpower_s(self):
        for rec in self:
            rec.total_1=( rec.quantity_1 * rec.man_day_1)


class CustomFabricationProductList(models.Model):
    _name = 'product.fabrication.cost.list'
    _description = 'Custom Lines for Bills of Material og fabrication cost'

    process_fab_1 = fields.Many2one('process.product',string='Process',compute="_sequence_ref_s")
    process_fabrication_1= fields.Many2one('fabrication.process.category',string='Fabrication Process')
    process_1 = fields.Many2one('fabrication.process.category',string='Process')
    quantity_1 = fields.Float(string='Quantity')
    time_1 = fields.Float(string='Time')
    cost_1 = fields.Float(string='Cost', readonly=False)
    amount_1 = fields.Float(string='Amount', readonly=False, compute='amount_fabrication_s')
    amount_without_per_1 = fields.Float(string='Amount Per', readonly=False, compute='amount_fabrication_per_s')
    margin_amount_1= fields.Float(string='Margin percentage (%)')

    ttproduct_fabrication_id_name = fields.Many2one('process.model', string='Bill of Material')

    @api.onchange('process_1')
    def rate_get(self):
        for rec in self:
            orm=self.env['fabrication.process.category'].search([('fabrication_category','=',rec.process_1.fabrication_category)], limit=1)
            rec.cost_1=orm.rate_hour

    @api.depends('ttproduct_fabrication_id_name.fabrication_list')
    def _sequence_ref_s(self):
        for line in self:
            line.process_fab_1 = line.ttproduct_fabrication_id_name.process_name.id


    @api.depends('time_1','cost_1','margin_amount_1')
    def amount_fabrication_s(self):
        for rec in self:
            amount1=(rec.quantity_1 * rec.cost_1 * rec.time_1)
            a = amount1/100
            b = rec.margin_amount_1 * a
            rec.amount_1=amount1 + b

    @api.depends('time_1','cost_1')
    def amount_fabrication_per_s(self):
        for rec in self:
            rec.amount_without_per_1=(rec.quantity_1 * rec.cost_1 * rec.time_1)



class ProductMaterialList(models.Model):
    _name = 'product.material.cost.list'
    _description = 'Custom Lines for Bills of Material og material cost'

    process_mat_1 = fields.Many2one('process.product',string='Process',compute="_sequence_ref_s")
    description_1 = fields.Many2one('material.desription',string='Description')
    quantity_1 = fields.Float(string='Quantity')
    weight_No_1 = fields.Float(string='Weight/No')
    weight_1 = fields.Float(string='Weight', readonly=False, compute='amount_material_weight_s')
    cost_no_1 = fields.Float(string='Cost/No',readonly=False)
    amount_1 = fields.Float(string='Amount',readonly=False, compute='amount_material_s')
    amount_without_per_1 = fields.Float(string='Amount Per',readonly=False, compute='amount_material_per_s')
    margin_amount_1= fields.Float(string='Margin percentage (%)')

    product_material_id = fields.Many2one('process.model', string='Bill of Material')

    @api.onchange('description_1')
    def rate_get(self):
        for rec in self:
            orm=self.env['material.desription'].search([('material_description','=',rec.description_1.material_description)], limit=1)
            rec.cost_no_1=orm.cost


    @api.depends('product_material_id.material_list')
    def _sequence_ref_s(self):
        for line in self:
            line.process_mat_1 = line.product_material_id.process_name.id

    @api.depends('quantity_1','weight_No_1')
    def amount_material_weight_s(self):
        for rec in self:
            rec.weight_1=( rec.quantity_1 * rec.weight_No_1)

    @api.depends('quantity_1','weight_No_1','cost_no_1')
    def amount_material_per_s(self):
        for rec in self:
            rec.amount_without_per_1=( rec.quantity_1 * rec.cost_no_1)

    @api.depends('quantity_1','weight_No_1','cost_no_1','margin_amount_1')
    def amount_material_s(self):
        for rec in self:
            amount1=( rec.quantity_1 * rec.cost_no_1)
            a = amount1/100
            b = rec.margin_amount_1 * a
            rec.amount_1=amount1 + b


class MaintoolsList(models.Model):
    _name = 'main.tools.cost.list'
    _description = 'Custom Lines for Bills of Material og tools cost'

    process_tool_1 = fields.Many2one('process.product',string='Process',compute="_sequence_ref_s")
    description_1 = fields.Many2one('tools.desription',string='Description')
    rate = fields.Float(string='Cost before margin')
    cost_1 = fields.Float(string='Cost',readonly=False)
    cost_without_per_1 = fields.Float(string='Cost per',readonly=False)
    margin_amount_1= fields.Float(string='Margin percentage (%)')
    quantity_new = fields.Float(string='Quantity', default='1')

    main_tools_id = fields.Many2one('process.model', string='Bill of Material')

    @api.onchange('description_1')
    def rate_get(self):
        for rec in self:
            orm=self.env['tools.desription'].search([('tools_description','=',rec.description_1.tools_description)], limit=1)
            rec.rate=orm.cost

    @api.depends('main_tools_id.tools_list')
    def _sequence_ref_s(self):
        for line in self:
            line.process_tool_1 = line.main_tools_id.process_name.id

    @api.onchange('margin_amount_1')
    def tool_product_one_per_s(self):
        # for rec in self:
        a = self.rate/100
        b = self.margin_amount_1 * a
        stock = self.rate+b
        self.cost_1 = stock
        
    @api.onchange('rate')
    def _sequence_cost_s(self):
        self.cost_1 = self.rate * self.quantity_new



class ProductequipmentList(models.Model):
    _name = 'product.equipment.cost.list'
    _description = 'Custom Lines for Bills of Material og equipment cost'

    process_equ_1 = fields.Many2one('process.product',string='Process',compute="_sequence_ref_s")
    types_of_equipment_1 = fields.Many2one('equipment.desription',string='Types Of Equipment')
    man_day_1 = fields.Float(string='Man day')
    rate_man_day_1 = fields.Float(string='Rate/Man Day', readonly=False)
    total_cost_1 = fields.Float(string='Total Cost', readonly=False, compute='amount_equipment_s')
    total_cost_without_per_1 = fields.Float(string='Total Cost Per', readonly=False, compute='amount_equipment_per_s')
    margin_amount_1= fields.Float(string='Margin percentage (%)')

    product_equipment_id = fields.Many2one('process.model', string='Bill of Material')

    @api.onchange('types_of_equipment_1')
    def rate_get(self):
        for rec in self:
            orm=self.env['equipment.desription'].search([('types_of_equipment','=',rec.types_of_equipment_1.types_of_equipment)], limit=1)
            rec.rate_man_day_1=orm.rate_hour

    @api.depends('product_equipment_id.equipment_list')
    def _sequence_ref_s(self):
        for line in self:
            line.process_equ_1 = line.product_equipment_id.process_name.id

    @api.depends('man_day_1','rate_man_day_1','margin_amount_1')
    def amount_equipment_s(self):
        for rec in self:
            amount1=( rec.man_day_1 * rec.rate_man_day_1)
            a = amount1/100
            b = rec.margin_amount_1 * a
            rec.total_cost_1=amount1 + b

    @api.depends('man_day_1','rate_man_day_1')
    def amount_equipment_per_s(self):
        for rec in self:
            rec.total_cost_without_per_1=( rec.man_day_1 * rec.rate_man_day_1)

class ProducttransportList(models.Model):
    _name = 'product.transport.cost.list'
    _description = 'Custom Lines for Bills of Material og transport cost'

    process_trans_1 = fields.Many2one('process.product',string='Process',compute="_sequence_ref_s")
    types_of_transport_1 = fields.Many2one('transport.desription',string='Types Of Transport')
    man_day_1 = fields.Float(string='Man day')
    rate_man_day_1 = fields.Float(string='Rate/Man Day', readonly=False)
    total_cost_1 = fields.Float(string='Total Cost', readonly=False, compute='amount_transport_s')
    total_cost_without_per_1 = fields.Float(string='Total Cost Per', readonly=False, compute='amount_transport_per_s')
    margin_amount_1= fields.Float(string='Margin percentage (%)')

    product_transport_id = fields.Many2one('process.model', string='Bill of Material')

    @api.onchange('types_of_transport_1')
    def rate_get(self):
        for rec in self:
            orm=self.env['transport.desription'].search([('types_of_transport','=',rec.types_of_transport_1.types_of_transport)], limit=1)
            rec.rate_man_day_1=orm.rate_hour

    @api.depends('product_transport_id.transport_list')
    def _sequence_ref_s(self):
        for line in self:
            line.process_trans_1 = line.product_transport_id.process_name.id

    @api.depends('man_day_1','rate_man_day_1','margin_amount_1')
    def amount_transport_s(self):
        for rec in self:
            amount1=( rec.man_day_1 * rec.rate_man_day_1)
            a = amount1/100
            b = rec.margin_amount_1 * a
            rec.total_cost_1=amount1 + b

    @api.depends('man_day_1','rate_man_day_1')
    def amount_transport_per_s(self):
        for rec in self:
            rec.total_cost_without_per_1=( rec.man_day_1 * rec.rate_man_day_1)

class thirdParty(models.Model):
    _name = 'third.party.list.cost'
    _description = 'Custom Lines for Bills of Material'

    
    process_third_party = fields.Many2one('process.product',string='Process',compute="_sequence_ref_s",store=True)
    category_third = fields.Char(string='Category')
    quantity_third = fields.Float(string='Quantity')
    cost_day_third = fields.Float(string='Cost per day')
    total_third = fields.Float(string='Total',readonly=False, compute='total_third_party',store=True)

    product_third_party_id = fields.Many2one('process.model', string='Bill of Material')

    @api.depends('quantity_third','cost_day_third')
    def total_third_party(self):
        for rec in self:
            rec.total_third=( rec.quantity_third * rec.cost_day_third)

    @api.depends('product_third_party_id.third_party_list')
    def _sequence_ref_s(self):
        for line in self:
            line.process_third_party = line.product_third_party_id.process_name.id

