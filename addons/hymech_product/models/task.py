from odoo import fields, models, api, tools, _ 
from odoo.exceptions import ValidationError
from datetime import datetime

class TaskInherit(models.Model):
    _inherit = 'project.task'

    product_name= fields.Many2one('product.product', string='BOQ')
    price = fields.Float(string='Price',readonly=False, compute='amount_price')
    process=fields.Many2one('product.process.cost.line', string='Select Process',domain = "[('product_process_id.product_name','=',product_name)]")
    sum_of_total_expense=fields.Float(string='Expense Sub Total', store=True,default='0')

    @api.depends('sum_of_total','sum_of_total_fabrication','sum_of_total_material','sum_of_total_tools','sum_of_total_equipment','sum_of_total_transport')
    def amount_price(self):
        for rec in self:
            rec.price = (rec.sum_of_total + rec.sum_of_total_fabrication + rec.sum_of_total_material + rec.sum_of_total_tools + rec.sum_of_total_equipment + rec.sum_of_total_transport)

    
    actual_man_cost = fields.One2many('actual.man.power.cost', 'man_power_id', string='Man Power')
    fabrication_lines= fields.One2many('actual.fabrication.cost', 'product_fabrication_id_name', string='Fabrication')
    material_lines= fields.One2many('actual.material.cost', 'product_material_id', string='Material')
    tools_lines= fields.One2many('actual.tools.cost', 'main_tools_id', string='tool')
    equipment_lines= fields.One2many('actual.equipment.cost', 'product_equipment_id', string='equipment')
    transport_lines= fields.One2many('actual.transport.cost', 'product_transport_id', string='transport')
    
    
    sum_of_total = fields.Float(string='Man Sub Total' ,compute='onchan_func_lab')
    sum_of_total_fabrication=fields.Float(string='Fabrication Sub Total' ,compute='fabrication_lines_func_lab')
    sum_of_total_material=fields.Float(string='Material Sub Total' ,compute='material_lines_func_lab')
    sum_of_total_tools=fields.Float(string='Tools Sub Total' ,compute='tools_lines_func_lab')
    sum_of_total_equipment=fields.Float(string='Eqipment Sub Total' ,compute='equipment_lines_func_lab')
    sum_of_total_transport=fields.Float(string='Transport Sub Total' ,compute='transport_lines_func_lab')
    expenses_lines= fields.One2many('hr.expense.cost', 'expense_id', string='Expense')    
    @api.depends('actual_man_cost')
    def onchan_func_lab(self):
        for i in self:
            sums = 0.00
            for k in i.actual_man_cost:
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

    @api.onchange('process')
    def _task_name(self):
        for rec in self:
            if rec.process:
                rec.name = f"{rec.project_id.name} - {rec.process.process_id.process_product}"
            else:
                rec.name = f"{rec.project_id.name}"   
            
    @api.onchange('expenses_lines')
    def onchange_expense_amount(self):
        for i in self:
            sums = 0.00
            for k in i.expenses_lines:
                sums += k.total
            i.update({
                'sum_of_total_expense':sums,
             })           
class ManPowerid(models.Model):
    _name = 'actual.man.power.cost'
    # _description = 'Custom Lines for Bills of Material'

    name_man_power_rec= fields.Char(string='ff')
    process_man = fields.Many2one('process.product',string='Process')
    name1 = fields.Many2one('man.power.category',string='Category')
    quantity = fields.Float(string='Quantity')
    man_day = fields.Float(string='Man day')
    total = fields.Float(string='Total',readonly=False, compute='total_manpower')
    total_man_hours = fields.Float(string='Total Man Hour', readonly=False,compute='amount_manpower_hours')
    rate_hour = fields.Float(string='Rate/Hour', readonly=False, compute='man_product_one')
    total_cost = fields.Float(string='Total cost',readonly=False, compute='amount_manpower')
    
    man_power_id = fields.Many2one('project.task', string='Bill of Material')
    
    @api.depends('total')
    def amount_manpower_hours(self):
        for rec in self:
            orm=self.env['man.power.category'].search([('man_power_category','=',rec.name1.man_power_category)], limit=1)
            a=orm.work_hourss
            rec.total_man_hours=(rec.total * a)

    @api.depends('total_man_hours','rate_hour')
    def amount_manpower(self):
        for rec in self:
            rec.total_cost=(rec.total_man_hours * rec.rate_hour)

    @api.depends('quantity','man_day')
    def total_manpower(self):
        for rec in self:
            rec.total=( rec.quantity * rec.man_day)

    @api.depends('name1')
    def man_product_one(self):
        for rec in self:
            orm=self.env['man.power.category'].search([('man_power_category','=',rec.name1.man_power_category)], limit=1)

            rec.rate_hour=orm.rate_hour
    
