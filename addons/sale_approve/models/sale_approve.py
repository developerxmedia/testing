from odoo import fields, models
from inspect import signature
from odoo import api, fields, models, _
from datetime import date,datetime,timedelta
from dateutil.relativedelta import relativedelta 
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    approval_req = fields.Boolean("Approval Required",store=True, default=True)
    approval = fields.Selection([('approval_not_required',"Approval Not Required"),('waiting_approval',"Waiting For Approval"),('approved',"Approved")],string="Sale Approval",readonly=True,default='waiting_approval')
    checking_approval = fields.Boolean('Check Approval',compute='_stage_allow',store=True)
    
    approver_user_id = fields.Many2one(string="Approved By", comodel_name="res.users", tracking=1,readonly=True)
    approve_date = fields.Date(string="Approved On", tracking=1,readonly=True)

    # Add missing fields here 👇
    actual_price = fields.Float(string="Actual Price", store=True)
    expected_price = fields.Float(string="Expected Price", store=True)
    

    @api.depends('state')
    def _stage_allow(self):
        for rec in self:
            if rec.approval_req == True:
                if rec.state == 'sent' or rec.state == 'sale':
                    if rec.approval == 'waiting_approval':
                        raise ValidationError("Approval Required")
                    else:
                        pass
            rec.checking_approval = True

 
            
    def button_approved(self):
        for rec in self:
            rec.approval = 'approved'
            rec.approver_user_id = self.env.user.id
            rec.approve_date = fields.Date.today()
            
    def button_rejected(self):
        for rec in self:
            rec.approval = 'waiting_approval'






    # @api.depends('order_line')
    # def _sale_line_amount(self):
    #     for rec in self:       
    #         if True in values:
    #             rec.approval_req = True
    #             rec.approval = 'waiting_approval'
    #         else:f25
    #             rec.approval_req = False
    
    
# class SaleOrderLine(models.Model):
#     _inherit = 'sale.order.line'
    
#     approval_req = fields.Boolean("Approval Req",compute='_sale_amounts',store=True)
    
#     @api.depends('price_unit')
#     def _sale_amounts(self):
#         for rec in self:
#             if rec.price_unit < rec.product_id.lst_price:
#                 rec.approval_req = True
#             else:
#                 rec.approval_req = False
