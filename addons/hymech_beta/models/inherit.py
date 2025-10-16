from odoo import fields, models, api, tools, _ 
from odoo.exceptions import ValidationError
from datetime import datetime
from io import BytesIO
import qrcode
import base64
import logging
from weasyprint import HTML
_logger = logging.getLogger(__name__)

class inherit_account_move_linesssss(models.Model):
    _inherit = 'account.move.line'

    unit =fields.Char(string='Unit')

    s_no = fields.Integer(compute="_sequence_ref",store = True)  

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
    boq = fields.Many2one('product.budget',string ='BOQ')

    @api.depends('order_id.order_line')
    def _sequence_ref_sale(self):
        for line in self:
            no = 0
            for l in line.order_id.order_line:
                no += 1
                l.s_noss = no
                
    @api.onchange('product_uom')
    def product_change_uom(self):
        if self.product_id:
            orm_search = self.env['product.product'].search([('id','=',self.product_id.id)])
            if orm_search:
                orm_search.uom_id = self.product_uom
        
    @api.onchange('boq')
    def unit_price_boq(self):
        if self.boq:
            unit_price_orm = self.env["product.budget"].search([('id','=',self.boq.id)])
            if unit_price_orm:
                self.price_unit = unit_price_orm.price

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
    atten=fields.Many2one('res.partner', string='Attn')
    customer_rfq_numnber = fields.Selection([('verbal',"Verbal"), ('email', "E-mail")],string='REF Number')
    product_name = fields.Many2one('product.product', string='Product Name') 
    
    sef_number = fields.Char(string='SEF Number')
    cash_term_paid = fields.Selection([('cash',"Cash"), ('cheque', "Cheque"), ('online', "Online Transfer")], string='Cash Terms')
    cash_terms = fields.Selection([('cash',"Cash"), ('cheque', "Cheque"), ('online', "Online Transfer")])
    cheque_no = fields.Char(string='Cheque No.')
    
    @api.onchange('opportunity_id')
    def product_sale(self):
        if self.opportunity_id and self.opportunity_id.product_id_one:
            self.product_name = self.opportunity_id.product_id_one.id
            
    @api.onchange('partner_id')
    def function_partner(self):
        list1 = []
        for rec in self.partner_id.child_ids:
            list1.append(rec.id)
        return {'domain':{'atten':[('id','in',list1)]}}
    
    
