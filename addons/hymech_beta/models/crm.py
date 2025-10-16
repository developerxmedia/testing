from odoo import fields, models, api, tools, _ 
from odoo.exceptions import ValidationError
from datetime import datetime
import logging

class CustomCrmLead(models.Model):
    _inherit = 'crm.lead'
    
    product_id_one = fields.Many2one('product.product', string='Product')
    

    @api.model
    def create(self, vals):
        lead = super(CustomCrmLead, self).create(vals)
        try:
            product_vals = {
                'name': lead.name, 
                'type': 'product', 
                'categ_id' :1,
                'uom_id' :1,
                'uom_po_id' :1,
            }
            product_id = self.env['product.product'].create(product_vals)
            # Check if product_id is valid before assigning
            if product_id and hasattr(product_id, 'id') and product_id.id:
                lead.product_id_one = product_id.id
        except Exception as e:
            # Log error and continue without setting product_id_one
            _logger = logging.getLogger(__name__)
            _logger.warning("Failed to create product for CRM lead: %s", str(e))
            lead.product_id_one = False
        return lead