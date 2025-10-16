from odoo import api, fields, models,_
from odoo.exceptions import ValidationError

class Invoicing(models.Model):
    _inherit='project.project'

    project_count=fields.Integer(string='Project',compute='count_projects',store=True)
    
    def count_projects(self):
        for rec in self:
            project_counts = len(self.env['request.for.equipments'].search([('project_id','=',rec.name)]))
            rec.project_count = project_counts

    def click_project_count(self):
        return{
            'type':'ir.actions.act_window',
            'name':'project',
            'res_model':'request.for.equipments',
            'domain':[('project_id','=',self.name)],
            'view_mode':'tree,form',
            'target':'current'
        }

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None, order=None):
        args = list(args or [])
        if name :
            args += ['|',('name', operator, name),('service_number_project',operator, name)]
        return self._search(args, limit=limit, access_rights_uid=name_get_uid, order=order)