class inherit_invoive(models.Model):
    _inherit = 'account.move'

    account_no = fields.Char(string='Account No ',default='0029067301')
    bank_name =fields.Char(string='Bank: ',default='DBS')
    branch_code =fields.Char(string='Branch Code', default='7171-002')
    # payment_one = fields.Char(string='Payment',  default='Cash On Delivery(COD)')
    product_name = fields.Many2one('product.product', string='Product Name')
    atten=fields.Many2one('res.partner', string='Attn')

    po_number = fields.Char(string='PO Number')
    sef_number = fields.Char(string='SEF Number')
    job_code = fields.Char(string='Job Code')
    cash_terms = fields.Selection([('cash',"Cash"), ('cheque', "Cheque"), ('online', "Online Transfer")])
    cash_term_paid = fields.Selection([('cash',"Cash"), ('cheque', "Cheque"), ('online', "Online Transfer")], string='Cash Terms New')
    cheque_no = fields.Char(string='Cheque No.')
    gst_filing = fields.Selection([('q1',"Q1"), ('q2', "Q2"), ('q3', "Q3"),('q4', "Q4")],string='GST Filing')
    gst_status = fields.Selection([('gst',"GST"), ('nongst', "NON GST")],string='GST Status')
    cheque_num = fields.Char(string='Cheque No.')
    paid_by = fields.Selection([('own_account',"EMPLOYEE"), ('company', "COMPANY")])
    dc_id = fields.Many2many('stock.picking', string="DO")
    # sale_id = fields.Many2one('sale.order',string="Sale Order")
    terms_conditions = fields.Many2one('terms.conditions',"Terms and Conditions")

    payment_date = fields.Char(
        string='Payment Dates',
        compute='_compute_payment_date',
        store=True,
    )
    
    @api.depends('payment_state')
    def _compute_payment_date(self):
        for move in self:
            dates = []
            # Check account.payment for matching reference (ref) with the move name
            payments = self.env['account.payment'].search([('ref', '=', move.name)])
            for payment in payments:
                if payment.date:
                    dates.append(payment.date)
            # Join the collected payment dates and format them if available
            move.payment_date = ','.join(date.strftime('%d/%m/%Y') for date in dates) if dates else False

    @api.depends('invoice_origin')
    def _compute_dc_id(self):
        for move in self:
            move.dc_id = [(5, 0, 0)]  # Clear existing records
            if move.move_type == "out_invoice" and move.invoice_origin:
                try:
                    orm_dc = self.env['stock.picking'].search([('origin','=',move.invoice_origin)])
                    if orm_dc:
                        # Validate that all records are valid before setting
                        valid_ids = []
                        for record in orm_dc:
                            if record and hasattr(record, 'id') and record.id:
                                # Additional check to ensure record is valid
                                try:
                                    # Try to access a field to ensure record exists
                                    record.ensure_one()
                                    valid_ids.append(record.id)
                                except:
                                    # Record is invalid, skip it
                                    continue
                        if valid_ids:
                            move.dc_id = [(6, 0, valid_ids)]
                except Exception as e:
                    _logger.info("Error in _compute_dc_id: %s", str(e))
                    move.dc_id = [(5, 0, 0)]
            
    # @api.onchange('terms_conditions')
    # def _termscondition_invoice(self):
    #     for rec in self:
    #         rec.narration= rec.terms_conditions.terms
    
    @api.model
    def create(self,vals):
        result = super(inherit_invoive,self).create(vals)
        if result.move_type == "out_invoice":
            sale_order = result.invoice_origin
            if sale_order:
                try:
                    orm_sale = self.env['sale.order'].search([('name','=',sale_order)])
                    if orm_sale:
                        orm_project = self.env['project.project'].search([('sale_order_num','=',orm_sale.id)])
                        orm_dc = self.env['stock.picking'].search([('origin','=',sale_order)])
                        orm_invoice = self.env["sale.order"].search([('name','=',result.invoice_origin)])
                        
                        # Handle atten field more safely
                        if orm_invoice and orm_invoice.atten and orm_invoice.atten.id:
                            try:
                                # Verify the record exists before assigning
                                atten_record = self.env['res.partner'].browse(orm_invoice.atten.id)
                                if atten_record.exists():
                                    result.atten = orm_invoice.atten.id
                            except:
                                result.atten = False
                        
                        if orm_project:
                            try:
                                result.sale_id = orm_sale.id
                                # Check if orm_project has records and first record has service_number_project
                                if orm_project and orm_project[0] and hasattr(orm_project[0], 'service_number_project'):
                                    result.job_code = orm_project[0].service_number_project
                                
                                if orm_dc:
                                    # Check if orm_dc has records and first record has po_number
                                    if orm_dc and orm_dc[0] and hasattr(orm_dc[0], 'po_number'):
                                        result.po_number = orm_dc[0].po_number
                                    
                                    # Ensure we only set dc_id if we have valid records
                                    valid_dc_ids = []
                                    for dc_record in orm_dc:
                                        if dc_record and hasattr(dc_record, 'id') and dc_record.id:
                                            # Additional check to ensure record is valid
                                            try:
                                                # Try to browse the record to ensure it exists
                                                record_check = self.env['stock.picking'].browse(dc_record.id)
                                                if record_check.exists():
                                                    valid_dc_ids.append(dc_record.id)
                                            except:
                                                # Skip invalid records
                                                continue
                                    
                                    if valid_dc_ids:
                                        result.dc_id = [(6, 0, valid_dc_ids)]
                            except Exception as e:
                                # Log the exception for debugging
                                _logger.info("Exception in create method: %s", str(e))
                                pass

                        # Handle product_name field more safely
                        orm_invoice = self.env["sale.order"].search([('name','=',result.invoice_origin)])
                        if orm_invoice and orm_invoice.product_name and orm_invoice.product_name.id:
                            try:
                                # Verify the record exists before assigning
                                product_record = self.env['product.product'].browse(orm_invoice.product_name.id)
                                if product_record.exists():
                                    result.product_name = orm_invoice.product_name.id
                            except:
                                result.product_name = False
                except Exception as e:
                    _logger.info("Error in create method: %s", str(e))
        return result
    
    @api.onchange('invoice_date')
    def _onchange_invoice_date(self):
        if self.invoice_date:
            self.invoice_date= self.invoice_date
        else:
            pass
        


    def action_export_invoice_pdf(self):
        """Export invoice as PDF using WeasyPrint matching QWeb template structure"""
        try:
            # Get company logo as base64
            logo_data = ""
            if self.company_id.logo:
                logo_data = self.company_id.logo.decode('utf-8') if isinstance(self.company_id.logo, bytes) else self.company_id.logo

            # Get tax breakdown from invoice's computed taxes
            tax_breakdown = {}
            
            # Method 1: Try to get from tax_totals field (JSON field with detailed breakdown)
            if hasattr(self, 'tax_totals') and self.tax_totals:
                try:
                    import json
                    if isinstance(self.tax_totals, str):
                        tax_data = json.loads(self.tax_totals)
                    else:
                        tax_data = self.tax_totals
                    
                    # Extract tax groups from tax_totals
                    if 'groups_by_subtotal' in tax_data:
                        for subtotal_group in tax_data['groups_by_subtotal'].values():
                            for tax_group in subtotal_group:
                                tax_name = tax_group.get('tax_group_name', 'Tax')
                                tax_amount = tax_group.get('tax_group_amount', 0)
                                if tax_amount > 0:
                                    tax_breakdown[tax_name] = tax_amount
                except:
                    pass
            
            # Method 2: Fallback to GST 9% if standard tax structure
            if not tax_breakdown and self.amount_tax > 0:
                tax_breakdown['GST'] = self.amount_tax

            # HTML content matching QWeb template structure
            html_content = f"""
            <html>
            <head>
                <style>
                    @page {{
    size: A4;
    margin-top: 5mm;
    margin-bottom: 18mm;
    margin-left: 7mm;
    margin-right: 7mm;

    @bottom-center {{
        content: "This is a computer generated Invoice, No signature is required \A Please Visit: {self.company_id.website or ''} \A Page " counter(page) " of " counter(pages);
        white-space: pre;
        font-size: 11px;
        text-align: center;
        border-top: 1px solid #000;
        width: 100%;
    }}
    }}

                    body {{
                        font-family: Arial, sans-serif;
                        font-size: 13px;
                        line-height: 1.3;
                        margin: 0;
                        color: #333;
                    }}
                    .page {{
                        padding: 0;
                        margin: 0;
                    }}
                    h4 {{
                        text-align: center;
                        color: #0000ff;
                        margin-bottom: 10px;
                        font-size: 26px;
                        font-weight: 900;
                        letter-spacing: 0.3px;
                    }}
                    table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin: 0;
                    }}
                    .header-outer td {{
                        border: none;
                        padding: 5px;
                    }}
                    .meta-table {{
                        width: auto;
                        font-size: 13px;
                        font-weight: 600;
                        margin-top: 2em;
                        margin-right: 0;                
                    }}
                    .meta-table td {{
                        border: 2px solid black;
                        padding: 5px;
                        font-size: 13px;
                        height: 20px;
                        vertical-align: middle;
                    }}
                    .company-info {{
                        font-size: 13px;
                        font-weight: 450;
                        line-height: 1.3;
                    }}
                    .customer-info {{
                        padding: 8px 0 5px 0;
                        font-size: 15px;
                        font-weight: 450;
                    }}
                    .main-table th {{
                        text-align: center;
                        font-size: 16px;
                        vertical-align: middle;
                        border: 1px solid black;
                        padding: 4px;
                        background-color: #f8f9fa;
                        font-weight: bold;
                    }}
                    .main-table td {{
                        border: 1px solid black;
                        padding: 4px;
                        font-size: 14px;
                        vertical-align: top;
                        height: 30px;
                    }}
                    .center {{
                        text-align: center;
                    }}
                    .right {{
                        text-align: right;
                    }}
                    .description-cell {{
                        word-wrap: break-word;
                        white-space: pre-line;
                        text-align: left;
                        padding-left: 4px;
                        line-height: 1.3;
                    }}
                    .footer {{
                        display: flex;
                        margin-top: 20px;
                        justify-content: space-between;
                        align-items: flex-start;
                        width: 100%;
                        font-size: 13px;
                    }}
                    .terms-section {{
                        width: 55%;
                        padding-right: 15px;
                    }}
                    .totals-section {{
                        width: 40%;
                        max-width: 250px;
                        margin-left: auto;
                    }}
                    .totals-table td {{
                        padding: 4px 6px;
                        border: none;
                        border-top: 1px solid #000;
                    }}
                    .product-name {{
                        margin: 5px 0 0 0;
                        color: orange;
                        text-align: left;
                        font-size: 15px;
                    }}
                </style>
            </head>
            <body>
                <div class="page">
                    <!-- Title -->
                    <h4 style="color:#0000ff; margin-bottom:10px; font-size:26px; font-weight:900; letter-spacing:.3px;">Tax Invoice</h4>

                    <!-- Header Section -->
                    <table class="header-outer">
                        <tr>
                            <!-- Left: Company Info with Logo -->
                            <td style="width: 55%; vertical-align: top; padding-right: 10px; border-left: 1px solid white; border-top: 1px solid white; border-bottom: 1px solid white;">
                                {"<img src='data:image/png;base64," + logo_data + "' style='max-height:70px; max-width:200px; margin-bottom:10px;'/><br/>" if logo_data else ""}
                                <div class="company-info">
                                    <strong>{self.company_id.name or ''}</strong><br/>
                                    {self.company_id.street or ''}<br/>
                                    {self.company_id.street2 + '<br/>' if self.company_id.street2 else ''}
                                    {(self.company_id.city or '') + ' ' if self.company_id.city else ''}
                                    {(self.company_id.state_id.name or '') + ' ' if self.company_id.state_id else ''}
                                    {self.company_id.country_id.name + '<br/>' if self.company_id.country_id else ''}
                                    {self.company_id.zip or ''}<br/>
                                    <strong>Tel:</strong> {self.company_id.phone or ''}<br/>
                                    <strong>Email:</strong> {self.company_id.email or ''}<br/>
                                    <strong>Tax Reg No#:</strong> {self.company_id.vat or ''}
                                </div>
                            </td>
                            
                            <!-- Right: Meta Information Table -->
                            <td style="vertical-align: top;">
                                <table class="meta-table">
                                    <tr>
                                        <td style="white-space: nowrap;">Invoice #</td>
                                        <td>{self.name or ''}</td>
                                    </tr>
                                    <tr>
                                        <td style="white-space: nowrap;">Date</td>
                                        <td>{self.invoice_date.strftime('%Y-%m-%d') if self.invoice_date else ''}</td>
                                    </tr>
                                    <tr>
                                        <td style="white-space: nowrap;">PO Number</td>
                                        <td>{getattr(self, 'po_number', '') or ''}</td>
                                    </tr>
                                    <tr>
                                        <td style="white-space: nowrap;">Cash Terms</td>
                                        <td>{getattr(self, 'cash_term_paid', '') or ''}</td>
                                    </tr>
                                    <tr>
                                        <td style="white-space: nowrap;">Salesperson</td>
                                        <td>{self.user_id.name if self.user_id else ''}</td>
                                    </tr>
                                    <tr>
                                        <td style="white-space: nowrap;">DO Number</td>
                                        <td>{getattr(self, 'dc_id', '') or ''}</td>
                                    </tr>
                                    <tr>
                                        <td style="white-space: nowrap;">Job Code</td>
                                        <td>{getattr(self, 'job_code', '') or ''}</td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        
                        <!-- Customer Information -->
                        <tr>
                            <td colspan="2" class="customer-info" style="border-left: 1px solid white; border-bottom: 1px solid white; border-right: 1px solid white; height: 130px;">
                                <strong>Bill And Ship To:</strong><br/>
                                <p>
                                    {self.partner_id.name if self.partner_id else ''}<br/>
                                    {self.partner_id.street + '<br/>' if self.partner_id and self.partner_id.street else ''}
                                    {self.partner_id.street2 + '<br/>' if self.partner_id and self.partner_id.street2 else ''}
                                    {(self.partner_id.city or '') + ' ' if self.partner_id and self.partner_id.city else ''}
                                    {(self.partner_id.state_id.name or '') + ' ' if self.partner_id and self.partner_id.state_id else ''}
                                    {self.partner_id.country_id.name + '<br/>' if self.partner_id and self.partner_id.country_id else ''}
                                    {self.partner_id.zip + '<br/>' if self.partner_id and self.partner_id.zip else ''}
                                </p>
                                
                                <strong>Attn:</strong> {getattr(self, 'atten', '') and getattr(self.atten, 'name', '') or ''}<br/>
                                <strong>Tel:</strong> {getattr(self, 'atten', '') and getattr(self.atten, 'phone', '') or ''}<br/>
                                <h4 class="product-name"><strong>{getattr(self, 'product_name', '') and getattr(self.product_name, 'name', '') or ''}</strong></h4>
                            </td>
                        </tr>
                    </table>

                    <!-- Main Items Table -->
                    <table class="main-table" style="border: 1px solid black; margin-top: 5px;">
                        <thead>
                            <tr>
                                <th style="width:5%">S.No</th>
                                <th style="width:61%">Description</th>
                                <th style="width:5%">Qty</th>
                                <th style="width:5%">UM</th>
                                <th style="width:12%; white-space: nowrap;">Unit Price<br/>In SGD</th>
                                <th style="width:12%; white-space: nowrap;">Amount In<br/>SGD</th>
                            </tr>
                        </thead>
                        <tbody>
            """

            # Loop through invoice lines
            for line in self.invoice_line_ids:
                # Skip lines with zero quantity or non-product lines
                if line.quantity <= 0 or not line.product_id:
                    continue
                
                # Handle quantity formatting based on UOM
                uom = line.product_uom_id.name if line.product_uom_id else ''
                if uom.upper() in ['CM2', 'CM²']:
                    qty_str = f"{line.quantity:.2f}"
                else:
                    qty_str = f"{int(line.quantity)}"
                
                # Get S.No from the line or use a counter
                s_no = getattr(line, 's_no', '') or ''
                
                description = line.name or ''
                
                html_content += f"""
                    <tr style="border: 1px solid black;">
                        <td class="center" style="vertical-align: middle;">{s_no}</td>
                        <td class="description-cell">{description}</td>
                        <td class="center" style="vertical-align: middle;">{qty_str}</td>
                        <td class="center" style="vertical-align: middle;">{uom}</td>
                        <td class="right" style="vertical-align: middle; white-space: nowrap; padding-right: 4px;">${line.price_unit:.2f}</td>
                        <td class="right" style="vertical-align: middle; white-space: nowrap; padding-right: 4px;">{line.price_subtotal:.2f}</td>
                    </tr>
                """

            # Complete the HTML with footer
            html_content += f"""
                        </tbody>
                    </table>

                    <!-- Footer Section -->
                    <div class="footer">
                        <!-- Left Side: Terms -->
                        <div class="terms-section">
                            <h6><strong>Terms and Condition:</strong></h6><br/>
                            {self.narration or "Standard terms and conditions apply."}
                        </div>

                        <!-- Right Side: Totals -->
                        <div class="totals-section">
                            <table class="totals-table" style="border-collapse: collapse; border: none;">
                                <tr>
                                    <td style="text-align: left;"><strong>Subtotal</strong></td>
                                    <td class="right">${self.amount_untaxed:.2f}</td>
                                </tr>"""

            # Add individual tax rows from tax_breakdown
            if tax_breakdown:
                for tax_name, tax_amount in tax_breakdown.items():
                    html_content += f"""
                                <tr>
                                    <td style="text-align: left;"><strong>{tax_name}</strong></td>
                                    <td class="right">${tax_amount:.2f}</td>
                                </tr>"""
            else:
                # If no taxes found, show 0 tax
                html_content += f"""
                                <tr>
                                    <td style="text-align: left;"><strong>GST 9%</strong></td>
                                    <td class="right">0.00</td>
                                </tr>"""

            html_content += f"""
                                <tr>
                                    <td style="font-weight:bold; text-align: left;"><strong>Total</strong></td>
                                    <td class="right" style="font-weight:bold;">{self.amount_total:.2f}</td>
                                </tr>
                            </table>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """

            # Generate PDF
            buffer = BytesIO()
            HTML(string=html_content).write_pdf(buffer)

            pdf_data = buffer.getvalue()
            buffer.close()

            # Save as Odoo attachment
            attachment = self.env['ir.attachment'].create({
                'name': f'Invoice_{self.name}.pdf',
                'type': 'binary',
                'datas': base64.b64encode(pdf_data),
                'res_model': self._name,
                'res_id': self.id,
                'mimetype': 'application/pdf'
            })

            # Return download action
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{attachment.id}?download=true',
                'target': 'new',
            }

        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'PDF Export Error',
                    'message': f'Error generating PDF: {str(e)}',
                    'type': 'danger',
                    'sticky': True,
                }
            }
    
