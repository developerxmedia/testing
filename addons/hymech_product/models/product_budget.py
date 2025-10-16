from odoo import fields, models, api, tools, _ 
from odoo.exceptions import ValidationError
from datetime import datetime
from io import BytesIO
import qrcode
import base64

class ProductBudget(models.Model):
    _name = 'product.budget'
    _description = 'Product budget'
    _rec_name ='boq_project'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    product_name= fields.Many2one('product.product', string='Product Name')
    product_new_id= fields.Many2one('product.product', string='Product Name', required=True,store= True)
    price = fields.Float(string='Price',readonly=False, compute='amount_price',store= True)

    price_per = fields.Float(string='Price',readonly=False, compute='amount_price_per',default=0)
    sub_total_per= fields.Float(string='Total Price', readonly=False, compute='amount_price_subtotal_per',default=0)

    sub_total= fields.Float(string='Total Price', readonly=False, compute='amount_price_subtotal',default=0 , store=True)
    sub_total_product = fields.Float(string='Total Price', readonly=False)
    boq_attachment = fields.Integer(string='Attachment', compute='boq_attachment_fun')


    process_count_id = fields.Integer(string='Process', compute='count_process_id')
    target_ids = fields.Many2many('process.model', string='Targets',domain ="[('budget_ids','=',id)]")
    boq_project = fields.Char(string="BOQ Number", readonly=True, required=True,
                             copy=False, index=True, default=lambda self:_('New'))
    
    def button_one2many_process(self):
        return {
        'name': 'Process Selection',
        'type': 'ir.actions.act_window',
        'res_model': 'process.model',
        'view_mode': 'form',
        'view_type': 'form',
        "context" : {
            'default_budget_ids' : self.id
        },
        'target': 'new',
        }
        
    @api.model
    def create(self, values):
        if values.get('boq_project', _('New')) == _('New'):
            values['boq_project'] = self.env['ir.sequence'].next_by_code('product.budget') or _('New')
        result = super(ProductBudget, self).create(values)
        return result
    
    
    def count_process_id(self):
        for rec in self:
            rec.process_count_id = self.env['process.model'].search_count([('budget_ids', '=', self.id)])
        orm = self.env['process.model'].search([('budget_ids','=',self.id)])
        if orm:
            k = 0
            l = 0
            m = 0
            n = 0
            o = 0
            p = 0 
            q = 0
            sums = 0
            mech = 0
            for rec in orm:
                mech += rec.cost_all
                sums += rec.cost_total

                y = rec.cost_total_fabrication
                addition_fabrication = l + y
                l = addition_fabrication
                
                x = rec.cost_total_material
                addition_material = m + x
                m = addition_material
                
                w = rec.cost_total_tools
                addition_tools = n + w
                n = addition_tools
                
                v = rec.cost_total_equipment
                addition_equipment = o + v
                o = addition_equipment

                u = rec.cost_total_transport
                addition_transport = p + u
                p = addition_transport

                h = rec.cost_total_third
                addition_third_party = q + h
                q = addition_third_party

            self.price_per = mech
            self.sum_of_total = sums
            self.sum_of_total_fabrication = addition_fabrication
            self.sum_of_total_material = addition_material
            self.sum_of_total_tools = addition_tools
            self.sum_of_total_equipment = addition_equipment
            self.sum_of_total_transport = addition_transport
            self.sum_of_total_third_party = addition_third_party

            
    def process_model_button(self):
        return {
           'type' : 'ir.actions.act_window',
           'name' : 'Related Process',
           'view_mode' : 'tree,form',
           'res_model' : 'process.model',
           'domain': [('budget_ids','=',self.id)],
       }
        
    def boq_attachment_fun(self):
        for rec in self:
            rec.boq_attachment = self.env['ir.attachment'].search_count([('res_model', '=', self._name),('res_id','=',self.id)])
        

    def action_attachement_boq(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Employee Document',
            'res_model': 'ir.attachment',
            'domain': [('res_model', '=', 'product.budget'),('res_id','=',self.id)],
            'view_mode': 'tree,form',
            'context': {'default_res_id': self.id, 'default_res_model': self._name}
        }


    @api.depends('price')
    def amount_price_subtotal(self):
        for rec in self:
            rec.sub_total = (rec.price * 1.3)

    @api.depends('price_per')
    def amount_price_subtotal_per(self):
        for rec in self:
            rec.sub_total_per = (rec.price_per * 1.3)

    @api.constrains('price')
    def constrains_product_new_id(self):
            orm1 = self.env['product.product'].search([('id','=',self.product_new_id.id)])
            orm1.write({'lst_price': self.price})


    custom_liness = fields.One2many('man.power.custom.line', 'man_power_id', string='Custom Lines', ondelete='cascade')
    fabrication_lines= fields.One2many('product.fabrication.cost.line', 'ttproduct_fabrication_id_name', string='Fabrication', ondelete='cascade')
    material_lines= fields.One2many('product.material.cost.line', 'product_material_id', string='Material', ondelete='cascade')
    tools_lines= fields.One2many('main.tools.cost.line', 'main_tools_id', string='tool' , ondelete='cascade')
    equipment_lines= fields.One2many('product.equipment.cost.line', 'product_equipment_id', string='equipment', ondelete='cascade')
    transport_lines= fields.One2many('product.transport.cost.line', 'product_transport_id', string='transport', ondelete='cascade')
    process_lines= fields.One2many('product.process.cost.line', 'product_process_id', string='process', ondelete='cascade')

    sum_of_total=fields.Float(string='Man Sub Total' ,compute='onchan_func_lab',store= True)
    sum_of_total_fabrication=fields.Float(string='Fabrication Sub Total' ,compute='fabrication_lines_func_lab',store= True)
    sum_of_total_material=fields.Float(string='Material Sub Total' ,compute='material_lines_func_lab',store= True)
    sum_of_total_tools=fields.Float(string='Tools Sub Total' ,compute='tools_lines_func_lab',store= True)
    sum_of_total_equipment=fields.Float(string='Eqipment Sub Total' ,compute='equipment_lines_func_lab' ,store= True)
    sum_of_total_transport=fields.Float(string='Transport Sub Total' ,compute='transport_lines_func_lab' ,store= True)
    sum_of_total_third_party=fields.Float(string='Third Party Sub Total',readonly=True)
    total_margin_percentage= fields.Float(string='Total Margin Percentage (%)', compute ='total_per_margins_per' ,store= True)

    @api.depends('per_of_total','per_of_total_fabrication', 'per_of_total_material', 'per_of_total_tools', 'per_of_total_equipment', 'per_of_total_transport')
    def total_per_margins(self):
        for rec in self:
            rec.total_percentage_margin = (rec.per_of_total + rec.per_of_total_fabrication + rec.per_of_total_material + rec.per_of_total_tools + rec.per_of_total_equipment + rec.per_of_total_transport )/6

    @api.depends('price','price_per')
    def total_per_margins_per(self):
        for record in self:
            if record.price_per != 0:
                record.total_margin_percentage = ((record.price - record.price_per )/record.price_per) *100
            else:
                record.total_margin_percentage = 0.0


    @api.depends('sum_of_total','sum_of_total_fabrication','sum_of_total_material','sum_of_total_tools','sum_of_total_equipment','sum_of_total_transport')
    def amount_price(self):
        for rec in self:
            rec.price = (rec.sum_of_total + rec.sum_of_total_fabrication + rec.sum_of_total_material + rec.sum_of_total_tools + rec.sum_of_total_equipment + rec.sum_of_total_transport )

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

    sum_of_total_per =fields.Float(string='Man Sub Total' ,compute='onchan_func_lab_per')
    sum_of_total_fabrication_per =fields.Float(string='Fabrication Sub Total' ,compute='fabrication_lines_func_lab_per')
    sum_of_total_material_per =fields.Float(string='Material Sub Total' ,compute='material_lines_func_lab_per')
    sum_of_total_tools_per =fields.Float(string='Tools Sub Total' ,compute='tools_lines_func_lab_per')
    sum_of_total_equipment_per =fields.Float(string='Eqipment Sub Total' ,compute='equipment_lines_func_lab_per')
    sum_of_total_transport_per =fields.Float(string='Transport Sub Total' ,compute='transport_lines_func_lab_per')

    @api.depends('sum_of_total_per','sum_of_total_fabrication_per','sum_of_total_material_per','sum_of_total_tools_per','sum_of_total_equipment_per','sum_of_total_transport_per')
    def amount_price_per(self):
        for rec in self:
            rec.price_per = (rec.sum_of_total_per + rec.sum_of_total_fabrication_per + rec.sum_of_total_material_per + rec.sum_of_total_tools_per + rec.sum_of_total_equipment_per + rec.sum_of_total_transport_per)

    @api.depends('custom_liness')
    def onchan_func_lab_per(self):
        for i in self:
            sums = 0.00
            for k in i.custom_liness:
                sums += k.total_cost_without_per
            i.update({
                'sum_of_total_per':sums,
            })

    @api.depends('fabrication_lines')
    def fabrication_lines_func_lab_per(self):
        for i in self:
            sums = 0.00
            for k in i.fabrication_lines:
                sums += k.amount_without_per
            i.update({
                'sum_of_total_fabrication_per':sums,
            })

    @api.depends('material_lines')
    def material_lines_func_lab_per(self):
        for i in self:
            sums = 0.00
            for k in i.material_lines:
                sums += k.amount_without_per
            i.update({
                'sum_of_total_material_per':sums,
            })

    @api.depends('tools_lines')
    def tools_lines_func_lab_per(self):
        for i in self:
            sums = 0.00
            for k in i.tools_lines:
                sums += k.cost_without_per
            i.update({
                'sum_of_total_tools_per':sums,
            })

    @api.depends('equipment_lines')
    def equipment_lines_func_lab_per(self):
        for i in self:
            sums = 0.00
            for k in i.equipment_lines:
                sums += k.total_cost_without_per
            i.update({
                'sum_of_total_equipment_per':sums,
            })

    @api.depends('transport_lines')
    def transport_lines_func_lab_per(self):
        for i in self:
            sums = 0.00
            for k in i.transport_lines:
                sums += k.total_cost_without_per
            i.update({
                'sum_of_total_transport_per':sums,
            })

    per_of_total=fields.Float(string='Man Sub Total' ,compute='per_man')
    per_of_total_fabrication=fields.Float(string='Fabrication Sub Total' ,compute='per_fabrication')
    per_of_total_material=fields.Float(string='Material Sub Total' ,compute='per_material')
    per_of_total_tools=fields.Float(string='Tools Sub Total' ,compute='per_tools')
    per_of_total_equipment=fields.Float(string='Eqipment Sub Total' ,compute='per_equipment')
    per_of_total_transport=fields.Float(string='Transport Sub Total' ,compute='per_transport')

    @api.depends('custom_liness')
    def per_man(self):
        for record in self:
            values = record.custom_liness.mapped('margin_amount')
            if values:
                record.per_of_total = sum(values) / len(values)
            else:
                record.per_of_total = 0.0

    @api.depends('fabrication_lines')
    def per_fabrication(self):
        for record in self:
            values = record.fabrication_lines.mapped('margin_amount')
            if values:
                record.per_of_total_fabrication = sum(values) / len(values)
            else:
                record.per_of_total_fabrication = 0.0

    @api.depends('material_lines')
    def per_material(self):
        for record in self:
            values = record.material_lines.mapped('margin_amount')
            if values:
                record.per_of_total_material = sum(values) / len(values)
            else:
                record.per_of_total_material = 0.0

    @api.depends('tools_lines')
    def per_tools(self):
        for record in self:
            values = record.tools_lines.mapped('margin_amount')
            if values:
                record.per_of_total_tools = sum(values) / len(values)
            else:
                record.per_of_total_tools = 0.0

    @api.depends('equipment_lines')
    def per_equipment(self):
        for record in self:
            values = record.equipment_lines.mapped('margin_amount')
            if values:
                record.per_of_total_equipment = sum(values) / len(values)
            else:
                record.per_of_total_equipment = 0.0

    @api.depends('transport_lines')
    def per_transport(self):
        for record in self:
            values = record.transport_lines.mapped('margin_amount')
            if values:
                record.per_of_total_transport = sum(values) / len(values)
            else:
                record.per_of_total_transport = 0.0

