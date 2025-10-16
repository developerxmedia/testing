from odoo import fields, models, api, tools, _ 
from odoo.exceptions import ValidationError
from datetime import datetime
from io import BytesIO
import qrcode
import base64

class Buying(models.Model):
    _name = 'buy.product'
    _description = 'Product Buying'
    
    client_name= fields.Many2one('res.partner',string='Product Name')
    contact = fields.Char(string='Contact')
    address = fields.Char(string='Address')
    fax= fields.Char(string='Tel /Fax')
    email = fields.Char(string='Email')

    product_id= fields.One2many('product.description.line', 'buy_id')

    product_total=fields.Float(string='Sub Total' ,compute='product_description')

    @api.depends('product_id')
    def product_description(self):
        for i in self:
            sums = 0.00
            for k in i.product_id:
                sums += k.total_price
            i.update({
                'product_total':sums,
            })

class ProductDescription(models.Model):
    _name = 'product.description.line'
    _description = 'Custom Lines for Bills of Material'

    description = fields.Many2one('product.budget',string='Description')
    quantity = fields.Float(string='Quantity')
    unit_price = fields.Float(string='Unit Price')
    total_price = fields.Float(string='Total', compute='amount_product_total')

    buy_id= fields.Many2one('buy.product')

    @api.depends('quantity','unit_price')
    def amount_product_total(self):
        for rec in self:
            rec.total_price=( rec.quantity * rec.unit_price)

    @api.depends('description')
    def line_product_one(self):
        for rec in self:
            orm=self.env['product.budget'].search([('product_name','=',rec.description.product_name)], limit=1)

            rec.unit_price=orm.price


