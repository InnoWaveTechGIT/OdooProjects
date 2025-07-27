from odoo import http
# from werkzeug.wrappers import Response
import logging
from datetime import datetime
import xmlrpc.client as xmlrpclib
import json
from odoo import models, fields, api
import math
import os
import requests
from odoo.http import request ,Response
# from odoo.http import JsonRequest
import jwt
import re
import time
import base64
import werkzeug.wrappers
from requests_toolbelt.multipart import decoder
from . import verfiy_token
from os import path
from pathlib import Path 
import pathlib
from os import environ
from dotenv import load_dotenv
load_dotenv()
_logger = logging.getLogger(__name__)

def _abs_rout(self,data):
        path1=''
        
        os.path.dirname(os.path.abspath(__file__))

        abs = os.path.dirname(os.path.abspath(__file__))
        abs_sp =abs.split("/")
        
        for i in abs_sp:
            if  i != 'controller':
                path1 += i +'/'
            
        return path1




from pathlib import Path
class Section_Quize(http.Controller):
    url = os.getenv('URL')
    db = os.getenv('db')
    username = os.getenv('username')
    password = os.getenv('password')
    
    def false2empty(self,data):
        result = {}
        result1 = []
        for i in data:
            for key, value in i.items():
                if(value is False and key !=  "is_default" and key != 'is_active'):
                    value = ''
                result[key] = value
            result1.append(result)
            result = {}
    @http.route('/get_section_quize',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_section_quize(self, id,**kw):
        authe = request.httprequest.headers
        token = authe['Authorization'].replace('Bearer ', '')
            
                
                
        try:
            dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
        except Exception as e:
            response = json.dumps({ 'jsonrpc': '2.0', 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        is_submitted = False
        expexted_degree = False
        user_id = int(dec_token['id'])
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        section_id=int(id)
        section_result = http.request.env['section_quize_result'].sudo().search([('user_id' , '=' , user_id) , ('section_id' , '=' , section_id)])
        if len(section_result) != False:
           is_submitted = True
           for rec in section_result:
            if rec.the_expected_degree != 0 : 
                expexted_degree = True

        section_quizes=models.execute_kw(self.db, uid, self.password, 'section_quize', 'search_read', [[['section_id' , '=' , section_id]] ],{'fields': ['id','file_path','file_name' , 'correction_file_path']})
        if section_quizes!=[]:
            section_quizes[0]['is_submitted'] = is_submitted
            section_quizes[0]['expexted_degree'] = expexted_degree
            response = json.dumps({'data': section_quizes[0],'message':'معلومات أختبار القسم  '})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
            
        else :
            response = json.dumps({'data':[],'message':'لا يوجد بيانات'})
            return Response(response,
             status=200,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
            
    @http.route('/add_points_subscriptions',  auth="public",csrf=False, website=True, methods=['POST'])
    def add_points_subscriptions(self,image,payment_type,points_id,**kw):
        points_id=int(points_id)
        payment_type=int(payment_type)
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        
        authe = request.httprequest.headers
        blob=image.read()
        data = os.path.dirname(os.path.abspath(__file__))
        image_file_name=image.filename
        
        image_type = image.filename.split(".")
        
        
        types =['jpeg','JPEG','png','PNG','jpg','JPG']
        if image_type[-1] not in types :
            
            response = json.dumps({"data":[],'message': 'الرجاء ادخال صورة'})
            return Response(
                        response, status=400,
                        headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )            
            
            

            
        fields={}
        if(image != None ):

                
                fields['image_file_name']=image_file_name

                time_stamp = str(time.time())
                # module_path = "/home/vps112/odoo_16/torbetodoo/torbet_app/static/" #servar

                module_path = _abs_rout(self ,data)+"static/subscriptions"#loc
                
                
                
                isExist = os.path.exists(module_path)
                
                
                
                
                if isExist == False:
                    os.mkdir(module_path)
                image= base64.encodebytes(blob)
                fields["image"] = image

                
                
                fields["image_full_url"] = module_path + '/' + \
                time_stamp+image_file_name.replace(" ", "")
                fields["image_path"] = "/taleb/static/" + \
                    time_stamp+fields["image_file_name"].replace(" ", "")
                
            

                
                
                
        elif image == None:
                pass
                
        else:
                
                fields['image_file_name']=""
                fields["image"]=""
                
                return True
        fields['payment_type']=payment_type
        fields['points_id']=points_id
        
        try:
            token = authe['Authorization'].replace('Bearer ', '')
            dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
        
           
        except Exception as e:
            pass
        
        user_id=dec_token['id']
        if verfiy_token.verfiy_token (self,token,str(user_id)) ==False:
            
            response = json.dumps({ 'data': [], 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        fields['user_id']=int(user_id)
        fields['op_number']=""
        fields['sender_name']=""
        
        
        
        create_points_subscriptions = models.execute_kw(self.db, uid, self.password, 'points.subscription', 'create', [fields])
       
       

        if create_points_subscriptions :
                
                response=json.dumps({'data':{'id':create_points_subscriptions},'message': ' تمت أضافة الاشتراك'})
                return Response(
                        response, status=200,
                        headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
                
        else :
            
            response = json.dumps({"data":[],'message': 'بعض الحقول مفقودة'})
            return Response(
                        response, status=400,
                        headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
        
    # @http.route('/subscribe_to_course',  auth="public",csrf=False, website=True, methods=['POST'])
    # def subscribe_to_course(self,**kw): 
    #     add_suscription=[] 
    #     accepted_code = False
    #     discount_amount = 0
    #     common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
    #     uid = common.authenticate(self.db, self.username, self.password, {})
    #     models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))   
    #     authe = request.httprequest.headers     
    #     body =json.loads(request.httprequest.data)
    #     try:
    #         token = authe['Authorization'].replace('Bearer ', '')
    #         dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
        
           
    #     except Exception as e:
    #             response = json.dumps({ 'jsonrpc': '2.0', 'message': 'Unauthorized!','errrror':e})
    #             return Response(
    #             response, status=401,
    #             headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
    #         )
        
    #     user_id=int(dec_token['id'])
    #     if verfiy_token (self,token,str(user_id)) ==False:
            
             
    #         response = json.dumps({ 'data': [], 'message': 'Unauthorized!'})
    #         return Response(
    #         response, status=401,
    #         headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
    #     )
    #         # payment_type  payment_method   
    #     if 'course_id' in body :
    #         course_id=int(body['course_id'])
    #     else :
    #         response = json.dumps({ 'message': 'معرف الكورس غير موجود ضمن الطلب'})
    #         return Response(
    #             response, status=200,
    #             headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
    #         )
            
    #     try:
            
    #             subs=models.execute_kw(self.db,uid,self.password,'subscription','search_read', [['&',['user_id' , '=', user_id],['course_id' , '=' , course_id]]],{'fields': ['id']})
    #             if subs!=[]:
    #                 response = json.dumps({ 'message': 'الطالب مشترك سابقا بهذه الدورة  '})
    #                 return Response(
    #                     response, status=200,
    #                      headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
    #                      )
    #             else:
    #                 if 'code' in body :
    #                     code=body['code']
    #                 promo_code = request.env['promotion.code'].sudo().search(['&',('promotion_code','=',code),('is_valid','=',True)])
                    
    #                 if len(promo_code)!= 0 :
    #                     for course_pro_id in promo_code.course_ids:
                           
                          
    #                         if course_pro_id.id == course_id:
    #                             accepted_code = True
    #                             discount_amount = promo_code.discount_percentage
    #                             break
    #                         else:
    #                             accepted_code = False

    #     except Exception as e:
    #         add_suscription=[]
       
    #     if accepted_code == True: 
    #         #Create payment subscribtion with discount and payment type Coupon
    #         create_paymnet=
    #         add_suscription = models.execute_kw(self.db, uid, self.password, 'subscription', 'create', [{'course_id':course_id,'user_id':user_id,'discont':discount_amount}])
           
    #     else:
    #         # Create Direct 
    #         add_suscription = models.execute_kw(self.db, uid, self.password, 'subscription', 'create', [{'course_id':course_id,'user_id':user_id}])
    #     if add_suscription:
    #          response = json.dumps({"data":[],'message': "تم أشتراك الطالب في الدورات بنجاح"})
    #          return Response(
    #                         response, status=200,
    #                         headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
    #                     )
            
    #     else:
    #         response = json.dumps({"data":[],'message': "عدد النقاط لا يكفي "})
    #         return Response(
    #                         response, status=200,
    #                         headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
    #                     )
    @http.route('/get_user_points_history',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_user_points_history(self,**kw):  
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        uid = common.authenticate(self.db, self.username, self.password, {})
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))   
        authe = request.httprequest.headers     
        try:
            token = authe['Authorization'].replace('Bearer ', '')
            dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
        
           
        except Exception as e:
                response = json.dumps({ 'jsonrpc': '2.0', 'message': 'Unauthorized!','errrror':e})
                return Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        
        user_id=dec_token['id']
        if verfiy_token.verfiy_token (self,token,str(user_id)) ==False:
            
            
            response = json.dumps({ 'data': [], 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        withdraw_points=[]
        total=[]
        try:
            
        
            user_subscriptions=models.execute_kw(self.db, uid, self.password, 'points.user', 'search_read', [[['user_id' , '=' , user_id]] ],{'fields': ["total_number_of_points",'last_number_of_points','points','created_date']})
            user_points_suscriptions=models.execute_kw(self.db,uid,self.password,'points.subscription','search_read', [[['user_id' , '=' , user_id]] ],{'fields': ['total_number_of_points','last_number_of_points','created_date',"number_of_points",'accepted','payment_type']})
            user_course_subscriptions=models.execute_kw(self.db,uid,self.password,'subscription','search_read',[[['user_id' , '=' , user_id]] ],{'fields': ['course_id','points','created_date','user_total_point']})
            for rec in user_course_subscriptions:
                rec['course_name']=rec['course_id'][1]
                rec['course_id']=rec['course_id'][0]
                del rec['course_id']
            for rec in user_points_suscriptions:
                rec['payment_method']=rec['payment_type'][1]
                rec['payment_method_id']=rec['payment_type'][0]
                del rec['payment_type']
            total.append(user_subscriptions)
            total.append(user_points_suscriptions)
            withdraw_points.append(user_course_subscriptions)
            
        except Exception as e:
           
             response = json.dumps({"data":[],'message': " حدث خطأ ما "})
             return Response(
                            response, status=200,
                            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                        )
        if  withdraw_points!=[]:
            withdraw_points=withdraw_points[0]   
        if total!=[]:
             response = json.dumps({"data":{"charge_points":total,"withdraw_points":withdraw_points},'message': "سجل عمليات شحن وسحب النقاط"})
             return Response(
                            response, status=200,
                            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                        )
            
        else:
            response = json.dumps({"data":[],'message': "لا يوجد عمليات تحويل للمستخدم "})
            return Response(
                            response, status=200,
                            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                        )
    @http.route('/get_pending_points_requests',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_pending_point_requests(self,**kw):
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        uid = common.authenticate(self.db, self.username, self.password, {})
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))   
        authe = request.httprequest.headers   
        try:
            token = authe['Authorization'].replace('Bearer ', '')
            dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
        
           
        except Exception as e:
                response = json.dumps({ 'jsonrpc': '2.0', 'message': 'Unauthorized!'})
                return Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        
        user_id=dec_token['id']
        if verfiy_token.verfiy_token(self,token,str(user_id)) ==False:
            
            response = json.dumps({ 'data': [], 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        pending_requests=models.execute_kw(self.db,uid,self.password,'points.subscription','search_read', [['&',['accepted' , '=', False],['user_id' , '=' , user_id]]],{'fields': ['last_number_of_points','created_date',"number_of_points",'accepted','payment_type']})
        if pending_requests!=[]:
            for rec in pending_requests:
                rec['payment_method']=rec['payment_type'][1]
                del rec['payment_type']
            response = json.dumps({"data":pending_requests,'message': "عمليات شحن النقاط المعلقة"})
            return Response(
                            response, status=200,
                            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                        )
            
        else:
            response = json.dumps({"data":[],'message': "لا يوجد عمليات شحن للمستخدم "})
            return Response(
                            response, status=200,
                            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                        )
        

    @http.route('/get_subscriped_courses',  auth="public",csrf=False, website=True, methods=['GET'])  
    def get_subscriped_courses(self,**kw):  
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))  
        uid = common.authenticate(self.db, self.username, self.password, {})  
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))     
        authe = request.httprequest.headers     
        fileds=[]  
        watched=[]
        watched_vid = 0
        try:  
            token = authe['Authorization'].replace('Bearer ', '')  
            dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])  
             
        except Exception as e:  
                response = json.dumps({ 'jsonrpc': '2.0', 'message': 'Unauthorized!'})  
                return Response(  
                response, status=401,  
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]  
            )  
          
        user_id=dec_token['id']  
        if verfiy_token.verfiy_token (self,token,str(user_id)) ==False:  
              
            response = json.dumps({ 'data': [], 'message': 'Unauthorized!'})  
            return Response(  
            response, status=401,  
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]  
        )  
         
        user_courses=models.execute_kw(self.db,uid,self.password,'subscription','search_read',[[['user_id' , '=' , user_id]] ],{'fields': ['course_id','start_date','end_date']})  
  
        if user_courses!=[]:  
            for rec in user_courses:  
                row={}  
                course_info=models.execute_kw(self.db,uid,self.password,'courses','search_read',[[['id' , '=' , rec['course_id'][0]]] ],{'fields': ['teacher_name','image_path','name','date_of_create']})  
                if course_info!=[]:  
                    row['course_id']=rec['course_id'][0]  
                    row['teacher_name']=course_info[0]['teacher_name']  
                    row['course_name']=course_info[0]['name']  
                    row['image_path']=course_info[0]['image_path']  
                    row['start_date']=rec['start_date']  
                    row['end_date']=rec['end_date']  
                    session_watched = models.execute_kw(self.db, uid, self.password, 'session_status', 'search_read', [['&',['user_id','=',user_id],['course_name' , '=' , int(rec['course_id'][0])]]], {'fields': ['session_id']})  
                    all_session = models.execute_kw(self.db, uid, self.password, 'course.video', 'search', [[['course_id' , '=' , int(rec['course_id'][0])]]])  
                    for data in session_watched: 
                        if data['session_id']:  
                            watched.append(data['session_id'][0])  
                        else:  
                            pass  
  
                    watched_vid = len(watched)
                    all_session = len(all_session)
                    if all_session != 0:
                        percentage = (watched_vid / all_session) * 100
                    else:
                        percentage = 0.0

                    if percentage != 0.0:
                        row['progres'] = percentage
                        fileds.append(row)
             
            response = json.dumps({"data":fileds,'message': "الدورات المسجل بها الطالب"})  
            return Response(  
                            response, status=200,  
                            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]  
                        )  
              
        else:  
            response = json.dumps({"data":[],'message': "    لا يوجد دورات مسجلة للطالب "})  
            return Response(  
                            response, status=200,  
                            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]  
                        )
    @http.route('/message_support',  auth="public",csrf=False, website=True, methods=['POST'])
    def message_support(self,message,conversation_id=None, **kw):
        size=0
        loctions=[]
        body=request.httprequest.files.getlist('image[]')
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        authe = request.httprequest.headers
        # handle message image
        
        fields={}
        image_dic={}
        uid = common.authenticate(self.db,self.username, self.password, {})
        try:
            token = authe['Authorization'].replace('Bearer ', '')
            dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
        except Exception as e:
            response = json.dumps({ 'data': [], 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        user_id = int(dec_token['id'])
        fields['user_id']=user_id
        fields['body']=message
        
        if verfiy_token.verfiy_token (self,token,str(user_id)) ==False:
            
            response = json.dumps({ 'data': [], 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        data = os.path.dirname(os.path.abspath(__file__))
        if conversation_id == None:
            check_last_conversation=models.execute_kw(self.db, uid, self.password, 'support.conversation', 'search_read', [[['user_id' , '=' , user_id]] ],{'fields': ['id']})
            if check_last_conversation==[]:
                new_message=models.execute_kw(self.db, uid, self.password, 'support.message', 'create', [fields])
                
                
                # new_message_image=models.execute_kw(self.db, uid, self.password, 'support.message.images', 'create', [fields])
                
                
                if(body != None ):
                    for image in body:
                        blob = image.read()
                        size += len(blob) 
                        image_file_name=image.filename
                    
                      
                        image_file_name=image.filename
                        time_stamp = str(time.time())
                        image_dic['image_file_name']=image_file_name.replace(" ", "")
                        image_dic['image_id']=new_message
                        image_dic['image']=base64.encodebytes(blob)
                
                        # module_path = "/home/vps112/odoo_16/torbetodoo/torbet_app/static/" #servar

                        module_path = _abs_rout(self ,data)+"static/messages_images"#loc
                        isExist = os.path.exists(module_path)

                        if isExist == False:
                            os.mkdir(module_path)
                        # blob = image.read()
                        section_image= base64.encodebytes(blob)
                        

                        
                        with open(os.path.join(module_path, time_stamp + image_dic['image_file_name']), "wb+") as f:
                            f.write(base64.b64decode(section_image))
                        image_dic["image_full_url"] = module_path + '/' + \
                        time_stamp+image_file_name.replace(" ", "")
                        image_dic["image_path"]='/taleb/static/messages_images/'+time_stamp + image_dic['image_file_name']

                        new_message_image=models.execute_kw(self.db, uid, self.password, 'support.message.images', 'create', [image_dic])
                        image_dic={}

                    # 
                        
                    
                
                else:
                    
                    pass
                    

                conversation=models.execute_kw(self.db, uid, self.password, 'support.message', 'search_read', [[['id' , '=' , new_message]] ],{'fields': ['conversation_id']})
                
                
                if new_message:
                    response = json.dumps({ 'data': [{'conversation_id':conversation[0]['conversation_id'][0]}], 'support.message': 'تم أضافة محادثة جديدة'})
                    return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
            else :
                
                conversation_id=check_last_conversation[0]['id']
                
        if conversation_id :
            correct_user=models.execute_kw(self.db, uid, self.password, 'support.conversation', 'search_read', [[['id' , '=' ,conversation_id]] ],{'fields': ['user_id']})
            if correct_user!=[]:
                if correct_user[0]['user_id'][0]!=user_id:
                    response = json.dumps({ 'data': [{}], 'support.message': 'المحادثة ليست للمستخدم'})
                    return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                        )
                
            
        
            try :
                new_message_exist_conversation=models.execute_kw(self.db, uid, self.password, 'support.message', 'create', [{'user_id': user_id ,'body':message,'conversation_id':conversation_id}])
                if(body != None ):
                    for image in body:
                        blob = image.read()
                        size += len(blob) 
                        image_file_name=image.filename
                        image_file_name=image.filename
                        time_stamp = str(time.time())
                        image_dic['image_file_name']=image_file_name.replace(" ", "")
                        image_dic['image_id']=new_message_exist_conversation
                        image_dic['image']=base64.encodebytes(blob)
                        module_path = _abs_rout(self ,data)+"static/messages_images"#loc
                        isExist = os.path.exists(module_path)
                        if isExist == False:
                            os.mkdir(module_path)
                        section_image= base64.encodebytes(blob)
                        with open(os.path.join(module_path, time_stamp + image_dic['image_file_name']), "wb+") as f:
                            f.write(base64.b64decode(section_image))
                        image_dic["image_full_url"] = module_path + '/' + \
                        time_stamp+image_file_name.replace(" ", "")
                        image_dic["image_path"]='/taleb/static/messages_images/'+time_stamp + image_dic['image_file_name']
                        new_message_image=models.execute_kw(self.db, uid, self.password, 'support.message.images', 'create', [image_dic])
                        image_dic={}
            except:
                response = json.dumps({ 'data': [{}], 'support.message': 'رقم المحادثة غير موجود'})
                return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
                
            if new_message_exist_conversation:
                
                response = json.dumps({'data': [{'conversation_id':conversation_id}], 'message': 'تم أضافة  الرسالة الى المحادثة'})
                return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
        
        
        
        
        
        
        
        
        
        
        
        
        
                

    @http.route('/dacast_data',  auth="public",csrf=False, website=True, methods=['POST'])
    def dacast_data():
        # common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        # models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        # uid = common.authenticate(self.db, self.username, self.password, {})
        isExist = os.path.exists('/home/vpsa15/taleb_odoo16/talebodoo/zxcvasdzx.txt')
                   
        if isExist == False:
            os.mkdir('/home/vpsa15/taleb_odoo16/talebodoo/zxcvasdzx.txt')
        file2 = open('/home/vpsa15/taleb_odoo16/talebodoo/zxcvasdzx.txt', 'w')
        multipart_data = decoder.MultipartDecoder.from_response(request)
        file1 = open('/home/vpsa15/taleb_odoo16/talebodoo/myfile.txt', 'w')
        file1.write(multipart_data)
        file1.close()
        file2.close()
    @http.route('/get_student_rate',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_student_rate(self,course_id=int(0),**kw):
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        authe = request.httprequest.headers
        token = authe['Authorization'].replace('Bearer ', '')
        # body =json.loads(request.httprequest.data)
        try:
           dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
           
           
        except Exception as e:
            response = json.dumps({ 'data': [], 'message': 'Unauthorized!'})
            return Response(
            response, status=400,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
    
        user_id = dec_token['id']
        if verfiy_token.verfiy_token (self,token,str(user_id)) ==False:
            
            response = json.dumps({ 'data': [], 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        login=dec_token['login']
        course_id=int(course_id)
        if course_id ==0 :
    
            response = json.dumps({ 'message': 'معرف الكورس غير موجود ضمن الطلب'})
            return Response(
                response, status=400,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        else :
            rate=-1
            try:
                course_value =models.execute_kw(self.db, uid, self.password, 'course.result', 'search_read', [[['course_id' , '=' , course_id]]],{'fields':['course_result_id','result'], 'order': 'result desc'})
                
                
            except:
                response = json.dumps({ 'data': [], 'message': ' حدث خطأ'})
                return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
            if course_value==[]:
                response = json.dumps({ 'data': [], 'message': '    الكورس غير موجود أو لا يوجد نتائج متعلقة بهذه الدورة'})
                return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
                
            for i in range(len(course_value)):
                if course_value[i]['course_result_id'][0]==user_id:
                    rate=i
            if rate != -1:
                response = json.dumps({"data":{'rate':int(rate+1)},'message': 'ترتيب الطالب'})
                return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
            else :
                response = json.dumps({"data":{},'message': 'لا يوجد نتيجة متعلقة بهذا الطالب'})
                return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])
       
    @http.route('/subscribe_to_section',  auth="public",csrf=False, website=True, methods=['POST'])
    def subscribe_to_section(self,**kw):
        accepted_code = False
        discount_amount = 0
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        uid = common.authenticate(self.db, self.username, self.password, {})
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))   
        authe = request.httprequest.headers     
        body =json.loads(request.httprequest.data)
        fileds={}
        
        try:
            token = authe['Authorization'].replace('Bearer ', '')
            dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
        
           
        except Exception as e:
                response = json.dumps({ 'jsonrpc': '2.0', 'message': 'Unauthorized!'})
                return Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        
        user_id=int(dec_token['id'])
        is_active  = verfiy_token.verify_active(self,user_id)
        if not is_active :
            response = json.dumps({ 'data': [], 'message': 'حسابك ليس نشطا !'})
            return Response(
            response, status=400,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        if 'section_id' in body :
            section_id=int(body['section_id'])

        else :
            response = json.dumps({ 'message': 'معرف الكورس غير موجود ضمن الطلب'})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        if 'course_id' in body :
            course_id=int(body['course_id'])
        else :
            response = json.dumps({ 'message': 'معرف الكورس غير موجود ضمن الطلب'})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        is_subscribtion = models.execute_kw(self.db,uid, self.password, 'purchased_sections', 'search_read', [['&',['user_id', '=', int(dec_token['id'])],['section_id','=', section_id]]],{'fields': ['id']} )
        is_subscribtion_course = models.execute_kw(self.db,uid, self.password, 'subscription', 'search_read', [['&',['user_id', '=', int(dec_token['id'])],['course_id','=', course_id]]],{'fields': ['id']} )
        if is_subscribtion == []:
            # sub_to_course= request.env['subscription'].create({
            #     'user_id':user_id,
            #     'course_id' : course_id,
            # })
            try: 
                request.env['subscription_payments'].sudo().create({
                    'user_id':user_id,
                    'section_ids' : [[6,False,[section_id]]],
                    'course_id' : course_id
                })
            
                response = json.dumps({ 'message': 'تم الاشتراك بالقسم'})
                return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
            
            except Exception as e:
                response = json.dumps({ 'message': str(e)})
                return Response(
                response, status=400,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        # elif is_subscribtion == [] and is_subscribtion_course != []:
        #     request.env['subscription_payments'].create({
        #         'user_id':user_id,
        #         'section_id' : section_id,
        #         'course_id' : course_id,
        #         'purchased_section_id' : is_subscribtion_course[0]['id']
        #     })
        #     response = json.dumps({ 'message': 'تم الاشتراك بالقسم'})
        #     return Response(
        #         response, status=200,
        #         headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        #     )
        else:
            response = json.dumps({ 'message': 'الطالب مشترك سابقا'})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
# create subscribe to course   
#
    @http.route('/subscribe_to_course',  auth="public",csrf=False, website=True, methods=['POST'])
    def subscribe_to_course(self,**kw):
        accepted_code = False
        discount_amount = 0
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        uid = common.authenticate(self.db, self.username, self.password, {})
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))   
        authe = request.httprequest.headers     
        body =json.loads(request.httprequest.data)
        fileds={}
        
        try:
            token = authe['Authorization'].replace('Bearer ', '')
            dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
        
           
        except Exception as e:
                response = json.dumps({ 'jsonrpc': '2.0', 'message': 'Unauthorized!','errrror':e})
                return Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        
        user_id=int(dec_token['id'])
        if verfiy_token.verfiy_token (self,token,str(user_id)) ==False:
            
             
            response = json.dumps({ 'data': [], 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        is_active  = verfiy_token.verify_active(self,user_id)
        if not is_active :
            response = json.dumps({ 'data': [], 'message': 'حسابك ليس نشطا !'})
            return Response(
            response, status=400,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
            # payment_type  payment_method   
        if 'course_id' in body :
            course_id=int(body['course_id'])
        else :
            response = json.dumps({ 'message': 'معرف الكورس غير موجود ضمن الطلب'})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
       
        if "code" in body and body['code']=="":
            payment_type="Direct"
        else :
            
             payment_type="Coupon"
        if "number_of_payments" in body and body['number_of_payments']=="":
            payment_method="كاش"
        else :
            payment_method="تقسيط"
            
            
            
       
        subs=models.execute_kw(self.db,uid,self.password,'subscription','search_read', [['&',['user_id' , '=', user_id],['course_id' , '=' , course_id]]],{'fields': ['id']})
        if subs!=[]:
            response = json.dumps({ 'message': 'الطالب مشترك سابقا بهذه الدورة  '})
            return Response(
                response, status=200,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
        
        user_points=models.execute_kw(self.db, uid, self.password, 'res.users', 'search_read',[[['id' , '=' , user_id]]],{
                                        'fields': ['id','points']})
        
        user_points=user_points[0]['points']
        course_points=models.execute_kw(self.db,uid,self.password,'courses','search_read', [[['id' , '=', course_id]]],{'fields': ['id','cost']})
        course_points=course_points[0]['cost']
        if payment_method=="كاش":
            if payment_type=="Direct":
                if int(course_points)>int(user_points):
                    response = json.dumps({ 'message': '   الطالب لا يملك ما يكفي من النقاط للأشتراك بالكورس   '})
                    return Response(
                response, status=400,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
                    
                #check user points and course cost 
                fileds['user_id']=user_id
                fileds['payment_type']=payment_type
                fileds['payment_method']=payment_method
                fileds['course_id']=course_id
                
            if payment_type=="Coupon":
                if 'code' in body :
                        code=body['code']
                        
                else :
                    # print("1 >>>")
                    response = json.dumps({ 'message': 'يرجى ادخال كود الكوبون'})
                    return Response(
                response, status=403,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
                    
                promo_code = request.env['promotion.code'].sudo().search(['&',('promotion_code','=',code),('is_valid','=',True)])
                
                if len(promo_code)!= 0 :
                    for course_pro_id in promo_code.course_ids:
                        
                        
                        if course_pro_id.id == course_id:
                            accepted_code = True
                            discount_amount = promo_code.discount_percentage
                            break
                        else:
                            accepted_code = False
    
                if accepted_code == False :
                    response = json.dumps({ 'message': ' كود الكوبون غير صالح '})
                    return Response(
                response, status=200,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
                discount_amount1=int(course_points)*discount_amount
                discount_amount1=discount_amount1/100
                course_points=int(course_points)-int(discount_amount)
                if int(course_points)>int(user_points):
                    response = json.dumps({ 'message': '   الطالب لا يملك ما يكفي من النقاط للأشتراك بالكورس   '})
                    return Response(
                response, status=400,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
                
                fileds['user_id']=user_id
                fileds['course_id']=course_id
                fileds['payment_type']=payment_type
                fileds['payment_method']=payment_method
                fileds['discont']=discount_amount
        elif payment_method=="تقسيط":
            if payment_type=="Direct":
                if "number_of_payments" in body:
                    nop=int(body['number_of_payments'])
                else :
                    response = json.dumps({ 'message': 'يرجى تحديد عدد الأقساط  '})
                    return Response(
                response, status=200,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
                    
                pay_amount=int(course_points)//int(body['number_of_payments'])
                if int(pay_amount)>int(user_points):
                    response = json.dumps({ 'message': '   الطالب لا يملك ما يكفي من النقاط للأشتراك بالكورس   '})
                    return Response(
                response, status=403,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
                
                fileds['user_id']=user_id
                fileds['course_id']=course_id
                fileds['payment_type']=payment_type
                fileds['payment_method']=payment_method
                fileds['number_of_payments']=body['number_of_payments']
                fileds['pyment_number']=1
            elif payment_type=="Coupon":
                if "number_of_payments" in body:
                    nop=int(body['number_of_payments'])
                else :
                    response = json.dumps({ 'message': 'يرجى تحديد عدد الأقساط  '})
                    return Response(
                response, status=200,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
                # get coupon 
                if 'code' in body :
                        code=body['code']
                        
                else :
                    # print("2 >>>")
                    response = json.dumps({ 'message': 'يرجى ادخال كود الكوبون'})
                    return Response(
                response, status=403,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
                    
                promo_code = request.env['promotion.code'].sudo().search(['&',('promotion_code','=',code),('is_valid','=',True)])
                
                if len(promo_code)!= 0 :
                    for course_pro_id in promo_code.course_ids:
                        
                        
                        if course_pro_id.id == course_id:
                            accepted_code = True
                            discount_amount = promo_code.discount_percentage
                            break
                        else:
                            accepted_code = False
    
                if accepted_code == False :
                    response = json.dumps({ 'message': ' كود الكوبون غير صالح '})
                    return Response(
                response, status=200,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
                # end get coupon
                discount_amount1=discount_amount*int(course_points)
                discount_amount1=discount_amount1/100
                
                
                pay_amount=int(course_points)/int(body['number_of_payments'])
                pay_amount=pay_amount-discount_amount1
                if int(pay_amount)>int(user_points):
                    response = json.dumps({ 'message': '   الطالب لا يملك ما يكفي من النقاط للأشتراك بالكورس   '})
                    return Response(
                response, status=403,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
                
                fileds['user_id']=user_id
                fileds['course_id']=course_id
                fileds['payment_type']=payment_type
                fileds['payment_method']=payment_method
                fileds['number_of_payments']=body['number_of_payments']
                fileds['pyment_number']=1
                fileds['discont']=discount_amount
        if fileds!={}:  
            # print("fields >>>" , fileds)
            create_subscribtion_payments = models.execute_kw(self.db, uid, self.password, 'subscription_payments', 'create', [fileds])
            if payment_method=="تقسيط":
                idd=  int(create_subscribtion_payments)
                models.execute_kw(self.db, uid, self.password, 'subscription_payments', 'write', [[idd], {'pyment_number':1}])
            response = json.dumps({ 'message': 'تم أضافة الأشتراك بنجاح'})
            return Response(
            response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
            
        
            
    @http.route('/pay_installment',  auth="public",csrf=False, website=True, methods=['POST'])
    def pay_installment(self,**kw):
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        uid = common.authenticate(self.db, self.username, self.password, {})
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))   
        authe = request.httprequest.headers     
        body =json.loads(request.httprequest.data)
        
        try:
            token = authe['Authorization'].replace('Bearer ', '')
            dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
        
           
        except Exception as e:
                response = json.dumps({ 'jsonrpc': '2.0', 'message': 'Unauthorized!','errrror':e})
                return Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        
        user_id=int(dec_token['id'])
        if verfiy_token.verfiy_token(self,token,str(user_id)) ==False:
            
             
            response = json.dumps({ 'data': [], 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
            # payment_type  payment_method   
        if 'course_id' in body :
            course_id=int(body['course_id'])
        else :
            response = json.dumps({ 'message': 'معرف الكورس غير موجود ضمن الطلب'})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
           
        get_subs_payment=models.execute_kw(self.db,uid, self.password, 'subscription_payments', 'search_read', [['&',['user_id', '=', user_id],['course_id','=',course_id]]],{'fields': ['id','pyment_number','payment_tracker_ids','number_of_payments']} )

        if get_subs_payment==[]:
            response = json.dumps({ 'message': 'الطالب غير مشترك بالدورة'})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        payment_number=int(get_subs_payment[0]['pyment_number'])
        number_of_payments=int(get_subs_payment[0]['number_of_payments'])
        if payment_number +1>number_of_payments:
            response = json.dumps({ 'message': 'تم تسديد كافة الدفعات مسبقا'})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
            
        payment_id=int(get_subs_payment[0]['id'])
        user_points=models.execute_kw(self.db, uid, self.password, 'res.users', 'search_read',[[['id' , '=' , user_id]]],{
                                        'fields': ['id','points']})
        user_points=user_points[0]['points']
        # get payment amount 
        payment_amount_id=int(get_subs_payment[0]['payment_tracker_ids'][payment_number-1])
        payment_amount=models.execute_kw(self.db, uid, self.password, 'payments_tracker', 'search_read',[[['id' , '=' , payment_amount_id]]],{
                                        'fields': ['id','payment_amount']})
        payment_amount=int(payment_amount[0]['payment_amount'])
        if payment_amount>user_points:
            response = json.dumps({ 'message': '   الرصيد غير كافي لدفع الأشتراك'})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        
        
        models.execute_kw(self.db, uid, self.password, 'subscription_payments', 'write', [[payment_id], {'pyment_number':payment_number+1}])
        # except:
        #     response = json.dumps({ 'message': ' تم تسديد كامل دفعات الكورس سابقا'})
        #     return Response(
        #         response, status=200,
        #         headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        #     )
            
        response = json.dumps({ 'message': ' تم تسديد الدفعة بنجاح'})
        return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        
                
    @http.route('/subscribe_to_package',  auth="public",csrf=False, website=True, methods=['POST'])
    def subscribe_to_package(self,**kw):
       
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        uid = common.authenticate(self.db, self.username, self.password, {})
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))   
        authe = request.httprequest.headers     
        body =json.loads(request.httprequest.data)
        fileds={}
        accepted_code = False
        try:
            token = authe['Authorization'].replace('Bearer ', '')
            dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
        
           
        except Exception as e:
                response = json.dumps({ 'jsonrpc': '2.0', 'message': 'Unauthorized!','errrror':e})
                return Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        
        user_id=int(dec_token['id'])
        if verfiy_token.verfiy_token (self,token,str(user_id)) ==False:
            
             
            response = json.dumps({ 'data': [], 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
            # payment_type  payment_method   
        if 'package_id' in body :
            package_id=int(body['package_id'])
        else :
            response = json.dumps({ 'message': 'معرف الكورس غير موجود ضمن الطلب'})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        
       
        if body['number_of_payments']=="":
            payment_method="كاش"
        else :
            payment_method="تقسيط"
        if body['code']=="":
            payment_type="Direct"
        else :
            payment_type="Coupon"
        

        
        user_points=models.execute_kw(self.db, uid, self.password, 'res.users', 'search_read',[[['id' , '=' , user_id]]],{
                                        'fields': ['id','points']})
        
        user_points=user_points[0]['points']
        package_points=models.execute_kw(self.db,uid,self.password,'packages','search_read', [[['id' , '=', package_id]]],{'fields': ['id','new_price','cost2','cost4','cost5']})
        # print("package pointss info")
        # print(package_points)
       
        if payment_method=="كاش":
            if payment_type=="Direct":
                package_points=package_points[0]['new_price']
            
                if int(package_points) > int(user_points):
                    response = json.dumps({ 'message': '   الطالب لا يملك ما يكفي من النقاط للأشتراك بالحزمة   '})
                    return Response(
                response, status=403,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
                    
                #check user points and course cost 
                fileds['user_id']=user_id
                fileds['payment_type']=payment_type
                fileds['payment_method']=payment_method
                fileds['Package']=package_id
                # fileds['course_id']="1"
                
            elif payment_type=="Coupon":
                
                
                
                
                
                if 'code' in body :
                        code=body['code']
                        
                else :
                    # print("3 >>>")
                    response = json.dumps({ 'message': 'يرجى ادخال كود الكوبون'})
                    return Response(
                response, status=403,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
                    
                promo_code = request.env['package_promotion.code'].sudo().search(['&',('promotion_code','=',code),('is_valid','=',True)])
                
                if len(promo_code)!= 0 :
                    for package_pro_id in promo_code.package_ids:
                        
                        if package_pro_id.id == package_id:
                            accepted_code = True
                            discount_amount = promo_code.discount_percentage
                            break
                        else:
                            accepted_code = False
    
                if accepted_code == False :
                    response = json.dumps({ 'message': ' كود الكوبون غير صالح '})
                    return Response(
                response, status=200,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
                package_points=package_points[0]['new_price']
                discount_amount1=int(package_points)*int(discount_amount)
                discount_amount1=int(discount_amount1/100)
                package_points=int(package_points)-int(discount_amount)
                
                if int(package_points)>int(user_points):
                    response = json.dumps({ 'message': '   الطالب لا يملك ما يكفي من النقاط للأشتراك بالكورس   '})
                    return Response(
                response, status=403,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
                
                fileds['user_id']=user_id
                fileds['Package']=package_id
                fileds['payment_type']=payment_type
                fileds['payment_method']=payment_method
                fileds['discont']=discount_amount
                #end package coupon
        elif payment_method=="تقسيط":
            if payment_type=="Direct":
            
                if "number_of_payments" in body:
                    nop=int(body['number_of_payments'])
                else :
                    response = json.dumps({ 'message': 'يرجى تحديد عدد الأقساط  '})
                    return Response(
                response, status=200,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
                if nop==2:
                    
                    package_points=int(package_points[0]['cost2'])
                elif nop==5:
                     package_points=int(package_points[0]['cost5'])
                elif nop==4:
                    package_points=int(package_points[0]['cost4'])
                pay_amount=package_points//int(body['number_of_payments'])
                if int(pay_amount)>int(user_points):
                    response = json.dumps({ 'message': '   الطالب لا يملك ما يكفي من النقاط للأشتراك بالكورس   '})
                    return Response(
                response, status=403,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
                
                fileds['user_id']=user_id
                fileds['Package']=package_id
                fileds['payment_type']=payment_type
                fileds['payment_method']=payment_method
                fileds['number_of_payments']=body['number_of_payments']
                fileds['pyment_number']=0
            # Coupon with installmentss 
            elif payment_type=="Coupon":
                if 'code' in body :
                        code=body['code']
                        
                else :
                    # print("4 >>>")
                    response = json.dumps({ 'message': 'يرجى ادخال كود الكوبون'})
                    return Response(
                response, status=403,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
                    
                promo_code = request.env['package_promotion.code'].sudo().search(['&',('promotion_code','=',code),('is_valid','=',True)])
                
                if len(promo_code)!= 0 :
                    for package_pro_id in promo_code.package_ids:
                        
                        if package_pro_id.id == package_id:
                            accepted_code = True
                            discount_amount = promo_code.discount_percentage
                            break
                        else:
                            accepted_code = False
    
                if accepted_code == False :
                    response = json.dumps({ 'message': ' كود الكوبون غير صالح '})
                    return Response(
                response, status=200,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
                # installment 
                if "number_of_payments" in body:
                    nop=int(body['number_of_payments'])
                else :
                    response = json.dumps({ 'message': 'يرجى تحديد عدد الأقساط  '})
                    return Response(
                response, status=200,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
                if nop==2:
                    
                    package_points=int(package_points[0]['cost2'])
                elif nop==5:
                     package_points=int(package_points[0]['cost5'])
                elif nop==4:
                    package_points=int(package_points[0]['cost4'])
                discount_amount1=discount_amount*package_points
                discount_amount1=discount_amount1//100
                pay_amount=package_points//int(body['number_of_payments'])
                if int(pay_amount)>int(user_points):
                    response = json.dumps({ 'message': '   الطالب لا يملك ما يكفي من النقاط للأشتراك بالكورس   '})
                    return Response(
                response, status=403,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
                
                fileds['user_id']=user_id
                fileds['Package']=package_id
                fileds['payment_type']=payment_type
                fileds['payment_method']=payment_method
                fileds['number_of_payments']=body['number_of_payments']
                fileds['pyment_number']=0
                fileds['discont']=discount_amount
                
                
                
                # end installment  
            # end Coupon and installment 
               
        if fileds!={}:
            create_subscribtion_payments = models.execute_kw(self.db, uid, self.password, 'package_subscription_payments', 'create', [fileds])
            if payment_method=="تقسيط":
                idd=  int(create_subscribtion_payments)
                models.execute_kw(self.db, uid, self.password, 'package_subscription_payments', 'write', [[idd], {'pyment_number':1}])
            response = json.dumps({ 'message': 'تم أضافة الأشتراك بنجاح'})
            return Response(
            response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
       
            
                
    @http.route('/pay_package_installment',  auth="public",csrf=False, website=True, methods=['POST'])
    def pay_package_installment(self,**kw):
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        uid = common.authenticate(self.db, self.username, self.password, {})
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))   
        authe = request.httprequest.headers     
        body =json.loads(request.httprequest.data)
        
        try:
            token = authe['Authorization'].replace('Bearer ', '')
            dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
        
           
        except Exception as e:
                response = json.dumps({ 'jsonrpc': '2.0', 'message': 'Unauthorized!','errrror':e})
                return Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        
        user_id=int(dec_token['id'])
        if verfiy_token.verfiy_token (self,token,str(user_id)) ==False:
            
             
            response = json.dumps({ 'data': [], 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
            # payment_type  payment_method   
        if 'package_id' in body :
            package_id=int(body['package_id'])
        else :
            response = json.dumps({ 'message': 'معرف الكورس غير موجود ضمن الطلب'})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
           
        get_subs_payment=models.execute_kw(self.db,uid, self.password, 'package_subscription_payments', 'search_read', [['&',['user_id', '=', user_id],['Package','=',package_id]]],{'fields': ['id','pyment_number','Package_payment_tracker_ids','number_of_payments']} )
       
        if get_subs_payment==[]:
            response = json.dumps({ 'message': 'الطالب غير مشترك بالحزمة'})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        payment_number=int(get_subs_payment[0]['pyment_number'])
        number_of_payments=int(get_subs_payment[0]['number_of_payments'])
        if payment_number+1 > number_of_payments:
            response = json.dumps({ 'message': 'تم تسديد كامل الدفعات مسبقا  '})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
            
        payment_id=int(get_subs_payment[0]['id'])
        user_points=models.execute_kw(self.db, uid, self.password, 'res.users', 'search_read',[[['id' , '=' , user_id]]],{
                                        'fields': ['id','points']})
        user_points=user_points[0]['points']
         
        payment_amount_id=int(get_subs_payment[0]['Package_payment_tracker_ids'][payment_number-1])
        payment_amount=models.execute_kw(self.db, uid, self.password, 'package_payments_tracker', 'search_read',[[['id' , '=' , payment_amount_id]]],{
                                        'fields': ['id','payment_amount']})
        payment_amount=int(payment_amount[0]['payment_amount'])
        if payment_amount>user_points:
            response = json.dumps({ 'message': '   الرصيد غير كافي لدفع الأشتراك'})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        
        try :
            models.execute_kw(self.db, uid, self.password, 'package_subscription_payments', 'write', [[payment_id], {'pyment_number':payment_number+1}])
            response = json.dumps({ 'message': 'تم تسديد الدفعة بنجاح'})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        except:
            response = json.dumps({ 'message': 'تم تسديد كامل الدفعات سابقا'})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        
            
            