class ProcessProductline(models.Model):
    _name = 'product.process.cost.line'
    _description = 'Custom Lines for Bills of process'
    _rec_name = 'process_id'
    
    process_id= fields.Many2one('process.product',string='Process')
    description_process = fields.Char(string='Description')
    # name1 = fields.Many2one('man.power.category',string='Category')
    man_cost = fields.Float(string='Man Power Cost', readonly=False, compute="man_process_costs")
    fab_quantity = fields.Float(string='Fabrication Cost', readonly=False, compute="fab_process_costs")
    mat_quantity = fields.Float(string='Material Cost', readonly=False, compute="mat_process_costs")
    tool_quantity = fields.Float(string='Tools Cost', readonly=False, compute="tool_process_costs")
    eqip_quantity = fields.Float(string='Eqipment Cost', readonly=False, compute="equ_process_costs")
    trans_quantity = fields.Float(string='Transport Cost', readonly=False, compute="trans_process_costs")
    total = fields.Float(string='Total Cost',readonly=False, compute='total_amount_price')

    
    product_process_id = fields.Many2one('product.budget', string='Process')

    @api.depends('man_cost','fab_quantity','mat_quantity','tool_quantity','eqip_quantity','trans_quantity')
    def total_amount_price(self):
        for rec in self:
            rec.total = (rec.man_cost + rec.fab_quantity + rec.mat_quantity + rec.tool_quantity + rec.eqip_quantity + rec.trans_quantity)



