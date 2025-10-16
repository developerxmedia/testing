# -*- coding: utf-8 -*-
from sqlite3 import DatabaseError
import werkzeug
from odoo import http
from odoo.http import request
from odoo.addons.auth_signup.models.res_users import SignupError
from ..JwtRequest import jwt_request
from ..util import is_valid_email
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import datetime
from datetime import timedelta,date
import base64
import jwt
import ast
import random
import logging
_logger = logging.getLogger(__name__)

SENSITIVE_FIELDS = ['password', 'password_crypt', 'new_password', 'create_uid', 'write_uid']
SECRET_KEY = "6+8RpZ7ccvF1mPnCV4MDL7/ROLEIBp4f3hqRhvOeTx4="


class JwtController(http.Controller):

    @http.route('/api/http/hello', type='http', auth='public', csrf=False, cors='*')
    def hello(self, **kw):
        return "hiii"
        email = request.params.get('email')
        password = request.params.get('password')
        token = jwt_request.login(email, password)
        return token

    # @jwt_request.middlewares('api_key')
    # def hello(self, **kw):
    #     return jwt_request.response({ 'message': 'hello!', 'key_info': jwt_request.data.get('key_info') })

    @http.route('/api/http/welcome', type='json', auth='public', csrf=False, cors='*', methods=['POST', 'GET'])
    def login(self, **kw):
        return {"message": "hiii"}


    @http.route('/api/http/login', type='json', auth='public', csrf=False, cors='*', methods=['POST'])
    def login(self, email=None, password=None, **kw):
        _logger.info("started")
        email = request.params.get('email')
        password = request.params.get('password')
        token = jwt_request.login(email, password)
        _logger.info(f"all output{email}{password}{token}")
        login_email = request.env['res.users'].sudo().search([('login', '=', email)])
        if login_email:
            if token:
                _logger.info(token)
                login_orm = request.env['res.users'].sudo().search([('login', '=', email)])
                _logger.info(login_orm)

                # type_users = login_orm.type_users
                # new_create_doc = request.env['doctor.registration'].sudo().search_read([('res_users','=',login_orm.id),('status','=','active')],fields=['status','res_users'])
                # if new_create_doc:
                
                access_app_orm = request.env['access.app'].sudo().search([('name', '=', login_orm.id)])
                _logger.info(access_app_orm)

                array_access = ast.literal_eval(access_app_orm.access_push)

                currency = request.env.user.currency_id.symbol
                currency_id = request.env.user.currency_id.id

                valss=[]
                for i in login_orm:
                    date=i['company_ids']
                    for rec in date:
                        valss.append(rec.id)

                res = {

                "accessToken": token,
                "status": "success",
                "message": "Login Successfully",
                'status_message':"success",
                'data': {
                    'email':login_orm['email'],
                    # 'phone_number':login_orm['phone_number'],
                    'id' : login_orm['id'],
                    'type_users': login_orm['type_users'],
                    'name':login_orm['name'],
                    'partner_id':login_orm['partner_id'].id,
                    'currency':currency,
                    'currency_id':currency_id,
                    'user_access':array_access,
                    'allowed_companies':valss,
                    'language':login_orm['lang'],
                    'employee_id': login_orm['employee_id'].id,
                    'default_company':login_orm['company_id'].id
                    
                }
                }
                return res
                
            else:
                res={
                    'status':"token",
                    'message':"Invalid Email Or Password",
                    'status_message':"invalid"
                }
                return res
        else:
            res={
                'status':"failure",
                'message':"You have not Registered, Please Register.",
                'status_message':"notfound"

            }
            return res
