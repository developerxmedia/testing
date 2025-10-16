from odoo import models, fields

class HrExpense(models.Model):
    _inherit = 'hr.expense'

    company_name = fields.Char(string='Vendor Name')
    tax = fields.Float(string='GST Amount')
    
    
    mode_of_payment = fields.Char(string='Mode of Payment')
    
    
    cheque = fields.Char(string='Cheque')
    cash = fields.Float(string='Cash')
    bank_transfer = fields.Char(string='Bank Transfer')
    gst_filing = fields.Char(string='GST Filing')
    gst_status = fields.Char(string='GST Status')
    invoice_no = fields.Char(string='Invoice number')
    invoice_amount = fields.Char(string='Invoice amount')
    job_no = fields.Char(string='Job number')
    registration_no = fields.Char(string='Registration number')