from odoo import fields, models, api, tools, _ 
from odoo.exceptions import ValidationError
from datetime import datetime
from io import BytesIO
import qrcode
import base64

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            budget = self.env['product.budget'].search([('product_name', '=', self.product_id.id)], limit=1)
            if budget:
                self.price_unit = budget.sub_total
            else:
                self.price_unit = 0.0
        else:
            self.price_unit = 0.0


class inherit_sales_oder_bom(models.Model):
    _inherit = 'sale.order'

    actual_price=fields.Float(string='Actual price', readonly=False ,compute='actual_price_one')
    expected_price=fields.Float(string='Expected Price' , readonly=False ,compute='expceted_price')
    terms_conditions = fields.Many2one('terms.conditions',"Terms and Conditions")
    usd_int_terms = fields.Html("")
    rfq_num=fields.Char(string='RFQ Number')
    bom_count_project = fields.Integer(string='Project', compute='boq_project')
    project_creation_new = fields.Boolean(string='project')
    sale_attachment = fields.Integer(string='Customer Documents', compute='sale_attachment_fun')
    
    
    def boq_project(self):
        for rec in self:
            rec.bom_count_project = self.env['project.project'].search_count([('sale_order_num','=',self.id )])

    
    def action_boq_project(self):
        return{
            'type': 'ir.actions.act_window',
            'name': 'project',
            'res_model': 'project.project',
            'domain': [('sale_order_num','=',self.id )],
            'view_mode': 'tree,form',
            'view_type': 'form',
        } 
        
    def sale_attachment_fun(self):
        for rec in self:
            rec.sale_attachment = self.env['ir.attachment'].search_count([('res_model', '=', rec._name),('res_id','=',rec.id)])


    def action_attachement_sale(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'sale',
            'res_model': 'ir.attachment',
            'domain': [('res_model', '=', self._name),('res_id','=',self.id)],
            'view_mode': 'tree,form',
            'context': {'default_res_id': self.id, 'default_res_model': self._name}
        }
    
            
    @api.onchange('terms_conditions')
    def _termscondition(self):
        for rec in self:
            rec.note = rec.terms_conditions.terms

    def expceted_price(self):
        list1=[]
        for rec in self.order_line:
            list1.append(rec.product_id.id)
        orm_1 = self.env['product.budget'].search([('product_name','in',list1)])
        # self.bom_count = orm_1
        self.expected_price= sum(orm_1.mapped('sub_total'))



    def actual_price_one(self):
        list1=[]
        for rec in self:
            # list1.append(rec.product_id.id)
            orm_1 = self.env['project.task'].search([('sale_order_task','=',self.id )])
        # self.bom_count = orm_1
        self.actual_price= sum(orm_1.mapped('price'))

    def action_project(self):
        self.project_creation_new = True
        for each in self.order_line:
            first_line = self.env['sale.order.line'].search([('order_id','=',self.id),],limit=1)
            
            
        return{
        'type': 'ir.actions.act_window',
        'name': 'Project`',
        'res_model': 'project.project',
        # 'target': 'new',
        'view_mode': 'form',
        'view_type': 'form',
        'context':{ 'default_sale_order_num': self.id,
                    'default_name': first_line.product_id.name,
                    'default_actual_price': self.actual_price,
                    'default_expected_price': self.expected_price,
                    'default_partner_id': self.partner_id.id,
                    'default_boq': first_line.product_id.id,
                    'default_project_type':'outhouse',
                    }
        }

    bom_count = fields.Integer(string='Bill of Materials',compute='sample_demo')
    bom_count_product = fields.Integer(string='Bills of Materials', compute='boq_product')
    
    bom_count_task = fields.Integer(string='Task', compute='boq_Task')

    def boq_Task(self):
        for rec in self:
            rec.bom_count_task = self.env['project.task'].search_count([('sale_order_task','=',self.id )])


    def action_boq_task(self):
        return{
            'type': 'ir.actions.act_window',
            'name': 'Task',
            'res_model': 'project.task',
            'domain': [('sale_order_task','=',self.id )],
            'view_mode': 'tree,form',
            'view_type': 'form',
        } 

    def boq_product(self):
        list1=[]
        for rec in self.order_line:
            list1.append(rec.product_id.id)
        orm_1 = self.env['product.budget'].search_count([('product_name','in',list1)])
        self.bom_count_product = orm_1


    def action_boq_product(self):
        list1 = []
        for line in self.order_line:
            list1.append(line.product_id.id)
        return{
            'type': 'ir.actions.act_window',
            'name': 'Bill of Materials',
            'res_model': 'product.budget',
            'domain': [('product_name','in',list1)],
            'view_mode': 'tree,form',
            'view_type': 'form',
        }    

    def sample_demo(self):
        list1=[]
        for rec in self.order_line:
            list1.append(rec.product_id.product_tmpl_id.id)
        # orm_2 = self.env['mrp.bom']
        # template = orm_2.product_tmpl_id.product_tmpl_id.id
        orm_1 = self.env['mrp.bom'].search_count([('product_tmpl_id','in',list1)])
        self.bom_count = orm_1


    def action_bom(self):
        list1 = []
        for line in self.order_line:
            list1.append(line.product_id.product_tmpl_id.id)
        return{
            'type': 'ir.actions.act_window',
            'name': 'Bill of Materials',
            'res_model': 'mrp.bom',
            'domain': [('product_tmpl_id','in',list1)],
            'view_mode': 'tree,form',
            'view_type': 'form',
        }
    