class ManPowerid(models.Model):
    _name = 'man.power.custom.line'
    _description = 'Custom Lines for Bills of Material'

    
    name_man_power_rec= fields.Char(string='ff')
    process_man = fields.Many2one('process.product',string='Process')
    name1 = fields.Many2one('man.power.category',string='Category')
    quantity = fields.Float(string='Quantity')
    man_day = fields.Float(string='Man day')
    total = fields.Float(string='Total',readonly=False, compute='total_manpower')
    total_man_hours = fields.Float(string='Total Man Hour', readonly=False,compute='amount_manpower_hours')
    rate_hour = fields.Float(string='Rate/Hour', readonly=False, compute='man_product_one')
    total_cost = fields.Float(string='Total cost',readonly=False, compute='amount_manpower')
    total_cost_without_per = fields.Float(string='Total cost',readonly=False, compute='amount_manpower_per')
    margin_amount= fields.Float(string='Margin percentage (%)')

    man_power_id = fields.Many2one('product.budget', string='Bill of Material')

    @api.depends('total')
    def amount_manpower_hours(self):
        for rec in self:
            orm=self.env['man.power.category'].search([('man_power_category','=',rec.name1.man_power_category)], limit=1)
            a=orm.work_hourss
            rec.total_man_hours=(rec.total * a)

    @api.depends('total_man_hours','rate_hour')
    def amount_manpower_per(self):
        for rec in self:
            rec.total_cost_without_per=(rec.total_man_hours * rec.rate_hour)

    @api.depends('total_man_hours','rate_hour','margin_amount')
    def amount_manpower(self):
        for rec in self:
            amount=(rec.total_man_hours * rec.rate_hour)
            a = amount/100
            b = rec.margin_amount * a
            rec.total_cost=amount + b

    @api.depends('quantity','man_day')
    def total_manpower(self):
        for rec in self:
            rec.total=( rec.quantity * rec.man_day)

    @api.depends('name1')
    def man_product_one(self):
        for rec in self:
            orm=self.env['man.power.category'].search([('man_power_category','=',rec.name1.man_power_category)], limit=1)

            rec.rate_hour=orm.rate_hour

