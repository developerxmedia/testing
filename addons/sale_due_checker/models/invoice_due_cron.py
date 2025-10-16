from odoo import fields, models, api
from datetime import date
import requests
import logging
import io
import base64

_logger = logging.getLogger(__name__)

class AccountMoveDueChecker(models.Model):
    _inherit = 'account.move'
    
    mail_replied = fields.Boolean(string='Customer Replied to Mail', default=False)
    
    @api.model
    def cron_check_unpaid_invoices(self):
        today = date.today()

        partners = self.env['res.partner'].search([])

        for partner in partners:
            invoices = self.search([
                ('partner_id', '=', partner.id),
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('amount_residual', '>', 0),
                ('invoice_date_due', '<=', today),
                ('mail_replied', '=', False),
            ])

            if not invoices:
                continue

            total_outstanding = sum(inv.amount_residual for inv in invoices)
            pdf_base64 = self.generate_combined_invoice_pdf(invoices)

            payload = {
                "name": partner.name or "",
                "email": partner.email or "",
                "total_outstanding": float(total_outstanding),
                "pdf_base64": pdf_base64,
            }

            try:
                response = requests.post(
                    "http://143.1.1.33:8003/api/send-mail",
                    json=payload,
                    timeout=10
                )
                if response.status_code == 200:
                    _logger.info(f"[OK] Sent unpaid invoices for {partner.name}")
                else:
                    _logger.warning(f"[WARN] Failed to send invoices for {partner.name}, Status: {response.status_code}")
            except Exception as e:
                _logger.error(f"[ERROR] Could not send data for {partner.name}: {str(e)}")
                
    def generate_combined_invoice_pdf(self, invoices):
        """Generate a professional PDF statement using ReportLab directly"""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
            
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer, 
                pagesize=A4,
                rightMargin=40,
                leftMargin=40,
                topMargin=50,
                bottomMargin=50
            )
            
            # Get styles
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=20,
                alignment=TA_CENTER,
                textColor=colors.darkblue
            )
            
            header_style = ParagraphStyle(
                'CustomHeader',
                parent=styles['Heading2'],
                fontSize=13,
                spaceAfter=15,
                alignment=TA_LEFT
            )
            
            story = []
            
            # Title
            title = Paragraph("OUTSTANDING INVOICES STATEMENT", title_style)
            story.append(title)
            story.append(Spacer(1, 15))
            
            # Customer Information
            if invoices:
                partner = invoices[0].partner_id
                customer_info = f"""
                <b>Customer:</b> {partner.name or 'N/A'}<br/>
                <b>Email:</b> {partner.email or 'N/A'}<br/>
                <b>Phone:</b> {partner.phone or 'N/A'}<br/>
                <b>Statement Date:</b> {date.today().strftime('%B %d, %Y')}
                """
                customer_para = Paragraph(customer_info, styles['Normal'])
                story.append(customer_para)
                story.append(Spacer(1, 20))
            
            # Invoice Table Header
            invoice_header = Paragraph("Invoice Details", header_style)
            story.append(invoice_header)
            
            # Get currency symbol and format it properly
            currency_symbol = self._get_currency_symbol(invoices[0] if invoices else None)
            
            # Main invoice data table
            table_data = [
                ['Invoice\nNumber', 'Invoice\nDate', 'Due\nDate', 'Total\nAmount', 'Outstanding\nAmount', 'Days\nOverdue', 'Payment\nStatus']
            ]
            
            total_outstanding = 0.0
            today = date.today()
            
            for invoice in invoices:
                due_date = invoice.invoice_date_due or invoice.invoice_date
                days_overdue = (today - due_date).days if due_date and due_date < today else 0
                
                # Determine payment status
                payment_status = self._get_payment_status(invoice)
                
                table_data.append([
                    str(invoice.name or ''),
                    invoice.invoice_date.strftime('%Y-%m-%d') if invoice.invoice_date else '',
                    due_date.strftime('%Y-%m-%d') if due_date else '',
                    f"{currency_symbol}{invoice.amount_total:,.2f}",
                    f"{currency_symbol}{invoice.amount_residual:,.2f}",
                    str(days_overdue) if days_overdue > 0 else '0',
                    payment_status
                ])
                
                total_outstanding += invoice.amount_residual
            
            # Create main table with proper column widths (added one more column)
            col_widths = [1.5*inch, 0.9*inch, 0.9*inch, 1*inch, 1*inch, 0.7*inch, 1*inch]
            table = Table(table_data, colWidths=col_widths, repeatRows=1)
            
            # Calculate total table width for the total box
            total_table_width = sum(col_widths)
            table = Table(table_data, colWidths=col_widths, repeatRows=1)
            
            # Style the main table
            table.setStyle(TableStyle([
                # Header row styling
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),  # Center vertically for multi-line headers
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 7),  # Reduced font size for headers
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('TOPPADDING', (0, 0), (-1, 0), 6),
                
                # Data rows styling
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ALIGN', (3, 1), (4, -1), 'RIGHT'),  # Right align amounts
                ('ALIGN', (5, 1), (5, -1), 'CENTER'),  # Center align days overdue
                ('ALIGN', (6, 1), (6, -1), 'CENTER'),  # Center align payment status
                ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),  # Center vertically for data
                
                # Grid and borders
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('LINEBELOW', (0, 0), (-1, 0), 2, colors.darkblue),
                
                # Padding
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('LEFTPADDING', (0, 0), (-1, -1), 3),
                ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ]))
            
            story.append(table)
            story.append(Spacer(1, 15))
            
            # Total Outstanding row - same width as main table
            total_data = [[f"TOTAL OUTSTANDING: {currency_symbol}{total_outstanding:,.2f}"]]
            total_table = Table(total_data, colWidths=[total_table_width])  # Same width as main table
            total_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 15),
                ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ]))
            
            story.append(total_table)
            story.append(Spacer(1, 25))
            
            # Summary and footer
            summary_text = f"""
            <b>PAYMENT SUMMARY:</b><br/>
            Total Outstanding Amount: <b>{currency_symbol}{total_outstanding:,.2f}</b><br/>
            Number of Outstanding Invoices: <b>{len(invoices)}</b><br/>
            <br/>
            <b>PAYMENT INSTRUCTIONS:</b><br/>
            Please remit payment for the above outstanding amount at your earliest convenience.<br/>
            All payments should reference the invoice number(s) listed above.<br/>
            <br/>
            For any questions regarding this statement, please contact our accounts receivable department.<br/>
            <br/>
            <i>This statement was generated automatically on {date.today().strftime('%B %d, %Y')}.</i>
            """
            
            summary_para = Paragraph(summary_text, styles['Normal'])
            story.append(summary_para)
            
            # Build the PDF
            doc.build(story)
            
            # Get PDF data
            pdf_data = buffer.getvalue()
            buffer.close()
            
            # Validate PDF data
            if len(pdf_data) < 100:  # PDF should be at least 100 bytes
                _logger.error("Generated PDF is too small, likely corrupted")
                return self._generate_simple_text_pdf(invoices)
            
            # Check PDF header
            if not pdf_data.startswith(b'%PDF'):
                _logger.error("Generated data is not a valid PDF")
                return self._generate_simple_text_pdf(invoices)
            
            encoded_pdf = base64.b64encode(pdf_data).decode('utf-8')
            _logger.info(f"Successfully generated PDF with {len(pdf_data)} bytes")
            return encoded_pdf
            
        except ImportError as e:
            _logger.error(f"ReportLab not available: {str(e)}")
            return self._generate_simple_text_pdf(invoices)
        except Exception as e:
            _logger.error(f"Error generating PDF: {str(e)}")
            return self._generate_simple_text_pdf(invoices)
    
    def _get_payment_status(self, invoice):
        """Get payment status for the invoice"""
        if invoice.amount_residual <= 0:
            return "Paid"
        elif invoice.amount_residual == invoice.amount_total:
            return "Unpaid"
        else:
            return "Partial"
    
    def _get_currency_symbol(self, invoice):
        """Get a safe currency symbol that displays properly in PDF"""
        if not invoice or not invoice.currency_id:
            return "Rs. "  # Default to Rs. for Indian Rupees
        
        # Map common currency symbols to safe alternatives
        currency_map = {
            '₹': 'Rs. ',
            '$': 'USD ',
            '€': 'EUR ',
            '£': 'GBP ',
            '¥': 'JPY ',
            'د.إ': 'AED ',
            '₨': 'Rs. ',
        }
        
        symbol = invoice.currency_id.symbol
        if symbol in currency_map:
            return currency_map[symbol]
        else:
            # If symbol is not recognized, use currency name
            return f"{invoice.currency_id.name} "
    
    def _generate_simple_text_pdf(self, invoices):
        """Generate a minimal PDF using basic reportlab functionality"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            
            buffer = io.BytesIO()
            p = canvas.Canvas(buffer, pagesize=A4)
            width, height = A4
            
            # Get currency symbol
            currency_symbol = self._get_currency_symbol(invoices[0] if invoices else None)
            
            # Title
            p.setFont("Helvetica-Bold", 16)
            p.drawCentredText(width/2, height - 80, "OUTSTANDING INVOICES STATEMENT")
            
            # Customer info
            y_position = height - 120
            if invoices:
                partner = invoices[0].partner_id
                p.setFont("Helvetica", 11)
                p.drawString(60, y_position, f"Customer: {partner.name}")
                y_position -= 20
                p.drawString(60, y_position, f"Email: {partner.email or 'N/A'}")
                y_position -= 20
                p.drawString(60, y_position, f"Date: {date.today().strftime('%Y-%m-%d')}")
                y_position -= 40
            
            # Table headers with proper spacing
            p.setFont("Helvetica-Bold", 8)
            p.drawString(50, y_position, "Invoice #")
            p.drawString(120, y_position, "Date")
            p.drawString(170, y_position, "Due Date")
            p.drawString(220, y_position, "Total")
            p.drawString(280, y_position, "Outstanding")
            p.drawString(350, y_position, "Days")
            p.drawString(380, y_position, "Status")
            y_position -= 15
            
            # Draw line
            p.line(50, y_position, 450, y_position)
            y_position -= 15
            
            # Invoice data
            p.setFont("Helvetica", 7)
            total_outstanding = 0.0
            
            for invoice in invoices:
                if y_position < 100:  # Start new page if needed
                    p.showPage()
                    y_position = height - 50
                
                due_date = invoice.invoice_date_due or invoice.invoice_date
                days_overdue = (date.today() - due_date).days if due_date and due_date < date.today() else 0
                payment_status = self._get_payment_status(invoice)
                
                p.drawString(50, y_position, str(invoice.name or ''))
                p.drawString(120, y_position, invoice.invoice_date.strftime('%m/%d') if invoice.invoice_date else '')
                p.drawString(170, y_position, due_date.strftime('%m/%d') if due_date else '')
                p.drawString(220, y_position, f"{currency_symbol}{invoice.amount_total:,.0f}")
                p.drawString(280, y_position, f"{currency_symbol}{invoice.amount_residual:,.0f}")
                p.drawString(350, y_position, str(days_overdue))
                p.drawString(380, y_position, payment_status)
                
                total_outstanding += invoice.amount_residual
                y_position -= 15
            
            # Total line
            y_position -= 10
            p.line(50, y_position, 450, y_position)
            y_position -= 20
            
            # Total Outstanding - right aligned
            p.setFont("Helvetica-Bold", 12)
            total_text = f"TOTAL OUTSTANDING: {currency_symbol}{total_outstanding:,.2f}"
            text_width = p.stringWidth(total_text, "Helvetica-Bold", 12)
            p.drawString(450 - text_width, y_position, total_text)
            
            p.save()
            
            pdf_data = buffer.getvalue()
            buffer.close()
            
            if pdf_data and pdf_data.startswith(b'%PDF'):
                encoded_pdf = base64.b64encode(pdf_data).decode('utf-8')
                _logger.info(f"Generated simple PDF with {len(pdf_data)} bytes")
                return encoded_pdf
            else:
                _logger.error("Simple PDF generation failed")
                return self._generate_fallback_response(invoices)
                
        except Exception as e:
            _logger.error(f"Error in simple PDF generation: {str(e)}")
            return self._generate_fallback_response(invoices)
    
    def _generate_fallback_response(self, invoices):
        """Generate a text-based response as last resort"""
        try:
            content = "OUTSTANDING INVOICES STATEMENT\n"
            content += "=" * 50 + "\n\n"
            
            # Get currency symbol
            currency_symbol = self._get_currency_symbol(invoices[0] if invoices else None)
            
            if invoices:
                partner = invoices[0].partner_id
                content += f"Customer: {partner.name}\n"
                content += f"Email: {partner.email or 'N/A'}\n"
                content += f"Date: {date.today().strftime('%Y-%m-%d')}\n\n"
            
            content += "Invoice Details:\n"
            content += "-" * 50 + "\n"
            
            total_outstanding = 0.0
            for invoice in invoices:
                content += f"Invoice: {invoice.name}\n"
                content += f"Date: {invoice.invoice_date}\n"
                content += f"Due Date: {invoice.invoice_date_due}\n"
                content += f"Total: {currency_symbol}{invoice.amount_total:,.2f}\n"
                content += f"Outstanding: {currency_symbol}{invoice.amount_residual:,.2f}\n"
                content += "-" * 30 + "\n"
                total_outstanding += invoice.amount_residual
            
            content += f"\nTOTAL OUTSTANDING: {currency_symbol}{total_outstanding:,.2f}\n"
            content += "\nPlease remit payment at your earliest convenience.\n"
            
            return base64.b64encode(content.encode('utf-8')).decode('utf-8')
            
        except Exception as e:
            _logger.error(f"Error in fallback generation: {str(e)}")
            error_msg = "Error generating invoice statement. Please contact support."
            return base64.b64encode(error_msg.encode('utf-8')).decode('utf-8')