class ActualFabrication(models.Model):
    _name = 'actual.fabrication.cost'
    _description = 'Custom Lines for Bills of Material og fabrication cost'

    process_fab = fields.Many2one('process.product',string='Process')
    process_fabrication= fields.Many2one('fabrication.process.category',string='Fabrication Process')
    process = fields.Many2one('fabrication.process.category',string='Process')
    quantity = fields.Float(string='Quantity')
    time = fields.Float(string='Time')
    cost = fields.Float(string='Cost', readonly=False, compute='fabrication_product_one')
    amount = fields.Float(string='Amount', readonly=False, compute='amount_fabrication')

    product_fabrication_id_name = fields.Many2one('project.task', string='Bill of Material')

    @api.depends('time','cost')
    def amount_fabrication(self):
        for rec in self:
            rec.amount=( rec.cost * rec.time)

    @api.depends('process')
    def fabrication_product_one(self):
        for rec in self:
            orm=self.env['fabrication.process.category'].search([('fabrication_category','=',rec.process.fabrication_category)], limit=1)

            rec.cost=orm.rate_hour
    
    
class ProductMaterialLine(models.Model):
    _name = 'actual.material.cost'
    _description = 'Custom Lines for Bills of Material og material cost'

    process_mat = fields.Many2one('process.product',string='Process')
    description = fields.Many2one('material.desription',string='Description')
    quantity = fields.Float(string='Quantity')
    weight_No = fields.Float(string='Weight/No')
    weight = fields.Float(string='Weight', readonly=False, compute='amount_material_weight')
    cost_no = fields.Float(string='Cost/No',readonly=False, compute='material_product_one')
    amount = fields.Float(string='Amount',readonly=False, compute='amount_material')


    product_material_id = fields.Many2one('project.task', string='Bill of Material')

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
    
    
class MaintoolsLine(models.Model):
    _name = 'actual.tools.cost'
    _description = 'Custom Lines for Bills of Material og tools cost'

    process_tool = fields.Many2one('process.product',string='Process')
    description = fields.Many2one('tools.desription',string='Description')
    cost = fields.Float(string='Cost',readonly=False, compute='tool_product_one')

    main_tools_id = fields.Many2one('project.task', string='Bill of Material')

    @api.depends('description')
    def tool_product_one(self):
        for rec in self:
            orm=self.env['tools.desription'].search([('tools_description','=',rec.description.tools_description)], limit=1)

            rec.cost=orm.cost
    
    
class ProductequipmentLine(models.Model):
    _name = 'actual.equipment.cost'
    _description = 'Custom Lines for Bills of Material og equipment cost'

    process_equ = fields.Many2one('process.product',string='Process')
    types_of_equipment = fields.Many2one('equipment.desription',string='Types Of Equipment')
    # quantity = fields.Float(string='Quantity')
    man_day = fields.Float(string='Man day')
    rate_man_day = fields.Float(string='Rate/Man Day', readonly=False, compute='equipment_product_one')
    total_cost = fields.Float(string='Total Cost', readonly=False, compute='amount_equipment')

    product_equipment_id = fields.Many2one('project.task', string='Bill of Material')
    
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
    _name = 'actual.transport.cost'
    _description = 'Custom Lines for Bills of Material og transport cost'

    process_trans = fields.Many2one('process.product',string='Process')
    types_of_transport = fields.Many2one('transport.desription',string='Types Of Transport')
    # quantity = fields.Float(string='Quantity')
    man_day = fields.Float(string='Man day')
    rate_man_day = fields.Float(string='Rate/Man Day', readonly=False, compute='transport_product_one')
    total_cost = fields.Float(string='Total Cost', readonly=False, compute='amount_transport')

    product_transport_id = fields.Many2one('project.task', string='Bill of Material')

    @api.depends('man_day','rate_man_day')
    def amount_transport(self):
        for rec in self:
            rec.total_cost=( rec.man_day * rec.rate_man_day)

    @api.depends('types_of_transport')
    def transport_product_one(self):
        for rec in self:
            orm=self.env['transport.desription'].search([('types_of_transport','=',rec.types_of_transport.types_of_transport)], limit=1)

            rec.rate_man_day=orm.rate_hour

class ExpenseCost(models.Model):
    _name = 'hr.expense.cost'
    _description = 'Custom Lines for Bills of Material'

    # name= fields.Many2one('res.partner', string='ff')
    name = fields.Many2one('res.partner',string='Supplier',required=True)
    product_id = fields.Many2one('product.product',string='Product',required=True)
    description = fields.Char(string='Description',required=True)
    unit_price = fields.Float(string='Unit Price')
    quantity = fields.Float(string='Quantity')
    bill_reference = fields.Char(string='Bill Reference')
    total = fields.Float(string='Total',)

    expense_id = fields.Many2one('project.task', string='Bill of Material')
 
    @api.model
    def create(self, vals):
         
        result = super(ExpenseCost, self).create(vals)
        for line in result:
            data_users = {
                'name_partner': line.name.id,
                'product_id' : line.product_id.id,
                'name' : line.description,
                'unit_amount' : line.unit_price,
                'quantity' : line.quantity,
                'reference' : line.bill_reference,
                'project_id':line.expense_id.project_id.id,
                'task_id' : line.expense_id.id
                        }
            orm = self.env['hr.expense'].create(data_users)
        return result
    
    @api.onchange('unit_price','quantity')
    def onchange_expense_total(self):
        for rec in self:
            rec.total=( rec.unit_price * rec.quantity)
