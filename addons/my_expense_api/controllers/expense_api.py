from odoo import http
from odoo.http import request
import base64
import mimetypes
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class ExpenseAPIController(http.Controller):

    @http.route('/api/expenses/create', type='json', auth='public', methods=['POST'], csrf=False)
    def create_expense(self, **kwargs):
        try:
            data = kwargs

            chat_id = data.get('chat_id')
            employee_id = data.get('employee_id')

            product_name = data.get('product_name')
            name = data.get('name')
            amount = data.get('total_amount')
            date = data.get('date')
            company_name = data.get('company_name')
            cheque = data.get('cheque')
            cash = data.get('cash')
            bank_transfer = data.get('bank_transfer')
            gst_filing = data.get('gst_filing')
            gst_status = data.get('gst_status')
            invoice_no = data.get('invoice_no')
            invoice_amount = data.get('invoice_amount')
            job_no = data.get('job_no')
            registration_no = data.get('registration_no')
            receipt_base64 = data.get('receipt_base64', 'N/A')
            products_data = data.get('products', [])

            # Validate required fields
            missing_fields = []
            if not chat_id:
                missing_fields.append("chat_id")
            if not product_name:
                missing_fields.append("product_name")
            if not name:
                missing_fields.append("name")
            if not amount:
                missing_fields.append("total_amount")
            if not date:
                missing_fields.append("date")

            if missing_fields:
                return {
                    'success': False,
                    'error': f"Missing required fields: {', '.join(missing_fields)}"
                }

            # Check if employee exists
            employee = request.env['hr.employee'].sudo().search([('chat_id', '=', chat_id)], limit=1)
            if not employee:
                return {
                    'success': False,
                    'error': f"Employee with chat ID {chat_id} not found"
                }

            # Get or create product
            product = request.env['product.product'].sudo().search([('name', '=', product_name)], limit=1)
            if not product:
                product = request.env['product.product'].sudo().create({
                    'name': product_name,
                    'type': 'service',
                })
                
            tax_ids = []
            if data.get('tax_names'):
                for tax_name in data.get('tax_names', []):
                    tax_rec = request.env['account.tax'].sudo().search([('name', '=', tax_name)], limit=1)
                    if tax_rec:
                        tax_ids.append(tax_rec.id)

            # Create the expense record
            expense = request.env['hr.expense'].sudo().create({
                'employee_id': employee.id,
                'product_id': product.id,
                'name': name,
                'total_amount': amount,
                'tax_ids': [(6, 0, tax_ids)] if tax_ids else [],
                'date': date,
                'company_name': company_name,
                'cheque' : cheque,
                'cash' : cash,
                'bank_transfer' : bank_transfer,
                'gst_filing' : gst_filing,
                'gst_status' : gst_status,
                'invoice_no' : invoice_no,
                'invoice_amount' : invoice_amount,
                'job_no' : job_no,
                'registration_no' : registration_no,
            })
            
            if receipt_base64:
                # Remove data prefix if present
                if receipt_base64.startswith("data:"):
                    receipt_base64 = receipt_base64.split(",")[1]

                # Create attachment
                request.env['ir.attachment'].sudo().create({
                    'name': 'receipt.jpg',  # default filename
                    'res_model': 'hr.expense',
                    'res_id': expense.id,
                    'type': 'binary',
                    'datas': receipt_base64,
                    'mimetype': 'image/jpeg',  # adjust if needed
                })
            
            # attachments = data.get('attachments', [])
            # for attachment in attachments:
            #     datas = attachment.get('datas')
            #     mimetype = attachment.get('mimetype', 'application/octet-stream')

            #     if datas:
            #         # Remove data URI prefix if present
            #         if datas.startswith("data:"):
            #             datas = datas.split(",")[1]

            #         request.env['ir.attachment'].sudo().create({
            #             'name': 'receipt', # default filename
            #             'datas': datas,
            #             'res_model': 'hr.expense',
            #             'res_id': expense.id,
            #             'type': 'binary',
            #             'mimetype': mimetype,
            #         })
                
            vendor = request.env['res.partner'].sudo().search([('name', '=', employee.name)], limit=1)
            if not vendor:
                vendor = request.env['res.partner'].sudo().create({
                    'name': employee.name,
                    'supplier_rank': 1
                })
                
            bill_lines = []
            for prod in products_data:
                product_name = prod.get('product_name')
                quantity = prod.get('quantity', 1)
                price_unit = prod.get('price_unit', 0)
                tax_names = prod.get('tax_names', [])

                if not product_name:
                    return {
                        'success': False,
                        'error': "One of the products is missing 'product_name'"
                    }

                # Get or create product
                product = request.env['product.product'].sudo().search([('name', '=', product_name)], limit=1)
                if not product:
                    product = request.env['product.product'].sudo().create({
                        'name': product_name,
                        'type': 'product',
                    })

                # Get taxes
                tax_ids = []
                for tax_name in tax_names:
                    tax_rec = request.env['account.tax'].sudo().search([('name', '=', tax_name)], limit=1)
                    if tax_rec:
                        tax_ids.append(tax_rec.id)

                # Build invoice line command
                bill_lines.append((0, 0, {
                    'product_id': product.id,
                    'quantity': quantity,
                    'price_unit': price_unit,
                    'tax_ids': [(6, 0, tax_ids)] if tax_ids else [],
                }))

            # Create vendor bill
            vendor_bill = request.env['account.move'].sudo().create({
                'move_type': 'in_invoice',
                'partner_id': vendor.id,
                'invoice_date': date,
                'invoice_line_ids': bill_lines
            })
            
            return {
                'success': True,
                'vendor_bill_id': vendor_bill.id,
                'message': "Expense and Vendor Bill created successfully"
            }

        except Exception as e:
            _logger.exception("Unexpected error while creating expense:")
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}"
            }