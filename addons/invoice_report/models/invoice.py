from odoo import models,fields,api,_
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError,UserError
import num2words
import json


class Invoice(models.Model):
   _inherit = 'account.move'


class AccountMoves(models.AbstractModel):
   _name="report.invoice_report.customer_invoices_pdf_document"

   @api.model
   def _get_report_values(self,docids,data=None):
      docs=self.env['account.move'].browse(docids)

      outstanding_amounts = {
         'current':0.0,
         '1_30_days': 0.0,
         '31_60_days': 0.0,
         '61_90_days': 0.0,
         'more_90_days': 0.0,}

      for invoice in docs:
         due_date = fields.Date.from_string(invoice.invoice_date_due)
         overdue_days = (datetime.today().date() - due_date).days if due_date else 0
         outstanding_amount = invoice.amount_residual
         
         if overdue_days == 0:
            outstanding_amounts['current'] += outstanding_amount
         elif overdue_days <= 30:
            outstanding_amounts['1_30_days'] += outstanding_amount
         elif 31 <= overdue_days <= 60:
            outstanding_amounts['31_60_days'] += outstanding_amount
         elif 61 <= overdue_days <= 90:
            outstanding_amounts['61_90_days'] += outstanding_amount
         elif overdue_days > 90:
            outstanding_amounts['more_90_days'] += outstanding_amount
            
      return {
         'doc_ids':docids,
         'doc_model':'account.move',
         'docs':docs ,
         'outstanding_amounts':outstanding_amounts,}   
      