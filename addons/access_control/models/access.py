from odoo import fields, models, api
from datetime import date, datetime,timedelta
from odoo.exceptions import ValidationError

class UserOne2Manuy(models.Model):
    
    _name = 'access.app'
    _inherit = ['mail.thread','mail.activity.mixin']
    _rec_name = 'name'
    
    name = fields.Many2one('res.users',string="User",required=True,tracking=True)
    def get_insert_access(self):
        return [(0,0,{
            "module" : 'LEAD',
            'access_create' : True,
            "access_read" : True,
            'access_write' : True,
            'access_unlink' : True
        }),(0,0,{
            "module" : 'OPPORTUNITY',
            "access_read" : True,
            'access_write' : True,
        }),(0,0,{
            "module" : 'CONTACTS',
            'access_create' : True,
            "access_read" : True,
            'access_write' : True,
        }),(0,0,{
            "module" : 'PRODUCT_CATALOG',
            "access_read" : True,
        }),(0,0,{
            "module" : 'MY_ACTIVITY',
            'access_create' : True,
        }),(0,0,{
            "module" : 'PROJECT',
            'access_create' : True,
            "access_read" : True,
        }),(0,0,{
            "module" : 'TASK',
            "access_read" : True,
        }),(0,0,{
            "module" : 'EQUIPMENT',
            'access_create' : True,
            "access_read" : True,
        }),(0,0,{
            "module" : 'SALE RFQ',
            'access_create' : True,
            "access_read" : True,
            'access_write' : True,
            'access_unlink' : True
        }),(0,0,{
            "module" : 'ORDER FORM',
            'access_create' : True,
            "access_read" : True,
            'access_write' : True,
            'access_unlink' : True
        }),(0,0,{
            "module" : 'RFQ',
            'access_create' : True,
            "access_read" : True,
            'access_write' : True,
            'access_unlink' : True,
            'access_approved_user' :True,
            'access_approved_manager' : True
        }),(0,0,{
            "module" : 'PURCHASE ORDER',
            "access_read" : True,
        }),(0,0,{
            "module" : 'INVENTORY',
            'access_create' : True,
            "access_read" : True,
        }),(0,0,{
            "module" : 'GRN',
            'access_create' : True,
            "access_read" : True,
            'scan' : True,
        }),(0,0,{
            "module" : 'DELIVERY CHELLAN',
            'access_create' : True,
            "access_read" : True,
            'scan' : True,
        }),(0,0,{
            "module" : 'CONSIGNMENT',
            'access_create' : True,
            "access_read" : True,
            'access_approved_user' : True,
            'access_approved_manager' : True
        }),(0,0,{
            "module" : 'PICKING',
            'access_create' : True,
            "access_read" : True,
            'scan' : True,
        }),(0,0,{
            "module" : 'INVOICE',
            'access_create' : True,
            "access_read" : True,
            'access_approved_user' : True,
            'access_approved_manager' : True
        }),(0,0,{
            "module" : 'VENDOR BILLS',
            'access_create' : True,
            "access_read" : True,
        }),(0,0,{
            "module" : 'PAYMENTS',
            'access_create' : True,
            "access_read" : True,
        }),(0,0,{
            "module" : 'ATTENDANCE',
            'access_create' : True,
            "access_read" : True,
        }),(0,0,{
            "module" : 'LEAVE',
            'access_create' : True,
            "access_read" : True,
        }),(0,0,{
            "module" : 'EXPENSES',
            'access_create' : True,
            "access_read" : True,
        }),(0,0,{
            "module" : 'OT REQUEST LIST',
            "access_read" : True,
            'access_approved_user' : True,
            'access_approved_manager' : True
        }),(0,0,{
            "module" : 'OT LIST',
            "access_read" : True,
        }),(0,0,{
            "module" : 'SERVICE REQUEST',
            'access_create' : True,
            "access_read" : True,
            'scan' : True,  
        }),(0,0,{
            "module" : 'SPARE REQUEST',
            'access_create' : True,
            "access_read" : True,
            'access_write' : True,
            'access_unlink' : True
        }),(0,0,{
            "module" : 'MANUFACTURING ACCESS',
            'access_create' : True,
            "access_read" : True,
            'access_write' : True,
            'access_unlink' : True
        }),(0,0,{
            "module" : 'WORK ORDER',
            'access_create' : True,
            "access_read" : True,
            'access_write' : True,
            'access_unlink' : True
        }),(0,0,{
            "module" : 'PAYMENT REPORT',
            'access_create' : True,
            "access_read" : True,
            'access_write' : True,
            'access_unlink' : True
        })]
    
    access_lines = fields.One2many('user.access.lines','access_line_id',string="Access Lines",ondelete="cascade",default=get_insert_access)
    crm_menu = fields.Boolean(string='CRM MENU',default=True)
    project_menu = fields.Boolean(string='PROJECT MENU',default=True)
    sale_menu = fields.Boolean(string='SALE MENU',default=True)
    purchase_menu = fields.Boolean(string='PURCHASE MENU',default=True)
    inventory_menu = fields.Boolean(string='INVENTORY MENU',default=True)
    accounting_menu = fields.Boolean(string='ACCOUNTING MENU',default=True)
    hr_menu = fields.Boolean(string='HR MENU',default=True)
    service_menu = fields.Boolean(string='SERVICE MENU',default=True)
    manufacturing_menu = fields.Boolean(string='MANUFACTURING MENU',default=True)
    payment_report = fields.Boolean(string='PAYMENT REPORT MENU',default=True)
    ceo_dashboard = fields.Boolean(string='CEO DASHBOARD',default=True)
    crm_dashboard = fields.Boolean(string='CRM DASHBOARD',default=True)
    sale_dashboard = fields.Boolean(string='SALES DASHBOARD',default=True)
    project_dashboard = fields.Boolean(string='PROJECT DASHBOARD',default=True)
    purchase_dashboard = fields.Boolean(string='PURCHASE DASHBOARD',default=True)
    access_push = fields.Text(string='ACCESS LIST')
    
    @api.constrains('access_lines','name')
    def access_insert(self):
        access_list = []
        if self:
            if self.crm_menu == True:
                access_list.append('CRM_MENU')
            if self.project_menu == True:
                access_list.append('PROJECT_MENU')
            if self.sale_menu == True:
                access_list.append('SALE_MENU')
            if self.purchase_menu == True:
                access_list.append('PURCHASE_MENU')
            if self.inventory_menu == True:
                access_list.append('INVENTORY_MENU')
            if self.accounting_menu == True:
                access_list.append('ACCOUNTING_MENU')
            if self.hr_menu == True:
                access_list.append('HR_MENU')
            if self.service_menu == True:
                access_list.append('SERVICE_MENU')
            if self.manufacturing_menu == True:
                access_list.append('MANUFACTURING_MENU')
            if self.payment_report == True:
                access_list.append('PAYMENT_REPORT_MENU')
            if self.ceo_dashboard == True:
                access_list.append('CEO_DASHBOARD')
            if self.crm_dashboard == True:
                access_list.append('CRM_DASHBOARD')
            if self.sale_dashboard == True:
                access_list.append('SALES_DASHBOARD')
            if self.project_dashboard == True:
                access_list.append('PROJECT_DASHBOARD')
            if self.purchase_dashboard == True:
                access_list.append('PURCHASE_DASHBOARD')
        for rec in self.access_lines:
            if rec.module == 'LEAD':
                if rec.access_create == True:
                    access_list.append('LEAD_CREATE')
                if rec.access_read == True:
                    access_list.append('LEAD_LIST')
                if rec.access_write == True:
                    access_list.append('LEAD_EDIT')
                if rec.access_unlink == True:
                    access_list.append('LEAD_DELETE')
                if rec.access_approved_user == True:
                    access_list.append('USER_ACCESS_LEAD')
                if rec.access_approved_manager == True:
                    access_list.append('MANAGER_ACCESS_LEAD')
                if rec.scan == True:
                    access_list.append('SCAN_ACCESS_LEAD')
            if rec.module == 'OPPORTUNITY':
                # if rec.access_create == True:
                #     access_list.append('CREATE_CRM_LEAD')
                if rec.access_read == True:
                    access_list.append('OPPORTUNITY_LIST')
                if rec.access_write == True:
                    access_list.append('OPPORTUNITY_EDIT')
                # if rec.access_unlink == True:
                #     access_list.append('UNLINK_CRM_LEAD')
                # if rec.access_approved_user == True:
                #     access_list.append('USER_ACCESS_CRM_LEAD')
                # if rec.access_approved_manager == True:
                #     access_list.append('MANAGER_ACCESS_CRM_LEAD')
            if rec.module == 'CONTACTS':
                if rec.access_create == True:
                    access_list.append('CONTACTS_CREATE')
                if rec.access_read == True:
                    access_list.append('CONTACTS_LIST')
                if rec.access_write == True:
                    access_list.append('CONTACTS_EDIT')
                # if rec.access_unlink == True:
                #     access_list.append('UNLINK_PROJECT')
                # if rec.access_approved_user == True:
                #     access_list.append('USER_ACCESS_PROJECT')
                # if rec.access_approved_manager == True:
                #     access_list.append('MANAGER_ACCESS_PROJECT')
            if rec.module == 'PRODUCT_CATALOG':
                # if rec.access_create == True:
                #     access_list.append('CREATE_PURCHASE_ORDER')
                if rec.access_read == True:
                    access_list.append('PRODUCT_LIST')
                # if rec.access_write == True:
                #     access_list.append('WRITE_PURCHASE_ORDER')
                # if rec.access_unlink == True:
                #     access_list.append('UNLINK_PURCHASE_ORDER')
                # if rec.access_approved_user == True:
                #     access_list.append('USER_ACCESS_PURCHASE_ORDER')
                # if rec.access_approved_manager == True:
                #     access_list.append('MANAGER_ACCESS_PURCHASE_ORDER')
            if rec.module == 'MY_ACTIVITY':
                if rec.access_create == True:
                    access_list.append('ACTIVITY_CREATE')
                # if rec.access_read == True:
                #     access_list.append('READ_INVENTORY')
                # if rec.access_write == True:
                #     access_list.append('WRITE_INVENTORY')
                # if rec.access_unlink == True:
                #     access_list.append('UNLINK_INVENTORY')
                # if rec.access_approved_user == True:
                #     access_list.append('USER_ACCESS_INVENTORY')
                # if rec.access_approved_manager == True:
                #     access_list.append('MANAGER_ACCESS_INVENTORY')
            if rec.module == 'PROJECT':
                if rec.access_create == True:
                    access_list.append('PROJECT_CREATE')
                if rec.access_read == True:
                    access_list.append('PROJECT_LIST')
                # if rec.access_write == True:
                #     access_list.append('WRITE_ACCOUNTING')
                # if rec.access_unlink == True:
                #     access_list.append('UNLINK_ACCOUNTING')
                # if rec.access_approved_user == True:
                #     access_list.append('USER_ACCESS_ACCOUNTING')
                # if rec.access_approved_manager == True:
                #     access_list.append('MANAGER_ACCESS_ACCOUNTING')
            if rec.module == 'TASK':
                # if rec.access_create == True:
                #     access_list.append('CREATE_HR')
                if rec.access_read == True:
                    access_list.append('TASK_LIST')
                # if rec.access_write == True:
                #     access_list.append('WRITE_HR')
                # if rec.access_unlink == True:
                #     access_list.append('UNLINK_HR')
                # if rec.access_approved_user == True:
                #     access_list.append('USER_ACCESS_HR')
                # if rec.access_approved_manager == True:
                #     access_list.append('MANAGER_ACCESS_HR')
            if rec.module == 'EQUIPMENT':
                if rec.access_create == True:
                    access_list.append('EQUIPMENT_CREATE')
                if rec.access_read == True:
                    access_list.append('EQUIPMENT_LIST')
                # if rec.access_write == True:
                #     access_list.append('WRITE_MANUFACTURING')
                # if rec.access_unlink == True:
                #     access_list.append('UNLINK_MANUFACTURING')
                if rec.access_approved_user == True:
                    access_list.append('USER_ACCESS_MANUFACTURING')
                if rec.access_approved_manager == True:
                    access_list.append('MANAGER_ACCESS_MANUFACTURING')
            if rec.module == 'SALE RFQ':
                if rec.access_create == True:
                    access_list.append('SALE_RFQ_CREATE')
                if rec.access_read == True:
                    access_list.append('SALE_RFQ_LIST')
                if rec.access_write == True:
                    access_list.append('SALE_RFQ_EDIT')
                if rec.access_unlink == True:
                    access_list.append('SALE_RFQ_DELETE')
                if rec.access_approved_user == True:
                    access_list.append('SALE_RFQ_REQUEST_APPROVAL_USER')
                if rec.access_approved_manager == True:
                    access_list.append('SALE_RFQ_APPROVAL_MANAGER')
                
            if rec.module == 'ORDER FORM':
                if rec.access_create == True:
                    access_list.append('ORDER_CREATE')
                if rec.access_read == True:
                    access_list.append('ORDER_LIST')
                if rec.access_write == True:
                    access_list.append('ORDER_EDIT')
                if rec.access_unlink == True:
                    access_list.append('ORDER_DELETE')
            if rec.module == 'RFQ':
                if rec.access_create == True:
                    access_list.append('RFQ_CREATE')
                if rec.access_read == True:
                    access_list.append('RFQ _LIST')
                if rec.access_write == True:
                    access_list.append('RFQ_EDIT')
                if rec.access_unlink == True:
                    access_list.append('RFQ_DELETE')
                if rec.access_approved_user == True:
                    access_list.append('RFQ_REQUEST_APPROVAL_USER')
                if rec.access_approved_manager == True:
                    access_list.append('RFQ_APPROVAL_MANAGER')
            if rec.module == 'PURCHASE ORDER':
                # if rec.access_create == True:
                #     access_list.append('SALE_RFQ_CREATE')
                if rec.access_read == True:
                    access_list.append('PURCHASE_LIST')
                    # PURCHASE_GRN
                # if rec.access_write == True:
                #     access_list.append('SALE_RFQ_EDIT')
                # if rec.access_unlink == True:
                #     access_list.append('SALE_RFQ_DELETE')
            if rec.module == 'INVENTORY':
                if rec.access_create == True:
                    access_list.append('INVENTORY_CREATE')
                if rec.access_read == True:
                    access_list.append('INVENTORY_LIST')
                # if rec.access_write == True:
                #     access_list.append('SALE_RFQ_EDIT')
                # if rec.access_unlink == True:
                #     access_list.append('SALE_RFQ_DELETE')
            if rec.module == 'GRN':
                if rec.access_create == True:
                    access_list.append('GRN_CREATE')
                if rec.access_read == True:
                    access_list.append('GRN_LIST')
                if rec.scan == True:
                    access_list.append('GRN_SCAN')
                # if rec.access_write == True:
                #     access_list.append('SALE_RFQ_EDIT')
                # if rec.access_unlink == True:
                #     access_list.append('SALE_RFQ_DELETE')
            if rec.module == 'DELIVERY CHELLAN':
                if rec.access_create == True:
                    access_list.append('DC_CREATE')
                if rec.access_read == True:
                    access_list.append('DC_LIST')
                if rec.scan == True:
                    access_list.append('DC_SCAN')
                # if rec.access_write == True:
                #     access_list.append('SALE_RFQ_EDIT')
                # if rec.access_unlink == True:
                #     access_list.append('SALE_RFQ_DELETE')
            if rec.module == 'CONSIGNMENT':
                if rec.access_create == True:
                    access_list.append('CONSIGNMENT_CREATE')
                if rec.access_read == True:
                    access_list.append('CONSIGNMENT_LIST')
                if rec.access_approved_user == True:
                    access_list.append('CONSIGNMENT_REQUEST_APPROVAL_USER')
                if rec.access_approved_manager == True:
                    access_list.append('CONSIGNMENT_APPROVAL_MANAGER')
                # if rec.access_write == True:
                #     access_list.append('SALE_RFQ_EDIT')
                # if rec.access_unlink == True:
                #     access_list.append('SALE_RFQ_DELETE')
            if rec.module == 'PICKING':
                if rec.access_create == True:
                    access_list.append('PICKING_CREATE')
                if rec.access_read == True:
                    access_list.append('PICKING_LIST')
                if rec.scan == True:
                    access_list.append('PICKING_SCAN')
                # if rec.access_write == True:
                #     access_list.append('SALE_RFQ_EDIT')
                # if rec.access_unlink == True:
                #     access_list.append('SALE_RFQ_DELETE')
            if rec.module == 'INVOICE':
                if rec.access_create == True:
                    access_list.append('INVOICE_CREATE')
                if rec.access_read == True:
                    access_list.append('INVOICE_LIST')
                if rec.access_approved_user == True:
                    access_list.append('INVOICE_REQUEST_APPROVAL_USER')
                if rec.access_approved_manager == True:
                    access_list.append('INVOICE_APPROVAL_MANAGER')
                # if rec.access_write == True:
                #     access_list.append('SALE_RFQ_EDIT')
                # if rec.access_unlink == True:
                #     access_list.append('SALE_RFQ_DELETE')
                
            if rec.module == 'VENDOR BILLS':
                if rec.access_create == True:
                    access_list.append('VENDOR_CREATE')
                if rec.access_read == True:
                    access_list.append('VENDOR_LIST')
                # if rec.access_write == True:
                #     access_list.append('SALE_RFQ_EDIT')
                # if rec.access_unlink == True:
                #     access_list.append('SALE_RFQ_DELETE')
            if rec.module == 'PAYMENTS':
                if rec.access_create == True:
                    access_list.append('PAYMENT_CREATE')
                if rec.access_read == True:
                    access_list.append('PAYMENTS_LIST')
                # if rec.access_write == True:
                #     access_list.append('SALE_RFQ_EDIT')
                # if rec.access_unlink == True:
                #     access_list.append('SALE_RFQ_DELETE')
            if rec.module == 'ATTENDANCE':
                if rec.access_create == True:
                    access_list.append('ATTENDANCE_CREATE')
                if rec.access_read == True:
                    access_list.append('ATTENDANCE_LIST')
                # if rec.access_write == True:
                #     access_list.append('SALE_RFQ_EDIT')
                # if rec.access_unlink == True:
                #     access_list.append('SALE_RFQ_DELETE')
            if rec.module == 'LEAVE':
                if rec.access_create == True:
                    access_list.append('LEAVE_CREATE')
                if rec.access_read == True:
                    access_list.append('LEAVE_LIST')
                # if rec.access_write == True:
                #     access_list.append('SALE_RFQ_EDIT')
                # if rec.access_unlink == True:
                #     access_list.append('SALE_RFQ_DELETE')
            if rec.module == 'EXPENSES':
                if rec.access_create == True:
                    access_list.append('EXPENSES_CREATE')
                if rec.access_read == True:
                    access_list.append('EXPENSES_LIST')
                # if rec.access_write == True:
                #     access_list.append('SALE_RFQ_EDIT')
                # if rec.access_unlink == True:
                #     access_list.append('SALE_RFQ_DELETE')
            if rec.module == 'OT REQUEST LIST':
                # if rec.access_create == True:
                #     access_list.append('PICKING_CREATE')
                if rec.access_read == True:
                    access_list.append('EMPLOYEE_LIST')
                if rec.access_approved_user == True:
                    access_list.append('OT_REQUEST_USER')
                if rec.access_approved_manager == True:
                    access_list.append('OT_REQUEST_MANAGER')
                #     OT_REQUEST
                # if rec.access_write == True:
                #     access_list.append('SALE_RFQ_EDIT')
                # if rec.access_unlink == True:
                #     access_list.append('SALE_RFQ_DELETE')
            if rec.module == 'OT LIST':
                # if rec.access_create == True:
                #     access_list.append('PICKING_CREATE')
                if rec.access_read == True:
                    access_list.append('OVERTIME_LIST')
                # if rec.access_write == True:
                #     access_list.append('SALE_RFQ_EDIT')
                # if rec.access_unlink == True:
                #     access_list.append('SALE_RFQ_DELETE')
            if rec.module == 'SERVICE REQUEST':
                if rec.access_create == True:
                    access_list.append('SERVICE_CREATE')
                if rec.access_read == True:
                    access_list.append('SERVICE_REQUEST_LIST')
                if rec.scan == True:
                    access_list.append('SERVICE_SCAN')
                if rec.access_write == True:
                    access_list.append('SERVICE_EDIT')
                if rec.access_unlink == True:
                    access_list.append('SERVICE_DELETE')
            if rec.module == 'SPARE REQUEST':
                if rec.access_create == True:
                    access_list.append('SPARE_CREATE')
                if rec.access_read == True:
                    access_list.append('SPARE_REQUEST_LIST')
                if rec.access_write == True:
                    access_list.append('SPARE_EDIT')
                if rec.access_unlink == True:
                    access_list.append('SPARE_DELETE')
            if rec.module == 'MANUFACTURING ACCESS':
                if rec.access_create == True:
                    access_list.append('MANUFACTURING_CREATE')
                if rec.access_read == True:
                    access_list.append('MANUFACTURING_LIST')
                if rec.access_write == True:
                    access_list.append('MANUFACTURING_EDIT')
                if rec.access_unlink == True:
                    access_list.append('MANUFACTURING_DELETE')
            if rec.module == 'WORK ORDER':
                if rec.access_create == True:
                    access_list.append('WORKORDER_CREATE')
                if rec.access_read == True:
                    access_list.append('WORKORDER_LIST')
                if rec.access_write == True:
                    access_list.append('WORKORDER_EDIT')
                if rec.access_unlink == True:
                    access_list.append('WORKORDER_DELETE')
            if rec.module == 'PAYMENT REPORT':
                if rec.access_create == True:
                    access_list.append('PAYMENT_REPORT_CREATE')
                if rec.access_read == True:
                    access_list.append('PAYMENT_REPORT_LIST')
                if rec.access_write == True:
                    access_list.append('PAYMENT_REPORT_EDIT')
                if rec.access_unlink == True:
                    access_list.append('PAYMENT_REPORT_DELETE')
        self.access_push = str(access_list)
class AccessUser(models.Model):
    _name="user.access.lines"

    access_line_id=fields.Many2one('access.app',string="Access App",ondelete='cascade')
    module=fields.Char(string="Model Name")
#access CRUD fields 
    access_create=fields.Boolean(string="Create")
    access_read=fields.Boolean(string="Read")
    access_write=fields.Boolean(string="Write")
    access_unlink=fields.Boolean(string="Unlink")
    access_access_date=fields.Date(string="Access Date")
#aproval acceess fields
    access_approved_user=fields.Boolean(string="Approved User")
    access_approved_manager = fields.Boolean(string="Approved by Manager")
    scan = fields.Boolean(string="Scan")


    


