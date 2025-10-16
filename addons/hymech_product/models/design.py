from odoo import fields, models, api, tools, _ 
from odoo.exceptions import ValidationError
from datetime import datetime
from io import BytesIO
import qrcode
import base64

class design(models.Model):
    _name = 'design.model'
    _description = 'Design'
    _rec_name = 'design_name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    design_name= fields.Char(string='Name')
    category=fields.Many2one('category.design', string='Category')
    design_attachment = fields.Integer(string='Attachment', compute='design_attachment_fun')

    def design_attachment_fun(self):
        for rec in self:
            rec.design_attachment = self.env['ir.attachment'].search_count([('res_model', '=', self._name),('res_id','=',self.id)])
        

    def action_attachement_design(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Design',
            'res_model': 'ir.attachment',
            'domain': [('res_model', '=', self._name),('res_id','=',self.id)],
            'view_mode': 'tree,form',
            'context': {'default_res_id': self.id, 'default_res_model': self._name}
        }


class categoryDesign(models.Model):
    _name = 'category.design'
    _description = 'Category Design'
    _rec_name = 'child'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    category_name = fields.Char(string='Category Name',track_visibility='onchange')
    parent_id = fields.Many2one('category.design', string ='Parent Category',track_visibility='onchange')
    child = fields.Char(string='Name', store=True)
    attachemets = fields.Many2many("ir.attachment",string="Attachments")
    
    @api.onchange('category_name', 'parent_id')
    def _compute_rec_name(self):
        for record in self:
            if record.parent_id.category_name == False:
                record.child = f"{record.category_name}"
            else:
                record.child = f"{record.parent_id.child} / {record.category_name}"