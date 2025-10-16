from odoo import fields, models, api, tools, _ 
from odoo.exceptions import ValidationError
from datetime import datetime
from io import BytesIO
import qrcode
import base64

class inherit_account_move_linesssss(models.Model):
    _inherit = 'account.move.line'

    unit =fields.Char(string='Unit')

    s_no = fields.Integer(compute="_sequence_ref",store = True)  
    expenses_id = fields.Many2one('account.account', string='Expense')

    @api.depends('move_id.invoice_line_ids')
    def _sequence_ref(self):
        for line in self:
            no = 0
            for l in line.move_id.invoice_line_ids:
                no += 1
                l.s_no = no

class inherit_order_linesssz(models.Model):
    _inherit = 'sale.order.line'

    unit =fields.Char(string='Unit')

    s_noss = fields.Integer(string='S.No',compute="_sequence_ref_sale",store = True)  

    @api.depends('order_id.order_line')
    def _sequence_ref_sale(self):
        for line in self:
            no = 0
            for l in line.order_id.order_line:
                no += 1
                l.s_noss = no
    

class inherit_delivery_linesssz(models.Model):
    _inherit = 'stock.move'

    unit =fields.Char(string='Unit')
    remark=fields.Text(string='Remark')

    s_nodd = fields.Integer(string='S.No',compute="_sequence_ref_delivery",store = True)  

    @api.depends('picking_id.move_ids_without_package')
    def _sequence_ref_delivery(self):
        for line in self:
            no = 0
            for l in line.picking_id.move_ids_without_package:
                no += 1
                l.s_nodd = no

class inherit_purchase_linesssz(models.Model):
    _inherit = 'purchase.order.line'

    s_nodd = fields.Integer(string='S.No',compute="_sequence_ref_purchase", store = True)  
    unit =fields.Char(string='Unit')

    @api.depends('order_id.order_line')
    def _sequence_ref_purchase(self):
        for line in self:
            no = 0
            for l in line.order_id.order_line:
                no += 1
                l.s_nodd = no

class inherit_delivery_linesz(models.Model):
    _inherit = 'sale.order'

    delivery_validates = fields.Char(string='Valitidity ',default='4 weeks from Quotation Date')
    tax_term =fields.Char(string='Tax: ',default='SGD with Subjected to 8% GST')
    delivery_in_one =fields.Char(string='Delivery', default='2-3 working days from PO')
    payment_one = fields.Char(string='Payment',  default='Cash On Delivery(COD)')

    sef_number = fields.Char(string='SEF Number')
    cash_terms = fields.Selection([('cash',"Cash"), ('cheque', "Cheque")])
    
    @api.onchange('partner_id')
    def bill_sequence_change(self):
        search_bill = self.env['account.move'].search([('move_type','=','in_invoice'),('name','ilike',"sale.order.line")],order="id asc")
        count = 1
        for rec in search_bill:
            rec.write({'name':f"BILL/{count}"})
            count += 1

class inherit_invoive(models.Model):
    _inherit = 'account.move'
    
    account_no = fields.Char(string='Account No ',default='0029067301')
    bank_name =fields.Char(string='Bank: ',default='DBS')
    branch_code =fields.Char(string='Branch Code', default='7171-002')
    dc_number=  fields.Many2one ('stock.picking', string='DC Number')
    # payment_one = fields.Char(string='Payment',  default='Cash On Delivery(COD)')

    po_number = fields.Char(string='PO Number')
    sef_number = fields.Char(string='SEF Number')
    job_code = fields.Char(string='Job Code')
    cash_terms = fields.Selection([('cash',"Cash"), ('cheque', "Cheque")])
    purchase_by = fields.Many2one('hr.employee', string='Purchase By')
    
    gst_tax_total = fields.Monetary(string='GST', compute='gst_tax_amount')

    @api.depends('amount_total','amount_untaxed')
    def gst_tax_amount(self):
        for rec in self:
            rec.gst_tax_total = (rec.amount_total - rec.amount_untaxed)
            
    # @api.model
    # def create(self,vals):
    #     result = super(inherit_invoive,self).create(vals)
    #     if result.move_type == "out_invoice":
    #         result.name = self.env['ir.sequence'].next_by_code('account.move.customer')

    #     elif result.move_type == 'in_invoice':
    #         search_bill = self.env['account.move'].search([('move_type' ,'=','in_invoice')],order='id desc')
    #         if len(search_bill) > 1:
    #             last_record = search_bill[1]
    #             string,integer = last_record.name.split('/')
    #             number_increment = str(int(integer)+1)
    #             concatination = f"{string}/{number_increment}"
    #             # raise ValidationError(concatination)
    #             result.name = str(concatination)
            
    #     else:
    #         pass
    #     return result

    @api.model
    def create(self, vals):
        result = super(inherit_invoive, self).create(vals)
        
        if result.move_type == "out_invoice":
            result.name = self.env['ir.sequence'].next_by_code('account.move.customer')

        elif result.move_type == 'in_invoice':
            search_bill = self.env['account.move'].search(
                [('move_type', '=', 'in_invoice')],
                order='id desc'
            )
            if len(search_bill) > 1:
                last_record = search_bill[1]
                
                # Split safely
                parts = last_record.name.split('/')
                string = '/'.join(parts[:-1])   # Everything except last part
                integer = parts[-1]              # Last part as number
                
                # Increment number
                number_increment = str(int(integer) + 1)
                concatination = f"{string}/{number_increment}"
                
                result.name = concatination

        return result



class inherit_delivery(models.Model):
    _inherit = 'stock.picking'
    
    po_number = fields.Char(string='PO Number')
    sef_number = fields.Char(string='SEF Number')
    job_code = fields.Char(string='Job Code')

    note_delivery = fields.Text(string='Note' ,placeholder='Terms & Condition...')

class inherit_purchase(models.Model):
    _inherit = 'purchase.order'

    cash_terms = fields.Selection([('cash',"Cash"), ('cheque', "Cheque") ,('online', "Online Transfer")])
    job_code = fields.Char(string='Job Code')

    # note_purchase = fields.Text(placeholder='Terms & Condition...')

class inherit_expenses(models.Model):
    _inherit = 'hr.expense'

    name_partner = fields.Many2one('res.partner', string='Name', domain="[('supplier_rank', '=', '1')]")
    task_id = fields.Many2one('project.task', string='Task Id', domain = "[('project_id','=',project_id)]")
    project_id = fields.Many2one('project.project', string ='Project Id')


    payment_type= fields.Selection([('cash',"Cash"), ('cheque', "Cheque")], string='Payment Type', widget='radio')
    cheque_no = fields.Char(string='Cheque No.')

class attendance_inherit(models.Model):
    _inherit = 'hr.attendance'

    location_in = fields.Char(string='Location In')
    location_out = fields.Char(string='Location Out')
    
# class inherit_partner(models.Model):
#     _inherit = 'res.partner'

#     vendor = fields.Boolean(string='Vendor')