class CustomFabricationProduct(models.Model):
    _name = 'product.fabrication.cost.line'
    _description = 'Custom Lines for Bills of Material og fabrication cost'

    process_fab = fields.Many2one('process.product',string='Process')
    process_fabrication= fields.Many2one('fabrication.process.category',string='Fabrication Process')
    process = fields.Many2one('fabrication.process.category',string='Process')
    quantity = fields.Float(string='Quantity')
    time = fields.Float(string='Time')
    cost = fields.Float(string='Cost', readonly=False, compute='fabrication_product_one')
    amount = fields.Float(string='Amount', readonly=False, compute='amount_fabrication')
    amount_without_per = fields.Float(string='Amount', readonly=False, compute='amount_fabrication_per')
    margin_amount= fields.Float(string='Margin percentage (%)')

    ttproduct_fabrication_id_name = fields.Many2one('product.budget', string='Bill of Material')

    @api.depends('time','cost','margin_amount')
    def amount_fabrication(self):
        for rec in self:
            amount1=( rec.cost * rec.time)
            a = amount1/100
            b = rec.margin_amount * a
            rec.amount=amount1 + b

    @api.depends('time','cost')
    def amount_fabrication_per(self):
        for rec in self:
            rec.amount_without_per=( rec.cost * rec.time)

    @api.depends('process')
    def fabrication_product_one(self):
        for rec in self:
            orm=self.env['fabrication.process.category'].search([('fabrication_category','=',rec.process.fabrication_category)], limit=1)

            rec.cost=orm.rate_hour