class inherit_delivery(models.Model):
    _inherit = 'stock.picking'

    po_number = fields.Char(string='PO Number')
    sef_number = fields.Char(string='SEF Number')
    job_code = fields.Char(string='Job Code')
    product_name = fields.Many2one('product.product', string='Product Name')
    atten=fields.Many2one('res.partner', string='Attn')

    note_delivery = fields.Text(string='Note' ,placeholder='Terms & Condition...')
    terms_conditions = fields.Many2one('terms.conditions',"Terms and Conditions")
    
    # @api.onchange('terms_conditions')
    # def _termscondition_delivery(self):
    #     for rec in self:
    #         rec.note_delivery = rec.terms_conditions.terms
    #     orm_sale_search = self.env['sale.order'].search([('name','=',self.origin)])
    #     list_1 = []
    #     list_2 = []
    #     count = 0
    #     for rec in orm_sale_search.order_line:
    #         list_1.append(rec.name)
    #     for rec_unit in orm_sale_search.order_line:
    #         list_2.append(rec_unit.product_uom.id)
    #     for lack in self.move_ids_without_package:
    #         lack.description_picking = list_1[count]
    #         lack.product_uom = list_2[count]
    #         count +=1
    
    # @api.model
    # def create(self,vals):
    #     result = super(inherit_delivery,self).create(vals)
    #     orm_sale = self.env['sale.order'].search([('name','=',result.origin)])
    #     if orm_sale:
    #         orm_project = self.env['project.project'].search([('sale_order_num','=',orm_sale.id)])
    #         if orm_project : 
    #             result.job_code = orm_project[0].service_number_project
            
    #         orm_dc = self.env["sale.order"].search([('name','=',result.origin)])
    #         if orm_dc:
    #             result.atten = orm_dc.atten
    #             result.note_delivery = orm_dc.note
    #             result.user_id = orm_dc.user_id
    #             result.product_name = orm_dc.product_name
    #     return result
    @api.model
    def create(self, vals):
        result = super(inherit_delivery, self).create(vals)
        if result.origin:
            try:
                orm_sale = self.env['sale.order'].search([('name', '=', result.origin)], limit=1)
                if orm_sale:
                    orm_project = self.env['project.project'].search([('sale_order_num', '=', orm_sale.id)], limit=1)
                    if orm_project and orm_project.service_number_project:
                        try:
                            result.job_code = orm_project.service_number_project
                        except:
                            result.job_code = False

                    # Handle atten field more safely
                    if orm_sale.atten and orm_sale.atten.id:
                        try:
                            # Verify the record exists before assigning
                            atten_record = self.env['res.partner'].browse(orm_sale.atten.id)
                            if atten_record.exists():
                                result.atten = orm_sale.atten.id
                        except:
                            result.atten = False
                    
                    # Handle other fields
                    try:
                        result.note_delivery = orm_sale.note or False
                        if orm_sale.user_id and orm_sale.user_id.id:
                            user_record = self.env['res.users'].browse(orm_sale.user_id.id)
                            if user_record.exists():
                                result.user_id = orm_sale.user_id.id
                        
                        if orm_sale.product_name and orm_sale.product_name.id:
                            product_record = self.env['product.product'].browse(orm_sale.product_name.id)
                            if product_record.exists():
                                result.product_name = orm_sale.product_name.id
                    except:
                        pass
            except Exception as e:
                _logger.info("Error in inherit_delivery create method: %s", str(e))

        return result





    def action_view_picking(self):
        """Override the smart button action to add error handling"""
        try:
            action = super(inherit_delivery, self).action_view_picking()
            # Ensure the action is valid
            if not action or not isinstance(action, dict):
                raise ValueError("Invalid action returned")
            return action
        except Exception as e:
            # If there's an error, return a safe empty action
            return {
                'type': 'ir.actions.act_window',
                'name': 'Operations',
                'res_model': 'stock.picking',
                'view_mode': 'tree,form',
                'domain': [('id', '=', False)],  # Empty domain
            }

    

    def action_export_delivery_pdf(self):
        """Export Delivery Order as PDF using WeasyPrint"""
        try:
            for picking in self:
                logo_data = ""
                if picking.company_id.logo:
                    logo_data = picking.company_id.logo.decode('utf-8') if isinstance(picking.company_id.logo, bytes) else picking.company_id.logo

                html_content = f"""
                <html>
                <head>
                    <style>
                        @page {{
                            size: A4;
                            margin-top: 5mm;
                            margin-bottom: 18mm;
                            margin-left: 7mm;
                            margin-right: 7mm;
                            @bottom-center {{
                                content: "This is a computer generated Delivery Order, No signature is required \\A Please Visit : {picking.company_id.website or ''} \\A Page " counter(page) " of " counter(pages);
                                white-space: pre;
                                font-size: 11px;
                                text-align: center;
                                border-top: 1px solid #000;
                                width: 100%;
                            }}
                        }}
                        body {{
                            font-family: Arial, sans-serif;
                            font-size: 13px;
                            color: #000;
                            margin: 0;
                        }}
                        h2 {{
                            text-align: center;
                            font-size: 22px;
                            color: #0000ff;
                            font-weight: bold;
                            margin-bottom: 8px;
                            line-height: 1.4;
                        }}
                        table {{
                            width: 100%;
                            border-collapse: collapse;
                        }}
                        td, th {{
                            padding: 5px;
                            font-size: 13px;
                        }}
                        .line-table {{
                            margin-top: 20px;
                        }}
                        .line-table th, .line-table td {{
                            border: 1px solid black;
                            padding: 6px;
                            text-align: left;
                            vertical-align: top;
                        }}
                        .line-table th {{
                            background-color: #f0f0f0;
                            text-align: center;
                        }}
                        .section-row {{
                            background-color: #e6f7ff;
                            font-weight: bold;
                            font-size: 14px;
                        }}
                        .note-row {{
                            font-style: italic;
                            background-color: #fafafa;
                        }}
                    </style>
                </head>
                <body>
                    <h2>Delivery Order /<br/>Job Completion Report</h2>

                    <!-- LOGO ON TOP -->
                    <div style="text-align: left; margin-bottom: 10px;">
                        {"<img src='data:image/png;base64," + logo_data + "' style='max-height:120px; max-width:280px;'/><br/>" if logo_data else ""}
                    </div>

                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <!-- LEFT SIDE: Company Details -->
                            <td style="width: 55%; vertical-align: top; padding-right: 10px;">
                                <strong>{picking.company_id.name}</strong><br/>
                                {picking.company_id.street or ''}<br/>
                                {picking.company_id.street2 + '<br/>' if picking.company_id.street2 else ''}
                                {(picking.company_id.city or '') + ' ' if picking.company_id.city else ''}
                                {(picking.company_id.state_id.name or '') + ' ' if picking.company_id.state_id else ''}
                                {picking.company_id.zip or ''}<br/>
                                {picking.company_id.country_id.name + '<br/>' if picking.company_id.country_id else ''}
                                <strong>Tel:</strong> {picking.company_id.phone or ''}<br/>
                                <strong>Email:</strong> {picking.company_id.email or ''}<br/>
                                <strong>Tax Reg No#:</strong> {picking.company_id.vat or ''}
                            </td>

                            <!-- RIGHT SIDE: Delivery Order Metadata -->
                            <td style="width: 45%; vertical-align: top;">
                                <table style="width: 100%; border: 1px solid black; border-collapse: collapse; font-size: 13px;">
                                    <tr>
                                        <td style="width: 40%; border: 1px solid black; font-weight: bold; padding: 5px;">DO Number</td>
                                        <td style="width: 60%; border: 1px solid black; padding: 5px;">{picking.name or ''}</td>
                                    </tr>
                                    <tr>
                                        <td style="border: 1px solid black; font-weight: bold; padding: 5px;">Date</td>
                                        <td style="border: 1px solid black; padding: 5px;">{picking.scheduled_date.strftime('%d/%m/%Y') if picking.scheduled_date else ''}</td>
                                    </tr>
                                    <tr>
                                        <td style="border: 1px solid black; font-weight: bold; padding: 5px;">PO Number</td>
                                        <td style="border: 1px solid black; padding: 5px;">{getattr(picking.sale_id, 'client_order_ref', '') or ''}</td>
                                    </tr>
                                    <tr>
                                        <td style="border: 1px solid black; font-weight: bold; padding: 5px;">Quotation</td>
                                        <td style="border: 1px solid black; padding: 5px;">{picking.origin or ''}</td>
                                    </tr>
                                    <tr>
                                        <td style="border: 1px solid black; font-weight: bold; padding: 5px;">Salesperson</td>
                                        <td style="border: 1px solid black; padding: 5px;">{picking.sale_id.user_id.name if picking.sale_id and picking.sale_id.user_id else ''}</td>
                                    </tr>
                                    <tr>
                                        <td style="border: 1px solid black; font-weight: bold; padding: 5px;">Job Code</td>
                                        <td style="border: 1px solid black; padding: 5px;">{getattr(picking, 'job_code', '') or ''}</td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                    </table>

                    <br/>

                    <!-- BILL TO / SHIP TO SIDE BY SIDE -->
                    <table style="width: 100%; margin-top: 10px;">
                        <tr>
                            <td style="width: 50%; vertical-align: top; padding-right: 15px;">
                                <strong>Bill To:</strong><br/>
                                {picking.partner_id.display_name if picking.partner_id else ''}<br/>
                                {picking.partner_id.street + '<br/>' if picking.partner_id and picking.partner_id.street else ''}
                                {picking.partner_id.city + ', ' if picking.partner_id and picking.partner_id.city else ''}
                                {picking.partner_id.zip or ''} {picking.partner_id.country_id.name if picking.partner_id and picking.partner_id.country_id else ''}<br/>
                            </td>
                            <td style="width: 50%; vertical-align: top;">
                                <strong>Ship To:</strong><br/>
                                {picking.partner_id.display_name if picking.partner_id else ''}<br/>
                                {picking.partner_id.street + '<br/>' if picking.partner_id and picking.partner_id.street else ''}
                                {picking.partner_id.city + ', ' if picking.partner_id and picking.partner_id.city else ''}
                                {picking.partner_id.zip or ''} {picking.partner_id.country_id.name if picking.partner_id and picking.partner_id.country_id else ''}<br/>
                            </td>
                        </tr>
                    </table>

                    <table class="line-table">
                        <thead>
                            <tr>
                                <th style="width:5%;">S.No</th>
                                <th style="width:55%;">Description</th>
                                <th style="width:10%;">Qty</th>
                                <th style="width:10%;">UM</th>
                                <th style="width:20%;">Remark</th>
                            </tr>
                        </thead>
                        <tbody>
                """

                line_counter = 0
                for move in picking.move_ids_without_package:
                    # Handle sections or notes
                    if hasattr(move, 'display_type') and move.display_type in ['line_section', 'line_note']:
                        section_class = "section-row" if move.display_type == 'line_section' else "note-row"
                        description = (move.name or '').strip()
                        html_content += f"""
                            <tr class="{section_class}">
                                <td colspan="5">{description}</td>
                            </tr>
                        """
                        continue

                    qty = move.product_uom_qty or 0
                    if qty <= 0:
                        continue

                    line_counter += 1
                    uom = move.product_uom.name or ''
                    description = (move.name or '').strip()
                    remark = getattr(move, 'remark', '') or ''

                    html_content += f"""
                        <tr>
                            <td style="text-align:center;">{line_counter}</td>
                            <td>{description}</td>
                            <td style="text-align:right;">{qty}</td>
                            <td style="text-align:center;">{uom}</td>
                            <td>{remark}</td>
                        </tr>
                    """

                html_content += f"""
                        </tbody>
                    </table>

                    <!-- TERMS AND CONDITIONS AND SIGNATURE -->
                    <div style="margin-top: 40px;">
                        <div style="text-align: left; font-size: 14px; margin-bottom: 30px;">
                            <strong>Terms and Condition:</strong><br/><br/>

                        </div>

                        <div style="text-align: right; font-size: 14px;">
                            <strong>Received in Good Order and Collection</strong><br/><br/>
                            <div style="border-top: 1px solid #000; width: 40%; margin: 10px 0 10px auto;"></div>
                            <strong>To: {picking.partner_id.name if picking.partner_id else ''}</strong><br/>
                            Please sign, stamp and date to confirm receipt
                        </div>
                    </div>
                </body>
                </html>
                """

                buffer = BytesIO()
                HTML(string=html_content).write_pdf(buffer)
                pdf_data = buffer.getvalue()
                buffer.close()

                attachment = picking.env['ir.attachment'].create({
                    'name': f'Delivery_{picking.name}.pdf',
                    'type': 'binary',
                    'datas': base64.b64encode(pdf_data),
                    'res_model': picking._name,
                    'res_id': picking.id,
                    'mimetype': 'application/pdf'
                })

                return {
                    'type': 'ir.actions.act_url',
                    'url': f'/web/content/{attachment.id}?download=true',
                    'target': 'new',
                }

        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'PDF Export Error',
                    'message': f'Error generating Delivery PDF: {str(e)}',
                    'type': 'danger',
                    'sticky': True,
                }
            }



