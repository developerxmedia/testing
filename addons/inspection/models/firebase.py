from odoo import models, fields, api
from datetime import datetime
import requests
import json


# class notification_list(models.Model):
#     _name='notification.list'
#     _rec_name='name'
#     _inherit = ['mail.thread', 'mail.activity.mixin',]
#     _description = "Notification"

#     name= fields.Char(string="Name",required=True)
#     description = fields.Html(string="Description",track_visibility='onchange')
#     #vehicle booking management notification  status selection field 

#     read_status = fields.Selection([('read','Readed'),('un_read','Un Read')],string='View',default="un_read",track_visibility='onchange')
#     res_users = fields.Many2one('res.users',string='Users')
#     res_partner_id = fields.Many2one('res.partner',string='Partner')
#     date = fields.Date(string="Date",default=datetime.now())
#     image = fields.Image(string="Image")

    
#     manager = fields.Boolean(string='Is Manager')
#     user = fields.Boolean(string='Is User')
#     tech = fields.Boolean(string='Is Tech')
    
#     inspection_task=fields.Many2one('inspection.request',string="Inspection Task")

#     background_image = fields.Image(string="Background Image")
    # image_notification = fields.Image(string="Notification Image")
    


class signal_master(models.Model):

    _name = 'one.signal.master'
    _rec_name = 'user_id'

    user_id = fields.Many2one('res.users',string='User Name')
    signal_type= fields.Selection([('android',"Android"),('ios',"IOS")],string="Signal Type")
    key = fields.Char('Key ID')
    
    #user
    user_mode= fields.Selection([('passenger',"Passenger"),('driver',"Driver")])
    driver_id = fields.Many2one('vb.driver.master',string='Driver')
    passenger_id = fields.Many2one('user.master',string='Passenger')
    
# class createOtp(models.Model):
#     _name='create.otp'
#     _rec_name = 'phone_number'
    
#     phone_number = fields.Char(string="Phone Number")
#     otp_number = fields.Char(string="Otp")
#     expire_date= fields.Float(string= "Expire Date")
#     type_users = fields.Selection([('driver','Driver'),('user','User'),('admin','Admin')],string = 'Type')