class ProductMaterialLine(models.Model):
    _name = 'product.material.cost.line'
    _description = 'Custom Lines for Bills of Material og material cost'

    process_mat = fields.Many2one('process.product',string='Process')
    description = fields.Many2one('material.desription',string='Description')
    quantity = fields.Float(string='Quantity')
    weight_No = fields.Float(string='Weight/No')
    weight = fields.Float(string='Weight', readonly=False, compute='amount_material_weight')
    cost_no = fields.Float(string='Cost/No',readonly=False, compute='material_product_one')
    amount = fields.Float(string='Amount',readonly=False, compute='amount_material')
    amount_without_per = fields.Float(string='Amount',readonly=False, compute='amount_material_per')
    margin_amount= fields.Float(string='Margin percentage (%)')

    product_material_id = fields.Many2one('product.budget', string='Bill of Material')

    @api.depends('quantity','weight_No')
    def amount_material_weight(self):
        for rec in self:
            rec.weight=( rec.quantity * rec.weight_No)

    @api.depends('quantity','weight_No','cost_no')
    def amount_material_per(self):
        for rec in self:
            rec.amount_without_per=( rec.quantity * rec.cost_no)

    @api.depends('quantity','weight_No','cost_no','margin_amount')
    def amount_material(self):
        for rec in self:
            amount1=( rec.quantity * rec.cost_no)
            a = amount1/100
            b = rec.margin_amount * a
            rec.amount=amount1 + b

    @api.depends('description')
    def material_product_one(self):
        for rec in self:
            orm=self.env['material.desription'].search([('material_description','=',rec.description.material_description)], limit=1)

            rec.cost_no=orm.cost