class inherit_purchase(models.Model):
    _inherit = 'purchase.order'

    cash_terms = fields.Selection([('cash',"Cash"), ('cheque', "Cheque"), ('online', "Online Transfer")])
    cheque_no = fields.Char(string='Cheque No.')
    job_code = fields.Char(string='Job Code')
    
    def action_view_picking(self):
        """Override the smart button action to add error handling"""
        try:
            action = super(inherit_purchase, self).action_view_picking()
            # Ensure the action is valid
            if not action or not isinstance(action, dict):
                raise ValueError("Invalid action returned")
            return action
        except Exception as e:
            # If there's an error, return a safe empty action
            return {
                'type': 'ir.actions.act_window',
                'name': 'Receipts',
                'res_model': 'stock.picking',
                'view_mode': 'tree,form',
                'domain': [('id', '=', False)],  # Empty domain
            }

    def action_export_purchase_pdf(self):
        """Export purchase order as PDF using WeasyPrint with fixed layout and footer"""
        try:
            # Get company logo as base64
            logo_data = ""
            if self.company_id.logo:
                logo_data = self.company_id.logo.decode('utf-8') if isinstance(self.company_id.logo, bytes) else self.company_id.logo

            # HTML content with fixed layout and proper footer
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8"/>
                <style>
                    @page {{
                        size: A4;
                        margin-top: 15mm;
                        margin-bottom: 25mm;
                        margin-left: 10mm;
                        margin-right: 10mm;

                        @bottom-center {{
                            content: "This is a computer generated Purchase Order, No signature is required \\A Phone: {self.company_id.phone or ''} \\9 Page " counter(page) " of " counter(pages) " \\9 Website: {self.company_id.website or ''}";
                            font-size: 10px;
                            text-align: center;
                            width: 100%;
                            white-space: pre;
                            border-top: 1px solid #000;
                            padding-top: 5px;
                        }}
                    }}

                    body {{
                        font-family: 'Arial', sans-serif;
                        margin: 0;
                        padding: 0;
                        color: #000;
                        font-size: 12px;
                        line-height: 1.2;
                    }}

                    .header-section {{
                        width: 100%;
                        margin-bottom: 15px;
                        page-break-inside: avoid;
                    }}

                    .logo-company-row {{
                        display: table;
                        width: 100%;
                    }}

                    .logo-section {{
                        display: table-cell;
                        width: 40%;
                        vertical-align: top;
                        padding-right: 20px;
                    }}

                    .logo-section img {{
                        max-width: 100%;
                        max-height: 60px;
                        height: auto;
                    }}

                    .company-section {{
                        display: table-cell;
                        width: 60%;
                        vertical-align: top;
                        text-align: right;
                    }}

                    .company-info {{
                        font-size: 11px;
                        font-weight: bold;
                        line-height: 1.3;
                    }}

                    .title {{
                        font-size: 20px;
                        color: black;
                        text-align: center;
                        text-decoration: underline;
                        font-weight: bold;
                        margin: 15px 0 15px 0;
                        page-break-inside: avoid;
                    }}

                    .info-table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin-bottom: 10px;
                        font-size: 11px;
                        page-break-inside: avoid;
                    }}

                    .info-table th, .info-table td {{
                        border: 1px solid black;
                        padding: 4px;
                        text-align: left;
                        vertical-align: top;
                    }}

                    .info-table th {{
                        font-weight: bold;
                        background-color: #f5f5f5;
                        width: 15%;
                    }}

                    .description-row {{
                        width: 100%;
                        border-collapse: collapse;
                        margin-bottom: 10px;
                        page-break-inside: avoid;
                    }}

                    .description-row td {{
                        border: 1px solid black;
                        padding: 5px;
                        font-size: 11px;
                        font-weight: bold;
                    }}

                    .items-table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin-bottom: 10px;
                        font-size: 10px;
                    }}

                    .items-table thead th {{
                        border: 1px solid black;
                        padding: 6px 3px;
                        font-weight: bold;
                        text-align: center;
                        background-color: #f5f5f5;
                        font-size: 10px;
                    }}

                    .items-table tbody td {{
                        border: 1px solid black;
                        padding: 4px 3px;
                        font-size: 10px;
                        vertical-align: top;
                    }}

                    /* Ensure table headers repeat on each page */
                    .items-table thead {{
                        display: table-header-group;
                    }}

                    .items-table tbody {{
                        display: table-row-group;
                    }}

                    .text-center {{ text-align: center; }}
                    .text-right {{ text-align: right; }}
                    .text-left {{ text-align: left; }}

                    .totals-row {{
                        page-break-inside: avoid;
                    }}

                    .terms-section {{
                        margin-top: 15px;
                        page-break-inside: avoid;
                    }}

                    .terms-table {{
                        width: 100%;
                        border-collapse: collapse;
                    }}

                    .terms-table td {{
                        border: 1px solid black;
                        padding: 8px;
                        font-size: 11px;
                    }}

                    .signature-section {{
                        margin-top: 20px;
                        text-align: right;
                        font-size: 11px;
                        page-break-inside: avoid;
                    }}

                    /* Prevent unnecessary page breaks */
                    .items-table tr {{
                        page-break-inside: avoid;
                    }}
                </style>
            </head>
            <body>
                <!-- Header Section with Logo and Company Info -->
                <div class="header-section">
                    <div class="logo-company-row">
                        <div class="logo-section">
                            {"<img src='data:image/png;base64," + logo_data + "' alt='Company Logo'/>" if logo_data else ""}
                        </div>
                        <div class="company-section">
                            <div class="company-info">
                                {self.company_id.name or ''}<br/>
                                {(self.company_id.street + ',') if self.company_id.street else ''}<br/>
                                {(self.company_id.street2 + ',') if self.company_id.street2 else ''}
                                {(self.company_id.city + ', ') if self.company_id.city else ''}{self.company_id.zip or ''}<br/>
                                {self.company_id.country_id.name if self.company_id.country_id else ''}<br/>
                                {('GST: ' + self.company_id.vat) if self.company_id.vat else ''}<br/>
                                {('Email: ' + self.company_id.email) if self.company_id.email else ''}
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Title -->
                <div class="title">Purchase Order</div>

                <!-- Info Table -->
                <table class="info-table">
                    <tr>
                        <th>Contact</th>
                        <td style="width: 35%;">{self.partner_id.name or ''}</td>
                        <th>Purchase Order No.</th>
                        <td style="width: 35%;">{self.name or ''}</td>
                    </tr>
                    <tr>
                        <th>Address</th>
                        <td>
                            {self.partner_id.street or ''}{('<br/>' + self.partner_id.street2) if self.partner_id.street2 else ''}<br/>
                            {(self.partner_id.city + ' - ') if self.partner_id.city else ''}{self.partner_id.state_id.name if self.partner_id.state_id else ''}<br/>
                            {(self.partner_id.country_id.name + ' - ') if self.partner_id.country_id else ''}{self.partner_id.zip or ''}
                        </td>
                        <th>Date</th>
                        <td>{self.date_order.strftime('%Y-%m-%d') if self.date_order else ''}</td>
                    </tr>
                    <tr>
                        <th>Phone No</th>
                        <td>{self.partner_id.phone or ''}</td>
                        <th>Your Ref.</th>
                        <td>{self.partner_ref or ''}</td>
                    </tr>
                    <tr>
                        <th>Email</th>
                        <td>{self.partner_id.email or ''}</td>
                        <th>Job Code</th>
                        <td>{getattr(self, 'job_code', '') or ''}</td>
                    </tr>
                </table>

                <!-- Description -->
                <table class="description-row">
                    <tr>
                        <td>We are pleased to provide the following purchase order as per our request</td>
                    </tr>
                </table>

                <!-- Main Items Table -->
                <table class="items-table">
                    <thead>
                        <tr>
                            <th style="width: 6%;">ITEM</th>
                            <th style="width: 50%;">DESCRIPTION</th>
                            <th style="width: 8%;">QTY</th>
                            <th style="width: 8%;">UM</th>
                            <th style="width: 14%;">UNIT PRICE<br/>S$({self.currency_id.name or 'SGD'})</th>
                            <th style="width: 14%;">TOTAL PRICE<br/>S$({self.currency_id.name or 'SGD'})</th>
                        </tr>
                    </thead>
                    <tbody>
            """

            # Add order lines
            line_count = 0
            
            for line in self.order_line:
                # Get quantity
                qty_value = getattr(line, 'product_qty', 0) or getattr(line, 'product_uom_qty', 0)
                
                if qty_value <= 0:
                    continue
                    
                line_count += 1
                
                # Get serial number
                s_no = getattr(line, 's_nodd', '') or str(line_count)
                
                # Get description
                description = line.name or (line.product_id.name if line.product_id else 'Product description not available')
                description = str(description).replace('\n', '<br/>').replace('\r', '')
                
                # Format quantity
                if qty_value == int(qty_value):
                    qty_display = int(qty_value)
                else:
                    qty_display = f"{qty_value:.2f}"
                
                # Get unit of measure
                unit_name = 'Units'
                if hasattr(line, 'product_uom') and line.product_uom:
                    unit_name = line.product_uom.name
                
                # Get prices
                unit_price = getattr(line, 'price_unit', 0) or 0
                subtotal = getattr(line, 'price_subtotal', 0) or (unit_price * qty_value)
                
                html_content += f"""
                    <tr>
                        <td class="text-center">{s_no}</td>
                        <td class="text-left">{description}</td>
                        <td class="text-right">{qty_display}</td>
                        <td class="text-center">{unit_name}</td>
                        <td class="text-right">S${unit_price:.2f}</td>
                        <td class="text-right">S${subtotal:.2f}</td>
                    </tr>
                """

            # If no lines found
            if line_count == 0:
                html_content += f"""
                    <tr>
                        <td colspan="6" style="padding: 15px; text-align: center;">
                            No purchase order lines found.
                        </td>
                    </tr>
                """

            # Complete the HTML with totals and footer
            html_content += f"""
                        <!-- Totals Section -->
                        <tr class="totals-row">
                            <td colspan="4" style="border: none; background: white;"></td>
                            <td style="font-weight: bold; background-color: #f5f5f5;">Sub Total</td>
                            <td class="text-right" style="background-color: #f5f5f5;">S${self.amount_untaxed:.2f}</td>
                        </tr>
                        <tr class="totals-row">
                            <td colspan="4" style="border: none; background: white;"></td>
                            <td style="font-weight: bold; background-color: #f5f5f5;">Taxes</td>
                            <td class="text-right" style="background-color: #f5f5f5;">S${self.amount_tax:.2f}</td>
                        </tr>
                        <tr class="totals-row">
                            <td colspan="4" style="border: none; background: white;"></td>
                            <td style="font-weight: bold; background-color: #f0f0f0;">Total</td>
                            <td class="text-right" style="font-weight: bold; background-color: #f0f0f0;">S${self.amount_total:.2f}</td>
                        </tr>
                    </tbody>
                </table>

                <!-- Terms and Conditions -->
                <div class="terms-section">
                    <table class="terms-table">
                        <tr>
                            <td>
                                <strong>TERMS AND CONDITIONS:</strong><br/><br/>
                                {self.notes or 'Standard terms and conditions apply.'}
                            </td>
                        </tr>
                    </table>
                </div>

                <!-- Signature Section -->
                <div class="signature-section">
                    <br/><br/>
                    <div style="margin-right: 20px;">
                        <div>_________________________</div>
                        <div style="margin-top: 5px; font-weight: bold;">Authorized Signature</div>
                        <div style="margin-top: 5px;">{self.company_id.name or 'COMPANY NAME'}</div>
                    </div>
                </div>
            </body>
            </html>
            """

            # Generate PDF
            buffer = BytesIO()
            HTML(string=html_content).write_pdf(buffer)

            pdf_data = buffer.getvalue()
            buffer.close()

            # Save as Odoo attachment
            attachment = self.env['ir.attachment'].create({
                'name': f'Purchase_Order_{self.name}.pdf',
                'type': 'binary',
                'datas': base64.b64encode(pdf_data),
                'res_model': self._name,
                'res_id': self.id,
                'mimetype': 'application/pdf'
            })

            # Return download action
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{attachment.id}?download=true',
                'target': 'new',
            }

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            _logger.error(f"PDF Export Error: {error_details}")
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'PDF Export Error',
                    'message': f'Error generating PDF: {str(e)}',
                    'type': 'danger',
                    'sticky': True,
                }
            }
        
    
class inherit_expenses(models.Model):
    _inherit = 'hr.expense'

    name_partner = fields.Many2one('res.partner', string='Name', domain="[('supplier_rank', '=', '1')]")

# class inherit_partner(models.Model):
#     _inherit = 'res.partner'

#     vendor = fields.Boolean(string='Vendor')

class TermsConditions(models.Model):
    _name = 'terms.conditions'
    _rec_name = 'conditions'

    conditions = fields.Char("Name")
    terms = fields.Text('Terms and Conditions')