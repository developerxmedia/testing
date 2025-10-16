from odoo import fields, models, api, _
from io import BytesIO
import base64
from weasyprint import HTML

class InheritSalesOrderBOM(models.Model):
    _inherit = 'sale.order'

    bom_count = fields.Integer(string='Bill of Materials', compute='sample_demo')   

    def action_confirm(self):
        res = super().action_confirm()
        for order in self:
            for picking in order.picking_ids:
                picking.terms_conditions = order.terms_conditions
        return res

    def sample_demo(self):
        for record in self:
            record.bom_count = self.env['mrp.bom'].search_count([('sale_order_id', '=', record.id)])

    def action_bom(self):
        list1 = []
        for line in self.order_line:
            list1.append(line.product_id.product_tmpl_id.id)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Bill of Materials',
            'res_model': 'mrp.bom',
            'domain': [('product_tmpl_id', 'in', list1)],
            'view_mode': 'tree,form',
            'view_type': 'form',
        }
    

    def action_export_quotation_pdf(self):
        """Export quotation as PDF using WeasyPrint matching QWeb template structure"""
        try:
            # Get company logo as base64
            logo_data = ""
            if self.company_id.logo:
                logo_data = self.company_id.logo.decode('utf-8') if isinstance(self.company_id.logo, bytes) else self.company_id.logo

            # Get tax breakdown from sales order's computed taxes
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
            
            # Method 2: If tax_totals doesn't work, try account_move approach for computed taxes
            if not tax_breakdown:
                # Look for any related invoices or use order's tax computation
                try:
                    # Get tax details from the order's _get_tax_totals method if available
                    if hasattr(self, '_get_tax_totals'):
                        tax_totals_data = self._get_tax_totals()
                        if tax_totals_data and 'groups_by_subtotal' in tax_totals_data:
                            for subtotal_group in tax_totals_data['groups_by_subtotal'].values():
                                for tax_group in subtotal_group:
                                    tax_name = tax_group.get('tax_group_name', 'Tax')
                                    tax_amount = tax_group.get('tax_group_amount', 0)
                                    if tax_amount > 0:
                                        tax_breakdown[tax_name] = tax_amount
                except:
                    pass
            
            # Method 3: Fallback to total tax amount if no breakdown available
            if not tax_breakdown and self.amount_tax > 0:
                tax_breakdown['Tax'] = self.amount_tax

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
        content: "This is a computer generated Quotation, No signature is required \A Please Visit: {self.company_id.website or ''} \A Page " counter(page) " of " counter(pages);
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
                        font-size: 13px;
                        vertical-align: top;
                    }}
                    .center {{
                        text-align: center;
                    }}
                    .right {{
                        text-align: right;
                    }}
                    .description-cell {{
                        word-wrap: break-word;
                        white-space: normal;
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
                        max-width: 240px;
                        margin-left: auto;
                    }}
                    .totals-table td {{
                        padding: 3px 5px;
                        border: none;
                        border-top: 1px solid #000;
                    }}
                    .product-name {{
                        margin: 5px 0 0 0;
                        color: orange;
                        text-align:left;
                        font-size: 15px;
                    }}
                    .section-row {{
                        background-color: #e8f4f8;
                        font-weight: bold;
                        font-size: 14px;
                    }}
                    .note-row {{
                        background-color: #f8f8f8;
                        font-style: italic;
                        font-size: 12px;
                    }}
                </style>
            </head>
            <body>
                <div class="page">
                    <!-- Title -->
                    <h4 style="color:#0000ff; margin-bottom:10px; font-size:26px; font-weight:900; letter-spacing:.3px;">Quotation</h4>

                    <!-- Header Section -->
                    <table class="header-outer">
                        <tr>
                            <!-- Left: Company Info with Logo -->
                            <td style="width: 55%; vertical-align: top; padding-right: 10px;">
                                {"<img src='data:image/png;base64," + logo_data + "' style='max-height:80px; max-width:200px; margin-bottom:10px;'/><br/>" if logo_data else ""}
                                <div class="company-info">
                                    <strong>{self.company_id.name or ''}</strong><br/>
                                    {self.company_id.street or ''}<br/>
                                    {self.company_id.street2 + '<br/>' if self.company_id.street2 else ''}
                                    {(self.company_id.city or '') + ' ' if self.company_id.city else ''}
                                    {(self.company_id.state_id.name or '') + ' ' if self.company_id.state_id else ''}
                                    {self.company_id.zip or ''}<br/>
                                    {self.company_id.country_id.name + '<br/>' if self.company_id.country_id else ''}
                                    <strong>Tel:</strong> {self.company_id.phone or ''}<br/>
                                    <strong>Email:</strong> {self.company_id.email or ''}<br/>
                                    <strong>Tax Reg No#:</strong> {self.company_id.vat or ''}
                                </div>
                            </td>
                            
                            <!-- Right: Meta Information Table -->
                            <td style="vertical-align: top;">
                                <table class="meta-table">
                                    <tr>
                                        <td style="white-space: nowrap;">Quotation #</td>
                                        <td>{self.name or ''}</td>
                                    </tr>
                                    <tr>
                                        <td style="white-space: nowrap;">Date</td>
                                        <td>{self.write_date.strftime('%Y-%m-%d') if self.write_date else ''}</td>
                                    </tr>
                                    <tr>
                                        <td style="white-space: nowrap;">Credit Terms</td>
                                        <td>{getattr(self, 'cash_term_paid', '') or ''}</td>
                                    </tr>
                                    <tr>
                                        <td style="white-space: nowrap;">Salesperson REF.</td>
                                        <td>{self.user_id.name if self.user_id else ''}</td>
                                    </tr>
                                    <tr>
                                        <td style="white-space: nowrap;">RFQ Number</td>
                                        <td>{getattr(self, 'rfq_num', '') or ''}</td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        
                        <!-- Customer Information -->
                        <tr>
                            <td colspan="2" class="customer-info">
                                <strong>To:</strong><br/>
                                {self.partner_id.name if self.partner_id else ''}<br/>
                                {self.partner_id.street + '<br/>' if self.partner_id and self.partner_id.street else ''}
                                {self.partner_id.street2 + '<br/>' if self.partner_id and self.partner_id.street2 else ''}
                                {(self.partner_id.city or '') + ' ' if self.partner_id and self.partner_id.city else ''}
                                {(self.partner_id.state_id.name or '') + ' ' if self.partner_id and self.partner_id.state_id else ''}
                                {self.partner_id.zip + '<br/>' if self.partner_id and self.partner_id.zip else ''}
                                {self.partner_id.country_id.name + '<br/>' if self.partner_id and self.partner_id.country_id else ''}
                                <br/>
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
                                <th style="width:61%">Descriptions</th>
                                <th style="width:5%">Qty</th>
                                <th style="width:5%">UOM</th>
                                <th style="width:12%; white-space: nowrap;">Unit Price<br/>In SGD</th>
                                <th style="width:12%; white-space: nowrap;">Amount In<br/>SGD</th>
                            </tr>
                        </thead>
                        <tbody>
            """

            # Loop through order lines with proper section handling
            line_counter = 0  # Only count actual product lines, not sections
            
            for line in self.order_line:
                # Check if this is a section/note (display_type exists in Odoo)
                is_section = hasattr(line, 'display_type') and line.display_type in ['line_section', 'line_note']
                
                if is_section:
                    # Handle sections/notes without line numbers
                    section_class = ""
                    if hasattr(line, 'display_type') and line.display_type == 'line_section':
                        # Section header styling
                        section_class = "section-row"
                    else:
                        # Note styling  
                        section_class = "note-row"
                    
                    description = line.name or ''
                    description = ' '.join(description.split())  # Clean extra whitespace
                    
                    html_content += f"""
                        <tr class="{section_class}">
                            <td colspan="6" style="border: 1px solid black; padding: 8px; text-align: left;">
                                {description}
                            </td>
                        </tr>
                    """
                else:
                    # Handle regular product lines
                    qty = line.product_uom_qty or 0
                    
                    # Skip lines with zero quantity
                    if qty <= 0:
                        continue
                        
                    line_counter += 1  # Only increment for actual product lines
                    
                    uom = line.product_uom.name if line.product_uom else ''
                    qty_str = f"{qty:.2f}" if uom == 'cm2' else f"{int(qty)}"
                    
                    # Use line_counter for S.No instead of any stored field
                    s_no = str(line_counter)
                    
                    description = line.name or ''
                    description = ' '.join(description.split())  # Clean extra whitespace
                    
                    html_content += f"""
                        <tr>
                            <td class="center">{s_no}</td>
                            <td class="description-cell">{description}</td>
                            <td class="center" style="vertical-align: middle;">{qty_str}</td>
                            <td class="center" style="vertical-align: middle;">{uom}</td>
                            <td class="right" style="vertical-align: middle;">S${line.price_unit:.2f}</td>
                            <td class="right" style="vertical-align: middle;">S${line.price_subtotal:.2f}</td>
                        </tr>
                    """

            # Complete the HTML with footer - using dynamic tax breakdown
            html_content += f"""
                        </tbody>
                    </table>

                    <!-- Footer Section -->
                    <div class="footer">
                        <!-- Left Side: Terms -->
                        <div class="terms-section">
                            <strong>Terms and Condition:</strong><br/>
                            {self.note or "Standard terms and conditions apply."}
                        </div>

                        <!-- Right Side: Totals -->
                        <div class="totals-section">
                            <table class="totals-table">
                                <tr>
                                    <td><strong>Subtotal</strong></td>
                                    <td class="right">S${self.amount_untaxed:.2f}</td>
                                </tr>"""

            # Add individual tax rows from tax_breakdown
            if tax_breakdown:
                for tax_name, tax_amount in tax_breakdown.items():
                    html_content += f"""
                                <tr>
                                    <td><strong>{tax_name}:</strong></td>
                                    <td class="right">S${tax_amount:.2f}</td>
                                </tr>"""
            else:
                # If no taxes found, show 0 tax
                html_content += f"""
                                <tr>
                                    <td><strong>Tax:</strong></td>
                                    <td class="right">0.00</td>
                                </tr>"""

            html_content += f"""
                                <tr>
                                    <td style="font-weight:bold;"><strong>Total</strong></td>
                                    <td class="right" style="font-weight:bold;">S${self.amount_total:.2f}</td>
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
                'name': f'Quotation_{self.name}.pdf',
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