class MaintoolsLine(models.Model):
    _name = 'main.tools.cost.line'
    _description = 'Custom Lines for Bills of Material og tools cost'

    process_tool = fields.Many2one('process.product',string='Process')
    description = fields.Many2one('tools.desription',string='Description')
    cost = fields.Float(string='Cost',readonly=False, compute='tool_product_one')
    cost_without_per = fields.Float(string='Cost',readonly=False, compute='tool_product_one_per')
    margin_amount= fields.Float(string='Margin percentage (%)')

    main_tools_id = fields.Many2one('product.budget', string='Bill of Material')

    @api.depends('description','margin_amount')
    def tool_product_one(self):
        for rec in self:
            orm=self.env['tools.desription'].search([('tools_description','=',rec.description.tools_description)], limit=1)

            amount1=orm.cost
            a = amount1/100
            b = rec.margin_amount * a
            rec.cost=amount1 + b

    @api.depends('description')
    def tool_product_one_per(self):
        for rec in self:
            orm=self.env['tools.desription'].search([('tools_description','=',rec.description.tools_description)], limit=1)

            rec.cost_without_per=orm.cost


class ProductequipmentLine(models.Model):
    _name = 'product.equipment.cost.line'
    _description = 'Custom Lines for Bills of Material og equipment cost'

    process_equ = fields.Many2one('process.product',string='Process')
    types_of_equipment = fields.Many2one('equipment.desription',string='Types Of Equipment')
    # quantity = fields.Float(string='Quantity')
    man_day = fields.Float(string='Man day')
    rate_man_day = fields.Float(string='Rate/Man Day', readonly=False, compute='equipment_product_one')
    total_cost = fields.Float(string='Total Cost', readonly=False, compute='amount_equipment')
    total_cost_without_per = fields.Float(string='Total Cost', readonly=False, compute='amount_equipment_per')
    margin_amount= fields.Float(string='Margin percentage (%)')

    product_equipment_id = fields.Many2one('product.budget', string='Bill of Material')

    @api.depends('man_day','rate_man_day','margin_amount')
    def amount_equipment(self):
        for rec in self:
            amount1=( rec.man_day * rec.rate_man_day)
            a = amount1/100
            b = rec.margin_amount * a
            rec.total_cost=amount1 + b

    @api.depends('man_day','rate_man_day')
    def amount_equipment_per(self):
        for rec in self:
            rec.total_cost_without_per=( rec.man_day * rec.rate_man_day)

    @api.depends('types_of_equipment')
    def equipment_product_one(self):
        for rec in self:
            orm=self.env['equipment.desription'].search([('types_of_equipment','=',rec.types_of_equipment.types_of_equipment)], limit=1)

            rec.rate_man_day=orm.rate_hour

class ProducttransportLine(models.Model):
    _name = 'product.transport.cost.line'
    _description = 'Custom Lines for Bills of Material og transport cost'

    process_trans = fields.Many2one('process.product',string='Process')
    types_of_transport = fields.Many2one('transport.desription',string='Types Of Transport')
    # quantity = fields.Float(string='Quantity')
    man_day = fields.Float(string='Man day')
    rate_man_day = fields.Float(string='Rate/Man Day', readonly=False, compute='transport_product_one')
    total_cost = fields.Float(string='Total Cost', readonly=False, compute='amount_transport')
    total_cost_without_per = fields.Float(string='Total Cost', readonly=False, compute='amount_transport_per')
    margin_amount= fields.Float(string='Margin percentage (%)')


    product_transport_id = fields.Many2one('product.budget', string='Bill of Material')

    @api.depends('man_day','rate_man_day','margin_amount')
    def amount_transport(self):
        for rec in self:
            amount1=( rec.man_day * rec.rate_man_day)
            a = amount1/100
            b = rec.margin_amount * a
            rec.total_cost=amount1 + b

    @api.depends('man_day','rate_man_day')
    def amount_transport_per(self):
        for rec in self:
            rec.total_cost_without_per=( rec.man_day * rec.rate_man_day)

    @api.depends('types_of_transport')
    def transport_product_one(self):
        for rec in self:
            orm=self.env['transport.desription'].search([('types_of_transport','=',rec.types_of_transport.types_of_transport)], limit=1)

            rec.rate_man_day=orm.rate_hour





