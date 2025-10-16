from odoo import fields, models, api, tools, _ 
from odoo.exceptions import ValidationError
from datetime import datetime
from io import BytesIO
import qrcode
import base64

class ProjectProject(models.Model):
    _inherit = 'project.project'

    asset_count = fields.Integer(string='Asset Count', compute='_compute_asset_count')

    def asset_view(self):
            return{
            'type': 'ir.actions.act_window',
            'name': 'Asset Bill',
            'res_model': 'equipment.assets',
            #domain is used to filter the records
            'domain': [('project_id', '=', self.id)],
            'view_mode': 'tree,form',
            #context is used to pass the default value in the form view
            'context': {'default_project_id': self.id},
            
            'view_type': 'form',
            }
            
#_compute_asset_count function is used to count the number of assets in the project
    def _compute_asset_count(self):
        for project in self:
            asset_data = self.env['equipment.assets'].search([('project_id', '=', project.id)])
            project.asset_count = len(asset_data)

