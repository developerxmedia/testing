from odoo import api, fields, models,_
from odoo.exceptions import ValidationError

class ProductInherit(models.Model):
    _inherit='product.product'

    equipments=fields.Boolean(string='Equipments')    
    product_display = fields.Char("Product Name")
    model_name = fields.Char("Attribute Name")
    
    
    @api.model
    def create(self,vals):
        result = super(ProductInherit, self).create(vals)

        for rec in result:
            rec.product_display = rec.display_name

            s_strs = rec.display_name
            data = s_strs.split('(')
            data1 = data[-1]
            
            if data1[-1] == ')':
                word = data1[:-1]
                rec.model_name = word

        return result
    