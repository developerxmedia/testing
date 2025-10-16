from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    employee_id = fields.Many2one(
        'hr.employee',
        string="Related Employee",
        help="The employee record linked to this user."
    )

    def action_create_employee(self):
        """Create and link an employee if none exists"""
        for user in self:
            if not user.employee_id:
                employee = self.env['hr.employee'].create({
                    'name': user.name,
                    'work_email': user.email,
                    'user_id': user.id,
                })
                user.employee_id = employee.id  # link it
            else:
                employee = user.employee_id
       