class inherit_project(models.Model):
    _inherit = 'project.project'
    _rec_name = 'service_number_project'

    sale_order_num=fields.Many2one('sale.order', string='Sale Order')
    project_type=fields.Selection([('inhouse','InHouse'),('outhouse','OutHouse')],string="Type")
    project_start_date  = fields.Datetime(string='Project start Date')
    project_status = fields.Selection( [ ('not_started', 'Not Started'),('onprogress', 'On Progress'), 
                                         ('onhold', 'On Hold'), ('completed', 'Completed')],string='Project Status',default='not_started',required=True)
    product_ids = fields.Many2many('product.product',string="products")
    boq=fields.Many2one('product.product', string='BOQ',domain="[('id','in',product_ids)]")
    expected_price_tasks=fields.Float(string='Expected Price' , readonly=False ,store='True')
    service_number_project = fields.Char(string="Project Number", readonly=True, 
                                 copy=False, index=True, default=lambda self:_('New'))
    vendor_bill_count = fields.Integer(string='Vendor Bill', compute='vendor_count_Task')
    
    profit = fields.Float(string = 'Profit' , compute='cal_profit' )
    
    inv_lines=fields.Many2many('account.move', string='Invoice',domain="[('move_type', '=', 'out_invoice')]")

    @api.depends('expected_price_tasks')
    def cal_profit(self):
        for rec in self:
            # Assuming 'vendor_bill_count' and 'price' are fields of the record
            rec.profit = rec.expected_price_tasks - (rec.vendor_bill_count + rec.price)


    @api.onchange('sale_order_num')
    def sale_amount(self):
        if self.sale_order_num:
            for rec in self:
                sale_amt= self.env['sale.order'].search([('id','=',rec.sale_order_num.id)])
                self.expected_price_tasks = sale_amt.amount_total
    
    def vendor_count_Task(self):
        for rec in self:
            orm_vendor = self.env['account.move'].search([('job_code','=',rec.service_number_project ),('move_type', '=', 'in_invoice')])
            rec.vendor_bill_count= sum(vendor.amount_total for vendor in orm_vendor)

    def action_vendor_bill_get(self):
        return{
            'type': 'ir.actions.act_window',
            'name': 'Vendor Bill',
            'res_model': 'account.move',
            'domain': [('job_code','=',self.service_number_project ),('move_type', '=', 'in_invoice')],
            'view_mode': 'tree,form',
            'view_type': 'form',
        }
        
    customer_bill_count = fields.Monetary(string='Customer Bill', compute='customer_count_Task')

    def customer_count_Task(self):
        for rec in self:
            orm_customer = self.env['account.move'].search([('job_code','=',rec.service_number_project ),('move_type', '=', 'out_invoice')])
            rec.customer_bill_count = sum(customer.amount_total for customer in orm_customer)


    def action_customer_bill_get(self):
        return{
            'type': 'ir.actions.act_window',
            'name': 'Customer Bill',
            'res_model': 'account.move',
            'domain': [('job_code','=',self.service_number_project ),('move_type', '=', 'out_invoice')],
            'view_mode': 'tree,form',
            'view_type': 'form',
        } 
        
    
    @api.model
    def create(self, values):
        if values.get('project_type') == 'outhouse':
            values['service_number_project'] = self.env['ir.sequence'].next_by_code('project.project') or _('New')
        else:
            search_bill = self.env['project.project'].search([('project_type' ,'=','inhouse')],order='id desc')
            if search_bill:
                # values['service_number_project'] = "INHOUSE/1"
                last_record = search_bill[0]
                string, integer = last_record.service_number_project.split('/')
                number_increment = str(int(integer) + 1)
                concatination = f"{string}/{number_increment}"
                values['service_number_project'] = str(concatination)
            else:
                values['service_number_project'] = _('New')

        return super(inherit_project, self).create(values)



    # def expceted_price_task(self):
    #     # list1=[]
    #     for rec in self:
    #         # list1.append(rec.product_id.id)
    #         orm_1 = self.env['project.task'].search([('project_id','=',self.id)])
    #         # self.bom_count = orm_1
    #         self.expected_price_tasks= sum(orm_1.mapped('sum_of_total_expense'))
        
        
    def action_task_one(self):
        return{
        'type': 'ir.actions.act_window',
        'name': 'Task`',
        'res_model': 'project.task',
        # 'target': 'new',
        'view_mode': 'form',
        'view_type': 'form',
        'context':{ 'default_sale_order_task': self.sale_order_num.id if self.sale_order_num else None,
                   'default_product_name': self.boq.id if self.boq else None,
                   'default_project_id': self.id,
                    }
            }
    
    bom_count_product = fields.Integer(string='BOQ', compute='boq_project')

    def boq_project(self):
        list1=[]
        for rec in self:
            # list1.append(rec.product_id.id)
            orm_1 = self.env['product.budget'].search_count([('product_name','=',self.boq.id )])
        self.bom_count_product = orm_1


    def action_boq_project(self):
        # list1 = []
        # for line in self:
        #     list1.append(line.product_id.id)
        return{
            'type': 'ir.actions.act_window',
            'name': 'Task',
            'res_model': 'product.budget',
            'domain': [('product_name','=',self.boq.id )],
            'view_mode': 'tree,form',
            'view_type': 'form',
        } 

    @api.onchange('sale_order_num')
    def _boq(self):
        for rec in self:
            products = []
            for line in rec.sale_order_num.order_line:
                products.append(line.product_id.id)
            rec.product_ids = [[6,True,products]]
            
            
class inherit_task(models.Model):
    _inherit = 'project.task'

    sale_order_task=fields.Many2one('sale.order', string='Sale Order')


    def action_purchase(self):
        return{
        'type': 'ir.actions.act_window',
        'name': 'Purchase',
        'res_model': 'purchase.order',
        # 'target': 'new',
        'view_mode': 'form',
        'view_type': 'form',
        'context':{ 'default_sale_order_purchase': self.sale_order_task.id,
                    'default_task_id': self.id,
                    }
    }
        
class inherit_purchase(models.Model):
    _inherit = 'purchase.order'

    sale_order_purchase=fields.Many2one('sale.order', string='Sale Order')
    task_id=fields.Many2one('project.task', string='Task Id')
    
    terms_and_condition_id=fields.Many2one('terms.conditions',string="Terms and Conditions")

    @api.onchange('terms_and_condition_id')
    def terms_and_condition_append(self):
        for rec in self:
            if rec.terms_and_condition_id:
                rec.notes=rec.terms_and_condition_id.terms