# 
    # @http.route('/api/http/welcome', type='http', auth='public', csrf=False, cors='*', methods=['POST'])
    # def login(self, **kw):
    #     # return "hiii"
    #     email = request.params.get('email')
    #     password = request.params.get('password')
    #     token = jwt_request.login(email, password)

    #     login_email = request.env['res.users'].sudo().search([('login', '=', email)])
    #     if login_email:
    #         if token:
    #             login_orm = request.env['res.users'].sudo().search([('login', '=', email)])
    #             # type_users = login_orm.type_users
    #             # new_create_doc = request.env['doctor.registration'].sudo().search_read([('res_users','=',login_orm.id),('status','=','active')],fields=['status','res_users'])
    #             # if new_create_doc:
                
    #             access_app_orm = request.env['access.app'].sudo().search([('name.id', '=', login_orm.id)])
    #             array_access = ast.literal_eval(access_app_orm.access_push)

    #             currency = request.env.user.currency_id.symbol
    #             currency_id = request.env.user.currency_id.id

    #             valss=[]
    #             for i in login_orm:
    #                 date=i['company_ids']
    #                 for rec in date:
    #                     valss.append(rec.id)

    #             res = {
    #             "accessToken": token,
    #             "status": "success",
    #             "message": "Login Successfully",
    #             'status_message':"success",
    #             'data': {
    #                 'email':login_orm['email'],
    #                 # 'phone_number':login_orm['phone_number'],
    #                 'id' : login_orm['id'],
    #                 'type_users': login_orm['type_users'],
    #                 'name':login_orm['name'],
    #                 'partner_id':login_orm['partner_id'].id,
    #                 'currency':currency,
    #                 'currency_id':currency_id,
    #                 'user_access':array_access,
    #                 'allowed_companies':valss,
    #                 'language':login_orm['lang'],
    #                 'employee_id': login_orm['employee_id'].id,
    #                 'default_company':login_orm['company_id'].id
                    
    #             }
    #             }
    #             return res
                
    #         else:
    #             res={
    #                 'status':"failure",
    #                 'message':"Invalid Email Or Password",
    #                 'status_message':"invalid"
    #             }
    #             return res
    #     else:
    #         res={
    #             'status':"failure",
    #             'message':"You have not Registered, Please Register.",
    #             'status_message':"notfound"

    #         }
    #         return res

    @http.route("/api/access_user",type="json",method=["POST","GET"],auth="none",csrf="false",cors='*')
    def access_user_application(self):
        user_id = request.params.get('user_id')
        access_app_orm = request.env['access.app'].sudo().search([('name.id', '=', user_id)])
        if access_app_orm:
            array_access = ast.literal_eval(access_app_orm.access_push)
            return{
                "message" : array_access
            }
        else:
            return{
                "message" : "User not Found"
            }
            
    @http.route('/api/http/me', type='http', auth='public', csrf=False, cors='*')
    @jwt_request.middlewares('jwt')
    def me(self, **kw):
        return jwt_request.response(request.env.user.to_dict())


    @http.route('/api/http/logout', type='http', auth='public', csrf=False, cors='*')
    @jwt_request.middlewares('jwt')
    def logout(self, **kw):
        jwt_request.logout()
        return jwt_request.response()


    @http.route('/api/new_registration', type='json', auth='public', csrf=False, cors='*', methods=['POST'])
    def new_registration(self, email=None, name=None, password=None,user='user' ,**kw):
        name =request.params.get('name')
        email = request.params.get('email')
        password =request.params.get('password')
        phone_number=request.params.get('mobileno')
        
        '''
        In previous version, we use auth_signup to register an external (portal) user.
        For this demo, we use res.users.create instead, this will create an internal user
        '''
        if not is_valid_email(email):
            return jwt_request.response(status=400, data={'message': 'Invalid email address','status': 'failure'})
        if not name:
            return jwt_request.response(status=400, data={'message': 'Name cannot be empty','status': 'failure'})
        if not password:
            return jwt_request.response(status=400, data={'message': 'Password cannot be empty','status': 'failure'})

        # sign up
        try:
            if request.env['res.users'].sudo().search([('login', '=', email)]):
                return jwt_request.response(status=400, data={'message': 'Email address is already exist','status': 'failure'})

            user = request.env['res.users'].sudo().create({
                'login': email,
                'password': password,
                'name': name,
                'email': email, 
            })
            user = request.env['res.users'].sudo().search([('login', '=', email)])
            if request.env['res.users'].sudo().search([('login', '=', email)]):
                #update mobile number in res partner
                partner = request.env['res.users'].sudo().search_read([('id','=',user.id)],fields=['partner_id'])
                partner_id = partner[0]['partner_id'][0]
                partner = request.env['res.partner'].sudo().browse(int(partner_id)).write({'mobile':phone_number})
                # create token
                token = jwt_request.create_token(user)
                return {
                    'message':'Successfully Login',
                     'status':'success',
                    'user': user.to_dict(),
                    'accessToken': token,
                    'data': {
                    'email':user['email'],
                    'name':user['name'],
                    'partner_id':partner_id,
                    }
                    
                }
        except Exception as e:
            _logger.error(str(e))
            return jwt_request.response_500({
                'message': 'Server error'
            })


    @http.route('/api/http/signup', type='http', auth='public', csrf=False, cors='*', methods=['POST'])
    def register(self, email=None, name=None, password=None, **kw):
        '''
        Sign up using auth_signup modules
        '''
        if not is_valid_email(email):
            return jwt_request.response(status=400, data={'message': 'Invalid email address'})
        if not name:
            return jwt_request.response(status=400, data={'message': 'Name cannot be empty'})
        if not password:
            return jwt_request.response(status=400, data={'message': 'Password cannot be empty'})

        # sign up
        try:
            model = request.env['res.users'].sudo()
            signup = getattr(model, 'signup')
            if signup:
                if request.env['res.users'].sudo().search([('login', '=', email)]):
                    return jwt_request.response(status=400, data={'message': 'Email address is not available'})
                data = {
                    'login': email,
                    'password': password,
                    'name': name,
                    'email': email,
                }
                # signup return a tuple (db, login, password)
                # you can use that to call jwt_request.login(login, password)
                signup(data)
                # but, we just need to retrieve the newly created user
                user = model.search([
                    ('login', '=', email)
                ])
                if user:
                    token = jwt_request.create_token(user)
                    return jwt_request.response({
                        'user': user.to_dict(),
                        'token': token
                    })
                raise Exception()
        except SignupError:
            return jwt_request.response({
                'message': 'Signup is currently disabled',
            }, 400)
        except Exception as e:
            _logger.error(str(e))
            return jwt_request.response_500({
                'message': 'Cannot create user'
            })

    def _response_auth(self, token: str):
        return jwt_request.response({
            'user': request.env.user.to_dict(),
            'token': token,
        })


        
    @http.route('/api/product_list', type="json", auth="none", methods=["POST"], csrf=False, cors='*')
    def product_list(self,name=None,ids=None ,**kw):
        ids =request.params.get('id')
        product_varient = []
        partner_search = request.env['product.product'].sudo().search_read([('product_tmpl_id','=',ids)],fields=['product_template_attribute_value_ids'])
        if len(partner_search) > 1:
            for line in partner_search:
                varient_line_id = request.env['product.template.attribute.value'].sudo().search_read([('id','=',line['product_template_attribute_value_ids'])],fields=['product_attribute_value_id','attribute_id'])
                name = varient_line_id[0]['product_attribute_value_id'][1]
                datas = name.split(": ")
                value = request.env['product.attribute.value'].sudo().search_read([('name','=',datas[-1])],fields=['name'])
                data = {
                    'product_id' : line['id'],
                    'attribute_id': varient_line_id[0]['attribute_id'][0],
                    'attribute_name' : varient_line_id[0]['attribute_id'][1],
                    'value_id': value[0]['id'],
                    'value_name': value[0]['name'],
                }
                product_varient.append(data)
                
        return {'attribute':product_varient}
    

    @http.route('/api/user_access', type="json", auth="none", methods=["POST"], csrf=False, cors='*')
    def user_access_fun(self):
        token = request.params.get('token')

        token_user_id=request.env['jwt_provider.access_token'].sudo().search_read([('token','=',token)],fields=['user_id'])
        if token_user_id:
            user_id=None
            for user_token in token_user_id:
                user_id=user_token['user_id'][0]

            user_groups = request.env['res.groups'].sudo().search_read([('users','=',user_id)],fields=['full_name'])
            uservar=[i['full_name'] for i in user_groups]

            currency = request.env.user.currency_id.symbol


            return {
                "status":"success",
                "message":uservar
            }
        else:
            return {
                "status":"failure",
                "message":"ivaild token"
            }
    @http.route('/api/profile_image', type="json", auth="none", methods=["POST"], csrf=False, cors='*')
    def profile_image(self,**kw):
        image = request.params.get('image')
        contact_id = request.params.get('contact_id')
        
        partner = request.env['res.partner'].sudo().browse(contact_id).write({'image_1920':image})
        
        return{'message':'image uploaded'}
    
    
    @http.route('/api/product_image', type="json", auth="none", methods=["POST"], csrf=False, cors='*')
    def product_image(self,**kw):
        image = request.params.get('image')
        product_id = request.params.get('product_id')
        
        product = request.env['product.template'].sudo().browse(product_id).write({'image_1920':image})
        
        return{'message':'image uploaded'}
    
    @http.route('/api/expense_attach', type="json", auth="none", methods=["POST"], csrf=False, cors='*')
    def expense_attach(self):
        res_id = request.params.get('res_id')
        company_id = request.params.get('company_id')
        file_data = request.params.get('files')
        file_names = request.params.get('file_name')
        file_data = ast.literal_eval(file_data)
        file_names = ast.literal_eval(file_names)

        for file,file_name in zip(file_data,file_names):
            file_data = {
                'name' : file_name,
                'type' : 'binary',
                'datas' : file,
                'res_model' : 'hr.expense',
                'res_id' : res_id,
                'public' : True,
                'company_id' : company_id
            }
            attached = request.env['ir.attachment'].sudo().create(file_data)
        return {'message' : 'file attached'}

    @http.route('/api/file_upload', type="json", auth="none", methods=["POST"], csrf=False, cors='*')
    def file_upload(self):
        filename = request.params.get('file_name')
        file_upload_image = request.params.get('files')

        return {'message' : file_upload_image}
    
    
    @http.route('/api/task_attachment', type="json", auth="none", methods=["POST"], csrf=False, cors='*')
    def task_attachment(self,**kw):
        res_id = request.params.get('res_id')
        company_id = request.params.get('company_id')
        file_data = request.params.get('files')
        file_names = request.params.get('file_name')
        file_data = ast.literal_eval(file_data)
        file_name = ast.literal_eval(file_names)
        for name,file in zip(file_name,file_data):
            data = {
                'name' : name,
                'type' : 'binary',
                'datas' : file,
                'public' : True,
                'company_id' : company_id
            }
            attached = request.env['ir.attachment'].sudo().create(data)
            request.env['project.task'].sudo().browse(res_id).write({'attachment_id':[[4,attached.id]]})

        return {'message' : 'file attached'}
    
    @http.route('/api/sale_print', type="http", auth="none", methods=["GET","OPTIONS"], csrf=False, cors='')
    def saleprint_id(self, *kw):
        sale_record=request.params.get('saleid')
        pdf = request.env.ref('hymech_beta.action_report_sale_mas_labellll').sudo().with_user(1)._render_qweb_pdf([int(sale_record)])[0]
        pdf_http_headers = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
        if pdf : 
            return request.make_response(pdf, headers=pdf_http_headers)
        else:
            return werkzeug.wrappers.Response(
            status=404,
            content_type="application/json; charset=utf-8",
            headers=[("Cache-Control", "no-store"),('Access-Control-Allow-Headers', 'Origin, Content-Type, X-Auth-Token, charset'),('Access-Control-Allow-Methods','POST, GET, OPTIONS, DELETE, PUT'), ('Access-Control-Allow-Origin', 'http://localhost:8062'), ("Pragma", "no-cache")],
            response=json.dumps("No Data"),
        )
            
    @http.route('/api/invoice_print', type="http", auth="none", methods=["GET","OPTIONS"], csrf=False, cors='*')
    def invoiceprint_id(self, **kw):
        invoice_record=request.params.get('invoiceid')
        pdf = request.env.ref('hymech_beta.action_report_invoices').sudo().with_user(1)._render_qweb_pdf([int(invoice_record)])[0]
        pdf_http_headers = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
        if pdf : 
            return request.make_response(pdf, headers=pdf_http_headers)    
        else:
            return werkzeug.wrappers.Response(
            status=404,
            content_type="application/json; charset=utf-8",
            headers=[("Cache-Control", "no-store"),('Access-Control-Allow-Headers', 'Origin, Content-Type, X-Auth-Token, charset'),('Access-Control-Allow-Methods','POST, GET, OPTIONS, DELETE, PUT'), ('Access-Control-Allow-Origin', 'http://localhost:8062'), ("Pragma", "no-cache")],
            response=json.dumps("No Data"),
        )

    @http.route('/api/transfer_print', type="http", auth="none", methods=["GET","OPTIONS"], csrf=False, cors='*')
    def transferprint_id(self, **kw):
        transfer_record=request.params.get('transferid')
        pdf = request.env.ref('hymech_beta.action_report_invoice').sudo().with_user(1)._render_qweb_pdf([int(transfer_record)])[0]
        pdf_http_headers = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
        if pdf : 
            return request.make_response(pdf, headers=pdf_http_headers)             
        else:
            return werkzeug.wrappers.Response(
            status=404,
            content_type="application/json; charset=utf-8",
            headers=[("Cache-Control", "no-store"),('Access-Control-Allow-Headers', 'Origin, Content-Type, X-Auth-Token, charset'),('Access-Control-Allow-Methods','POST, GET, OPTIONS, DELETE, PUT'), ('Access-Control-Allow-Origin', 'http://localhost:8062'), ("Pragma", "no-cache")],
            response=json.dumps("No Data"),
        )

    @http.route('/api/timer_on_button', type="json", auth="none", methods=["POST"], csrf=False, cors='*')
    def timer_on_button(self):
        ids = request.params.get('task_id')
        user_id = request.params.get('user_id')
        employee_id = request.params.get('employee_id')
        start_position = request.params.get('start_position')
        end_position = request.params.get('end_position')
        is_timer_on = request.env['account.analytic.line'].sudo().search_read([('task_id','=',ids),('employee_id','=',int(employee_id)),('date_end','=',False)],fields=['date_start','id'])
        if not is_timer_on:
            user =request.env['res.users'].sudo().search_read([('id','=',int(user_id))],fields = ['name'])
            task =request.env['project.task'].sudo().search_read([('id','=',int(ids))],fields = ['task_timer','name','user_id','project_id'])
            # request.env['project.task'].sudo().browse(int(ids)).write({'is_user_working':True})
            data ={
                'name': f"{user[0]['name']} : {task[0]['name']}",
                'task_id': ids,
                'user_id': int(user_id),
                'project_id': task[0]['project_id'][0],
                'date_start': datetime.datetime.now(),
                'date': datetime.datetime.now().date(),
                'employee_id' : int(employee_id),
                # 'lattitude' : start_position,
            }
            request.env['account.analytic.line'].sudo().with_user(int(user_id)).create(data)
            log_create = request.env['mail.message'].sudo().create({
            "body":"Timer Notify",
            "res_id":ids,
            "message_type":"notification",
            "model":"project.task"
            })   
            return  {"message":'timer on'}

        else:
            if not len(is_timer_on) > 1:

                duration = round(( datetime.datetime.now() - is_timer_on[0]['date_start']).total_seconds()/(60 * 60),2)
                request.env['account.analytic.line'].sudo().with_user(int(user_id)).browse(is_timer_on[0]['id']).write({'date_end': datetime.datetime.now(),'unit_amount':duration,'timer_duration':round(duration * 60,2)})
                return  {"message":'timer off'}
            else:
                return  {"message":'Multiple records not closed'}
            
    @http.route('/api/task_update_notification',type="json",auth="none",methods=["POST"],csrf=False,cors='*')
    def task_update_notification(self):
        id = request.params.get("id")
        task_call = request.env['project.task'].sudo().browse(int(id))     
        
        task_call.complete_stage_notification()
        
        return {
            'message' : 'Notification Sent'
            }