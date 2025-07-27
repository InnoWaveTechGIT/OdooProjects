from odoo import http
import logging
import xmlrpc.client as xmlrpclib
import json
from odoo import models, fields, api
import math
import os
import requests
from odoo.http import request ,Response
import jwt
import re
import werkzeug.wrappers
import os
import time
import base64
from os import path
from pathlib import Path
from operator import mul
from datetime import datetime as dt, timedelta
from odoo import http, fields, _
from odoo.exceptions import UserError
from odoo.http import request
from datetime import datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal
import math
from os import environ
from dotenv import load_dotenv

load_dotenv()
_logger = logging.getLogger(__name__)



def false2empty(self,data):
        result = {}
        result1 = []
        for i in data:
            for key, value in i.items():
                if(value is False and key !=  "is_default" and key != 'is_active' and key != 'is_public'  and key != 'is_subscribtion'):
                    value = ''
                result[key] = value
            result1.append(result)
            result = {}

        return result1


class LMSData(http.Controller):
    url = os.getenv('URL')
    db = os.getenv('db')
    username = os.getenv('username')
    password = os.getenv('password')
    


    @http.route('/set_session_watched',  cours='*',auth="public",csrf=False, website=True, methods=['POST'])
    def set_session_watched(self,idd= None, **kw):
        response = ''
        
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        body =json.loads(request.httprequest.data)
        session_id = int(body['session_id'])
        section_id = body['section_id']
        course_id = int(body['course_id'])
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
    
        user_id = int(dec_token['id'])
        # print('dec_token',dec_token)
        try:
            check = models.execute_kw(self.db, uid, self.password, 'session_status', 'search_read', [['&',['user_id','=',user_id],['session_id' , '=' , session_id]]], {'fields': ['is_watched']})
            
         
            if check == []:

                set_the_session_as_watched=models.execute_kw(self.db, uid, self.password, 'session_status', 'create', [{'user_id': user_id,'session_id':session_id,'is_watched':True}])
            elif check[0]['is_watched'] ==False:
                models.execute_kw(self.db, uid, self.password, 'session_status', 'write', [[check[0]['id']], {'is_watched':True}])
        
            else:
                pass
        except Exception as e:
            response = json.dumps({ 'data': [], 'message': 'البيانات المدخلة غير صالحة'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )

        session_watched = models.execute_kw(self.db, uid, self.password, 'session_status', 'search_count', [['&',['user_id','=',user_id],['section_name' , '=' , section_id]]])
        all_session = models.execute_kw(self.db, uid, self.password, 'course.video', 'search_count', [[['section_id' , '=' , section_id]]])

        if all_session == session_watched :
            set_the_section_as_watched=models.execute_kw(self.db, uid, self.password, 'section_status', 'create', [{'user_id': user_id,'section_id':section_id,'is_watched':True}])
            section_watched = models.execute_kw(self.db, uid, self.password, 'section_status', 'search_count', [['&',['user_id','=',user_id],['course_name' , '=' , course_id]]])
            all_section = models.execute_kw(self.db, uid, self.password, 'section', 'search_count', [[['course_id' , '=' , course_id]]])

            if section_watched == all_section:
                set_the_course_as_watched=models.execute_kw(self.db, uid, self.password, 'course_status', 'create', [{'user_id': user_id,'course_id':course_id,'is_watched':True}])
            else :
                pass
        else:
            pass
        
        response = json.dumps({ 'data': [], 'message': 'تمت العملية'})
        return Response(
        response, status=200,
        headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
    )
        # for section in all_session:
        #     if session not in session_watched:
        #         break

    @http.route('/get_course_progress',  cours='*',auth="public",csrf=False, website=True, methods=['GET'])
    def get_course_progress(self,course_id= None, **kw):
        watched =[]
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
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
        user_id = int(dec_token['id'])
        course_id = int(course_id)
        if course_id != None:
            session_watched = models.execute_kw(self.db, uid, self.password, 'session_status', 'search_read', [['&',['user_id','=',user_id],['course_name' , '=' , course_id]]], {'fields': ['session_id']})
            all_session = models.execute_kw(self.db, uid, self.password, 'course.video', 'search', [[['course_id' , '=' , course_id]]])
            for data in session_watched:
                if data['session_id']:
                    watched.append(data['session_id'][0])
                else:
                    pass

            watched = len(watched)
            # print('watched' , watched)
            all_session = len(all_session)
            # print('all_session' , all_session)
            percentage =( watched / all_session) * 100
              
            response = json.dumps({ 'data': {'progress':percentage}, 'message': 'تمت العملية'})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])
        else:
              
            response = json.dumps({ 'data': [], 'message': 'يرجى إدخال معرف الكورس'})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])
    
    
    
        
    @http.route('/cancel_subscription', auth="public",csrf=False, website=True, methods=['POST'])
    def cancel_subscription(self,idd= None, **kw):
        
    
        authe = request.httprequest.headers
        body =json.loads(request.httprequest.data)
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        token = authe['Authorization'].replace('Bearer ', '')
        try:
            dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
        except Exception as e:
                response = json.dumps({ 'jsonrpc': '2.0', 'message': 'Unauthorized!'})
                return Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        user_id = int(dec_token['id'])
        course_id=body['course_id']
        number_of_sessions =models.execute_kw(self.db, uid, self.password, 'course.video', 'search_read', [[['course_id' , '=' , course_id]]], {
                                        'fields': ['id']})
        number_of_watched_session= models.execute_kw(self.db, uid, self.password, 'session_status', 'search_read', [['&',['user_id','=',user_id],['course_name' , '=' , course_id],['is_watched','=',True]]], {'fields': ['session_id']})
        number_of_sessions=len(number_of_sessions)
        number_of_watched_session=len(number_of_watched_session)
        percentage = (number_of_watched_session / number_of_sessions) * 100
        percentage=math.floor(percentage)
        
        if percentage < 5 :
            
            subscribtion_id=models.execute_kw(self.db, uid, self.password, 'subscription', 'search_read', [['&',['user_id' , '=' , user_id],['course_id','=',course_id]]], {
                                        'fields': ['points','id','start_date']})
            
            
            if subscribtion_id!=[]:
                
                current_date = datetime.now().date()
                # print("subscribtion date ")
                # print(subscribtion_id[0]['start_date'])
                start= datetime.strptime(subscribtion_id[0]['start_date'], '%Y-%m-%d').date()

                date_difference = relativedelta(current_date,start)
                days_since_date = date_difference.days
                if days_since_date < 2 : 
                    get_user_points=models.execute_kw(self.db, uid, self.password, 'res.users', 'search_read', [[['id' , '=' , user_id]]], {
                                                'fields': ['points']})
                    recharge_points=models.execute_kw(self.db, uid, self.password, 'res.users', 'write', [[user_id], {'points': get_user_points[0]['points']+subscribtion_id[0]['points']}])
                    models.execute_kw(self.db, uid, self.password, "subscription", 'unlink', [[subscribtion_id[0]['id']]])
                    response = json.dumps({ 'data':[], 'message': ' تم حذف الأشتراك بنجاح  '})
                    return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
                else :
                    
                    response = json.dumps({ 'data':[], 'message': 'لا يمكن الغاء الأشتراك مضى أكثر من يومين '})
                    return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
                    
                    
            else :
                response=json.dumps({'data':[],'message':'  الطالب غير مشترك او تم حذف الأشتراك مسبقا '})
                return Response(
                response, status=402,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )

                
        else :
            response=json.dumps({'data':[],'message':'لا يمكن الغاء الأشتراك  '})
            return Response(
            response, status=403,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )

        