from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    job_code = fields.Char("Job Code")
    po_number = fields.Char("PO Number")  


    def _prepare_picking(self):
        """Extend picking values with custom fields"""
        res = super(PurchaseOrder, self)._prepare_picking()

        res.update({
            "job_code": self.job_code,
            "po_number": self.name, 
            'product_name': self.order_line and self.order_line[0].product_id.id or False,  
            'atten': self.partner_id.id,   
            'terms_conditions': self.terms_and_condition_id.id if self.terms_and_condition_id else False,

        })
        return res


    def action_create_invoice(self):
        """Override to handle missing accounts before creating invoice"""
        self._ensure_purchase_accounts()
        return super(PurchaseOrder, self).action_create_invoice()

    def _ensure_purchase_accounts(self):
        """Ensure all purchase order lines have proper accounts"""
        for line in self.order_line:
            if not line.product_id:
                continue
                
            if line.product_id.product_tmpl_id.property_account_expense_id:
                continue
                         
            category_account = line.product_id.categ_id.property_account_expense_categ_id
            if category_account:
                
                line.product_id.product_tmpl_id.property_account_expense_id = category_account
                continue
            
            
            default_expense_account = self._get_default_expense_account()
            if default_expense_account:
                line.product_id.product_tmpl_id.property_account_expense_id = default_expense_account
            else:
                raise UserError(_(
                    "No expense account found for product '%s'. "
                    "Please configure an expense account in the product or product category."
                ) % line.product_id.name)

    def _get_default_expense_account(self):
        """Get default expense account from company or chart of accounts"""      
        expense_account = self.env['account.account'].search([
            ('company_id', '=', self.company_id.id),
            ('account_type', '=', 'expense'),
            ('code', 'like', '5%')  
        ], limit=1)
        
        if not expense_account:           
            expense_account = self.env['account.account'].search([
                ('company_id', '=', self.company_id.id),
                ('account_type', '=', 'expense')
            ], limit=1)
            
        return expense_account


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _create_invoices(self, grouped=False, final=False, date=None):
        """Override to handle missing accounts before creating invoice"""
        self._ensure_sale_accounts()
        return super(SaleOrder, self)._create_invoices(grouped=grouped, final=final, date=date)

    def _ensure_sale_accounts(self):
        """Ensure all sale order lines have proper income accounts"""
        for line in self.order_line:
            if not line.product_id:
                continue
                
            if line.product_id.product_tmpl_id.property_account_income_id:
                continue
                
            category_account = line.product_id.categ_id.property_account_income_categ_id
            if category_account:
                line.product_id.product_tmpl_id.property_account_income_id = category_account
                continue
            
            default_income_account = self._get_default_income_account()
            if default_income_account:
                line.product_id.product_tmpl_id.property_account_income_id = default_income_account
            else:
                raise UserError(_(
                    "No income account found for product '%s'. "
                    "Please configure an income account in the product or product category."
                ) % line.product_id.name)

    def _get_default_income_account(self):
        """Get default income account from company or chart of accounts"""
        income_account = self.env['account.account'].search([
            ('company_id', '=', self.company_id.id),
            ('account_type', '=', 'income'),
            ('code', 'like', '4%') 
        ], limit=1)
        
        if not income_account:
            income_account = self.env['account.account'].search([
                ('company_id', '=', self.company_id.id),
                ('account_type', '=', 'income')
            ], limit=1)
            
        return income_account



class StockPicking(models.Model):
    _inherit = "stock.picking"

    job_code = fields.Char("Job Code")

    terms_conditions = fields.Many2one(
        'terms.conditions',
        string="Terms and Conditions"
    )

    po_number = fields.Char("PO Number")
    product_name = fields.Many2one("product.product", string="Product Name")
    atten = fields.Many2one("res.partner", string="Attn")

    @api.depends("move_ids.product_id")
    def _compute_product_names(self):
        for picking in self:
            products = picking.move_ids.mapped("product_id.display_name")
            picking.product_names = ", ".join(products) if products else False






class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """Fix taxes when vendor changes"""
        result = super().onchange_partner_id()
        
        # Recalculate taxes for all order lines
        for line in self.order_line:
            if line.product_id:
                # Get product taxes
                product_taxes = line.product_id.supplier_taxes_id
                
                if product_taxes and self.fiscal_position_id:
                    # Apply fiscal position mapping
                    taxes = self.fiscal_position_id.map_tax(
                        product_taxes,
                        line.product_id,
                        self.partner_id
                    )
                    line.taxes_id = [(6, 0, taxes.ids)]
                elif product_taxes:
                    line.taxes_id = [(6, 0, product_taxes.ids)]
        
        return result