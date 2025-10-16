from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from datetime import datetime, date


class RequestForEquipments(models.Model):
    _name ='request.for.equipments'
    _inherit=['mail.thread','mail.activity.mixin']
    _rec_name = 'project_id'
    _description='Request For Equipments'

    project_id=fields.Many2one('project.project',string='Project Id',tracking=True)
    req_by=fields.Many2one('res.users',string='Request By',default=lambda self: self.env.user,tracking=True)
    approved_by=fields.Many2one('res.users',string='Approved By',default=lambda self: self.env.user,tracking=True)
    date=fields.Datetime(string='Date',tracking=True,default=lambda self: fields.Datetime.now().strftime('%Y-%m-%d %H:%M'))

    state=fields.Selection([
        ('unapproved','Unapproved'),
        ('approved','Approved'),
        ('reversed','Return to Inventory')
    ],tracking=True,default='unapproved')
    show=fields.Boolean(string='Show Button')
    equipment_line_ids=fields.One2many('equipments.line','equipment_line',string='Equipment Lines',ondelete='cascade')

    


    @api.onchange('equipment_line_ids')
    def show_button(self):
        # raise ValidationError('ok')
        
        for rec in self:
            list1=[]
            list2=[]
            for record in rec.equipment_line_ids:
                if record.state == 'received':
                    list1.append(record.state)

            for records in rec.equipment_line_ids:
                if records.state == 'received' or records.state == 'not_received':
                    list2.append(record.state)

                    if len(list2) != len(list1):
                        rec.show=False
                    elif len(list2) == len(list1):
                        rec.show=True
                    else:
                        pass
                else:
                    pass


    def state_approved(self):
        for rec in self:
            rec.state='approved'

            for record in self.equipment_line_ids:

                if rec.state=='approved':
                    location = self.env['stock.location'].search([('complete_name', '=', 'WH/Stock')])
                    quant = self.env['stock.quant'].search([('product_id', '=', record.equipments.id),('location_id', '=', location.id)])
                    
                    if quant.available_quantity > record.quantity:
                        quant.write({'quantity': quant.quantity - record.quantity})
                    elif quant.available_quantity < record.quantity and quant.quantity !=0:
                        raise ValidationError(f"The Available Product Quantity In The Stock is  {quant.available_quantity}. You Have To Give Lesser Then {quant.available_quantity} To  Use In Projects")
                    elif quant.available_quantity == 0:
                        raise ValidationError(f"There Is  No Available Quantity In The Stock")
                    else:
                        pass

                else:
                    pass
    
    def state_unapproved(self):
        for rec in self:
            rec.state='unapproved'

    def state_reversed(self):
        for rec in self:
            rec.state='reversed'

            for record in self.equipment_line_ids:
                if rec.state=='reversed':
                    if record.state == 'received':
                        location = self.env['stock.location'].search([('complete_name', '=', 'WH/Stock')])
                        quant = self.env['stock.quant'].search([('product_id', '=', record.equipments.id),('location_id', '=', location.id)])
                        
                        if record.quantity:
                            quant.write({'quantity': quant.quantity + record.quantity})
                        else:
                            pass


    

class EquipmentsLine(models.Model):
    _name ='equipments.line'

    _description='Equipments Line'

    equipments=fields.Many2one('product.product',string='Equipments',domain=[('equipments','=',True)],tracking=True)
    quantity=fields.Float(string='Quantity',tracking=True,default=1)
    units=fields.Many2one('uom.uom',string='Units',tracking=True)
    project_id=fields.Many2one('project.project',string='Project Id',tracking=True)
    date=fields.Datetime(string='Date',tracking=True)
    req_by=fields.Many2one('res.users',string='Request By')
    state=fields.Selection([
        ('not_received','Not Received'),
        ('received','Received'),
    ],tracking=True,default='not_received')
    equipment_line=fields.Many2one('request.for.equipments',string='Equipment Line',ondelete='cascade')

    @api.onchange('equipments')
    def auto_change(self):
        for rec in self:
            rec.units=rec.equipments.uom_id



    

