from odoo import http
import logging
from datetime import datetime
import xmlrpc.client as xmlrpclib
import json
from odoo import models, fields, api
import os
import jwt
import requests
from odoo.http import request ,Response
from os import path
from pathlib import Path 
import pathlib
import base64
import time
from PIL import Image
from . import verfiy_token
from os import environ
from dotenv import load_dotenv
_logger = logging.getLogger(__name__)

load_dotenv()
from pathlib import Path
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

def _abs_rout(self,data):
        path1=''
        abs = os.path.dirname(os.path.abspath(__file__))
        abs_sp =abs.split("/")
        
        for i in abs_sp:
            if i != 'controller':
                path1 += i +'/'

        return path1


class Rate(http.Controller):
    url = os.getenv('URL')
    db = os.getenv('db')
    username = os.getenv('username')
    password = os.getenv('password')

    @http.route('/set_session_progress', auth="public", csrf=False, website=True, methods=['POST'])
    def set_session_progress(self, **kw):
        header = request.httprequest.headers
        token = header['Authorization'].replace('Bearer ', '')
        body = json.loads(request.httprequest.data)
        session_id = int(body['session_id'])
        progress = float(body['progress'])

        try:
            dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
        except Exception as e:
            response = json.dumps({ 'jsonrpc': '2.0', 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
     
        user_id = dec_token['id']
        if verfiy_token.verfiy_token(self,token,str(user_id)) == False:
            
            response = json.dumps({ 'data': [], 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        if not user_id or not session_id:
            response = json.dumps({ 'data': [], 'message': ''})
            return Response(response, status=400,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        if progress > 0.0:
            try:
                session_status_id = request.env['session_status'].sudo().search([('user_id', '=', user_id),
                                                                                  ('session_id', '=', session_id)], limit=1)
                if session_status_id:
                    if session_status_id.is_watched:
                        session_status_id.sudo().write({'progress': 1.0})
                        response=json.dumps({"data":[],'message' : 'already watched'})
                        return Response(response, status=200,
                            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
                        )
                    
                    if progress > session_status_id.progress and 0.0 < (progress - session_status_id.progress) <= 0.2:
                        session_status_id.sudo().write({'progress': progress})
                        response=json.dumps({"data":[],'message' : 'progress has been changed'})
                        return Response(response, status=200,
                            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
                        )
                        
                    else:
                        response=json.dumps({"data":[],'message' : 'no progress has been updated'})
                        return Response(response, status=200,
                            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
                        )
                        
                else:
                    request.env['session_status'].sudo().create(
                        {
                            'user_id': user_id,
                            'session_id': session_id,
                            'progress': 0.1
                        })

            except Exception as e:
                    response = json.dumps({ 'data': [], 'message': str(e)})
                    return Response(response, status=500,
                        headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
        else:
            response = json.dumps({ 'data': [], 'message': 'no progress'})
            return Response(response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
    
    @http.route('/add_course_rate',  auth="public",csrf=False, website=True, methods=['POST'])
    def add_course_rate(self, **kw):
        authe = request.httprequest.headers
        
        token = authe['Authorization'].replace('Bearer ', '')
        body =json.loads(request.httprequest.data)
        course_id = int(body['course_id'])
        rating = float(body['rating'])
        comment = body['comment']
        sum=rating
        if rating >5:
            response = json.dumps({ 'data': [], 'message': 'يرجى ادخال قيمة بين ال0 و ال5!'})
            return Response(
            response, status=400,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        try:
            dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
        except Exception as e:
            response = json.dumps({ 'jsonrpc': '2.0', 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
     
        user_id = dec_token['id']
        if verfiy_token.verfiy_token (self,token,str(user_id)) ==False:
            
            response = json.dumps({ 'data': [], 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        
       
        
        
            
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        can_rate=True
        uid = common.authenticate(self.db,self.username, self.password, {})
        user_rates=models.execute_kw(self.db, uid, self.password, 'rate', 'search_read', [[['course_id' , '=' , course_id]]], {
                                        'fields': ['id','rate_value']})
        
        check_blocked_student=models.execute_kw(self.db,uid,self.password,'block.student','search_read', [['&',['user_id' , '=' , user_id],['block','=',True]]], {
                                        'fields': [ 'id']})
        if check_blocked_student!=[]:
            response=json.dumps({"messsage":" الطالب محظور من التقييم يرجى مراسلة الدعم "})
            return Response(
                    
                    response, status=460,
                    headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
                )
        if user_rates!=[]:
            for i in user_rates[0]['rate_value']:
                rate_value_info=models.execute_kw(self.db, uid, self.password, 'rate.value', 'search_read', [[['id' , '=' , i]]], {
                                            'fields': ['id','user_id']})
                
                if rate_value_info[0]['user_id'][0]==user_id:
                    can_rate=False
        if can_rate:
            try:
                uid = common.authenticate(self.db,self.username, self.password, {})
                rate_data = models.execute_kw(self.db, uid, self.password, 'rate', 'search_read', [[['id' , '!=' , False]]], {
                                            'fields': ['course_id' , 'rate_value']})

                course_data = models.execute_kw(self.db, uid, self.password, 'courses', 'search_read', [[['id' , '=' , int(course_id)]]], {
                                            'fields': ['number_of_rater']})
                new_number_of_rater = int(course_data[0]['number_of_rater']) +1
            
                
                x = 0 
                if rate_data == []:
                    rate_id = models.execute_kw(self.db, uid, self.password, 'rate', 'create', [{'course_id': course_id,}])
                    rate_value = models.execute_kw(self.db, uid, self.password, 'rate.value', 'create', [{'rataing': rating,'user_id': user_id ,'rate_id' :rate_id , 'comment': comment}])
                    write_rate = models.execute_kw(self.db, uid, self.password, 'courses', 'write', [[course_id], {'rate': rating ,'number_of_rater':new_number_of_rater}])
                    response=json.dumps({"data":[],'message' : 'تم رفع التقييم'})
                    return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
                )
                
                for i in rate_data :
                    if i['course_id'][0] == course_id:
                        rate_id =i['id']
                
                        rate_count= len(i['rate_value'])
                        rate_count = rate_count +1
                        x = models.execute_kw(self.db, uid, self.password, 'rate.value', 'create', [{'rataing': rating ,'user_id': user_id ,'rate_id':rate_id , 'comment': comment}])
                        rate_data = models.execute_kw(self.db, uid, self.password, 'rate', 'search_read', [[['id' , '!=' , False]]], {
                                            'fields': ['course_id' , 'rate_value']})
                        
                        for j in i['rate_value']:
                            rate_in_db = models.execute_kw(self.db, uid, self.password, 'rate.value', 'search_read', [[['id' , '=' , j]]], {
                                            'fields': [ 'rataing']})

                        
                            sum +=  rate_in_db[0]['rataing']
                    
                        rate_dd = sum/rate_count
                        write_rate = models.execute_kw(self.db, uid, self.password, 'courses', 'write', [[course_id], {'rate': rate_dd,'number_of_rater':new_number_of_rater}])
                        response=json.dumps({"data":[],'message' : 'تم رفع التقييم'})
                        return Response(
                        response, status=200,
                        headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
                    )
                    else:
                        pass
                rate_id = models.execute_kw(self.db, uid, self.password, 'rate', 'create', [{'course_id': course_id,}])
                rate_value = models.execute_kw(self.db, uid, self.password, 'rate.value', 'create', [{'rataing': rating,'user_id': user_id ,'rate_id' :rate_id , 'comment': comment}])
        

                write_rate = models.execute_kw(self.db, uid, self.password, 'courses', 'write', [[course_id], {'rate': rating,'number_of_rater':new_number_of_rater}])
                response=json.dumps({"data":[],'message' : 'تم رفع التقييم'})
                return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
            )
            
            
            except Exception as e:
                
                response = json.dumps({ 'jsonrpc': '2.0', 'message': 'Unauthorized!',})
                return Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                 )
        else :
            
            response = json.dumps({'message': 'قمت بتقيم هذه الدورة سابقا ',})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                 )
            
    @http.route('/add_teacher_rate',  auth="public",csrf=False, website=True, methods=['POST'])
    def add_teacher_rate(self, **kw):
        authe = request.httprequest.headers
        sum = 0
        token = authe['Authorization'].replace('Bearer ', '')
        body =json.loads(request.httprequest.data)
        teacher_id = int(body['teacher_id'])
        rating = float(body['rating'])
        sum = rating
        comment = body['comment']
        if rating >5:
            response = json.dumps({ 'data': [], 'message': 'يرجى ادخال قيمة بين ال0 و ال5!'})
            return Response(
            response, status=400,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        
        try:
            dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
        except Exception as e:
            response = json.dumps({ 'jsonrpc': '2.0', 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        
        
        user_id = dec_token['id']
        if verfiy_token.verfiy_token (self,token,str(user_id)) ==False:
            
            response = json.dumps({ 'data': [], 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        
            
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        can_rate=True
        uid = common.authenticate(self.db,self.username, self.password, {})
        user_rates=models.execute_kw(self.db, uid, self.password, 'teacher_rate', 'search_read', [[['teacher_id' , '=' , teacher_id]]], {
                                        'fields': ['id','rate_value']})
        
        check_blocked_student=models.execute_kw(self.db,uid,self.password,'block.student','search_read', [['&',['user_id' , '=' , user_id],['block','=',True]]], {
                                        'fields': [ 'id']})
        if check_blocked_student!=[]:
            response=json.dumps({"messsage":" الطالب محظور من التقييم يرجى مراسلة الدعم "})
            return Response(
                    
                    response, status=460,
                    headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
                )
        if user_rates!=[]:
            for i in user_rates[0]['rate_value']:
                rate_value_info=models.execute_kw(self.db, uid, self.password, 'teacher.value', 'search_read', [[['id' , '=' , i]]], {
                                            'fields': ['id','user_id']})
                
                if rate_value_info[0]['user_id'][0]==user_id:
                    can_rate=False
        if can_rate:
            try:
                uid = common.authenticate(self.db,self.username, self.password, {})
                teacher_data = models.execute_kw(self.db, uid, self.password, 'teacher', 'search_read', [[['id' , '=' , teacher_id]]], {
                                            'fields': [ 'number_of_rater']})
                new_number_of_rater = int(teacher_data[0]['number_of_rater'])+1
                rate_data = models.execute_kw(self.db, uid, self.password, 'teacher_rate', 'search_read', [[['id' , '!=' , False]]], {
                                            'fields': ['teacher_id' , 'rate_value']})
                
                
                x = 0 
                if rate_data == []:
                    
                    rate_id = models.execute_kw(self.db, uid, self.password, 'teacher_rate', 'create', [{'teacher_id' :teacher_id}])
                

                    rate_value = models.execute_kw(self.db, uid, self.password, 'teacher.value', 'create', [{'rataing': rating,'user_id': user_id ,'rate_id' :rate_id , 'comment': comment}])
                    write_rate = models.execute_kw(self.db, uid, self.password, 'teacher', 'write', [[teacher_id], {'rate': rating , 'number_of_rater':new_number_of_rater}])
                    response=json.dumps({"data":[],'message' : 'تم رفع التقييم'})
                    return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
                    )


                for i in rate_data :
                    
                    
                    
                    
                    if i['teacher_id'][0] == teacher_id:
                        rate_id =i['id']
                        
                        
                        rate_value = models.execute_kw(self.db, uid, self.password, 'teacher.value', 'create', [{'rataing': rating ,'user_id': user_id ,'rate_id':rate_id , 'comment': comment}])
                        rate_count= len(i['rate_value'])
                        rate_count = rate_count +1
                        
                        
                        
                        
                        for j in i['rate_value']:
                            rate_in_db = models.execute_kw(self.db, uid, self.password, 'teacher.value', 'search_read', [[['id' , '=' , j]]], {
                                            'fields': [ 'rataing']})
                            sum +=  rate_in_db[0]['rataing']
                            
                        rate_dd = sum/rate_count
                        write_rate = models.execute_kw(self.db, uid, self.password, 'teacher', 'write', [[teacher_id], {'rate': rate_dd ,'number_of_rater':new_number_of_rater}])
                        response=json.dumps({"data":[],'message' : 'تم رفع التقييم'})
                        return Response(
                        response, status=200,
                        headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
                    )
                    else:
                        pass
                    
                
                
                
                rate_id = models.execute_kw(self.db, uid, self.password, 'teacher_rate', 'create', [{'teacher_id' :teacher_id }])
                rate_value = models.execute_kw(self.db, uid, self.password, 'teacher.value', 'create', [{'rataing': rating,'user_id': user_id ,'rate_id' :rate_id , 'comment': comment}])
                write_rate = models.execute_kw(self.db, uid, self.password, 'teacher', 'write', [[teacher_id], {'rate': rating ,'number_of_rater':new_number_of_rater}])
                
                
                response=json.dumps({"data":[],'message' : 'تم رفع التقييم'})
                return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
            )
            
            
            except Exception as e:
                response = json.dumps({ 'jsonrpc': '2.0', 'message': 'Unauthorized!'})
                return Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
        else :
            response = json.dumps({'message': 'قمت بتقييم المدرس سابقا '})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
            

    @http.route('/add_student_comment',  auth="public",csrf=False, website=True, methods=['POST'])
    def add_student_comment(self, **kw):
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        authe = request.httprequest.headers
        body = {}
        session_id = 0
        try:
            body = json.loads(request.httprequest.data)
        except Exception as e:
            pass  
        comment1 = ''
        comment = ''
        try:
            token = authe['Authorization'].replace('Bearer ', '')
            dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
        except Exception as e:
            response = json.dumps({ 'jsonrpc': '2.0', 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        
        
        user_id = dec_token['id']
        if verfiy_token.verfiy_token (self,token,str(user_id)) ==False:
            
            response = json.dumps({ 'data': [], 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        
        # course_id=int(body['course_id'])
        uid = common.authenticate(self.db,self.username, self.password, {})
        images=request.httprequest.files.getlist('images[]')
        comment_images=[]
        session_id1 = 0
        if body:
            if 'comment' in body:
                comment1 =body['comment']
            if 'session' in body:
            
        
                session_id1=int (body['session'])
            if 'session_id' in body:
            
        
                session_id1=int (body['session_id'])
        if 'comment'in kw:
            
        
            comment=kw['comment']
        if comment :
            pass
        elif comment1 :
            comment = comment1
        else :
            response = json.dumps({"message":"يرجى ادخال السؤال"})
            return Response(
                    
                    response, status=200,
                    headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
                )
        if 'session' in kw:
            
        
            session_id=int (kw['session'])
       
        elif session_id1:
            session_id = session_id1
        
        else :
            response = json.dumps({"message":"يرجى ادخال معرف الجلسة "})
            return Response(
                   
                    response, status=200,
                    headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
                )
            
        
        
        print(1)
        session_course_id= models.execute_kw(self.db, uid, self.password, 'course.video', 'search_read', [[['id' , '=' , session_id]]], {
                                        'fields': [ 'course_id','is_public']})
        print(2)
        # print("session_course_id")
        # print(session_course_id)
        if session_course_id==[]:
            response=json.dumps({"messsage":" الجلسة غير صحيحة"})
            return Response(
                    
                    response, status=404,
                    headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
                )
        check_blocked_student=models.execute_kw(self.db,uid,self.password,'block.student','search_read', [['&',['user_id' , '=' , user_id],['block','=',True]]], {
                                        'fields': [ 'id']})
       
        
        if check_blocked_student!=[]:
            response=json.dumps({"messsage":" الطالب محظور من السؤال يرجى مراسلة الدعم "})
            return Response(
                    
                    response, status=460,
                    headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
                )
            
            
        course_id = session_course_id[0]['course_id'][0]
        subscription_ids = models.execute_kw(self.db, uid, self.password, 'subscription', 'search_read', [['&',['course_id' , '=' ,course_id],['user_id' , '=' , user_id]]],{'fields':['id']})
        if session_course_id[0]['is_public']==False:
            if subscription_ids == []:
                
                response=json.dumps({"messsage":"الطالب غير مشترك بالكورس"})
                return Response(
                        
                        response, status=200,
                        headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
                    )
        # check number of questions for this user on this session 
        noq = http.request.env['enquiries'].search_count([('enquiry_id' , '=' ,session_id),('user_id' , '=' , user_id)])
    
        # noq=models.execute_kw(self.db, uid, self.password, 'enquiries', 'search_read', [['&',['enquiry_id' , '=' ,session_id],['user_id' , '=' , user_id]]])
        if noq>=10 :
            response=json.dumps({"messsage":"تجاوز الرقم المسموح لعدد الأسئلة"})
            return Response(
                    
                    response, status=200,
                    headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
                )
            
        # new_comment = models.execute_kw(self.db, uid, self.password, 'enquiries', 'create', [{}])
        new_comment = http.request.env['enquiries'].with_user(uid).create({
                'user_id': user_id, 'comment' : comment, 'enquiry_id' :session_id ,'course_id':course_id 
            })
        size = 0.0
        if images:
            for image in images:
                blob = image.read()
                size += len(blob) 
        
        
                if size >  5300000:
                    response = json.dumps({ 'data': [], 'message':'حجم الصور كبير'})
                    return Response(
                    response, status=400,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
                comment_image= base64.encodebytes(blob)
                comment_images.append({
                    'image' : comment_image,
                    'comment_id':new_comment.id
                })
        if comment_images:
            for i in comment_images:
                new_comment_images = http.request.env['comment.images'].with_user(uid).create(i)
        if new_comment:
            response = json.dumps({"data":{'id':new_comment.id},"message":"تم إضافة السؤال بنجاح"})
            return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
                )


    @http.route('/reply_comment',  auth="public",csrf=False, website=True, methods=['POST'])
    def reply_comment(self, **kw):
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        authe = request.httprequest.headers
        
        
        body =json.loads(request.httprequest.data)
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
        if verfiy_token.verfiy_token (self,token,str(user_id)) ==False:
            
            response = json.dumps({ 'data': [], 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        
        
        # course_id=int(body['course_id'])
        uid = common.authenticate(self.db,self.username, self.password, {})
        user_info = models.execute_kw(self.db, uid, self.password, 'res.users', 'search_read', [[['id' , '=' , user_id]]], {
                                        'fields': ['user_type']})
        can_reply=False
        
        if user_info[0]['user_type']!='student' :
            
            can_reply=True
       
         
        if 'comment'in body:
            
        
            comment=body['comment']
        else :
            response = json.dumps({"message":"حقل التعليق مطلوب"})
            return Response(
                    
                    response, status=200,
                    headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
                )
        if 'comment_id' in body:
            
        
            comment_id=int (body['comment_id'])
        else :
            response = json.dumps({"message":"حقل  معرف التعليق مطلوب"})
            return Response(
                   
                    response, status=200,
                    headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
                )
            
        
        
        comment_user_id= models.execute_kw(self.db, uid, self.password, 'enquiries', 'search_read', [[['id' , '=' , comment_id]]], {
                                        'fields': ['user_id']})
        if comment_user_id==[]:
             response = json.dumps({"message":"التعليق غير موجود"})
             return Response(
                   
                    response, status=200,
                    headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
                )
            
            
        
        
        if user_id==comment_user_id[0]['user_id'][0]:
            
            can_reply=True


            
        
        if can_reply:
            new_reply = models.execute_kw(self.db, uid, self.password, 'replay_enquiry', 'create', [{'user_id': user_id, 'comment' : comment, 'replay_id':comment_id,}])
            response = json.dumps({'data':{'id':new_reply},"message":"تم أضافة الرد بنجاح"})
            return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
                )
        else :
             response = json.dumps({"message":"لا يمكن للمستخدم الرد على هذا التعليق"})
             return Response(
                 response,
                     status=200,
                    headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
                )
    @http.route('/get_payments_method',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_payments_method(self, **kw):
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        payments=models.execute_kw(self.db, uid, self.password, 'payment.type', 'search_read', [[['id','!=',False]]], {
                                        'fields': ['name','image_path','phone_number','receiver_name']})
        payments=false2empty(self,payments)
        
        if payments!=[]:
             response = json.dumps({'data':{'payments':payments},"message":"طرق الدفع"})
             return Response(
                 response,
                     status=200,
                    headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
                ) 
       
        else :
            response = json.dumps({"message":" لا يوجد طرق دفع " })
            return Response(
                 response,
                     status=404,
                    headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
                ) 
    @http.route('/get_points',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_points(self, **kw):
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        points=models.execute_kw(self.db, uid, self.password, 'points', 'search_read', [[['id','!=',False]]], {
                                        'fields': ['number_of_points','price']})
        
        points = sorted(points, key=lambda x: x['number_of_points'], reverse=True)
        
        if points!=[]:
             response = json.dumps({'data':{'points':points},"message":" النقاط"})
             return Response(
                 response,
                     status=200,
                    headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
                ) 
       
        else :
            response = json.dumps({"message":" لا يوجد  نقاط " })
            return Response(
                 response,
                     status=404,
                    headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
                ) 
    

    @http.route('/set_expected_degree',  auth="public",csrf=False, website=True, methods=['POST'])
    def set_expected_degree(self ,**kw):
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

        try:
            expected_degree = int(kw['expected_degree'])
            section_id = int(kw['section_id'])
        except Exception as e:
            response = json.dumps({ 'data': [], 'message': 'required field was not sent!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )


        user_id = int(dec_token['id'])
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        uid = common.authenticate(self.db, self.username, self.password, {})
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        check_answred_before=models.execute_kw(self.db, uid, self.password, 'section_quize_result', 'search_read',[['&',['section_id','=',section_id],['user_id', '=', user_id]]], {'fields':  ['id','section_id','the_expected_degree']})
        if check_answred_before!=[]:
            if check_answred_before[0]['the_expected_degree'] != 0 :
     
            
                response = json.dumps({ 'data': [], 'message': 'تم رفع العلامة المتوقعة على هذا الأختبار سابقا '})
                return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
            else:
                section_quiz_result = http.request.env['section_quize_result'].sudo().search([('id' , '=' , int(check_answred_before[0]['id']))])
                section_quiz_result.the_expected_degree = int(expected_degree)
                response = json.dumps({ 'data': [], 'message': 'تم رفع العلامة المتوقعة على هذا الأختبار '})
                return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )

        else:
            response = json.dumps({ 'data': [], 'message': 'لم يتم رفع العلامة المتوقعة على هذا الأختبار يرجى رفع الاختبار أولا '})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
            




    @http.route('/submit_section_quiz',  auth="public",csrf=False, website=True, methods=['POST'])
    def submit_section_quiz(self ,section_id,**kw):
        size=0
        loctions=[]
        body=request.httprequest.files.getlist('section_image[]')
        section_id=int(section_id)
        data = os.path.dirname(os.path.abspath(__file__))
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
        id = dec_token['id']
        if verfiy_token.verfiy_token (self,token,str(id)) ==False:
            response = json.dumps({ 'data': [], 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        login=dec_token['login']
        fields={}
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        uid = common.authenticate(self.db, self.username, self.password, {})
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        user = models.execute_kw(self.db, uid, self.password, 'res.users', 'search_read',[[['id', '=', id]]], {'fields':  ['name','image_path',]})
        check_answred_before=models.execute_kw(self.db, uid, self.password, 'section_quize_result', 'search_read',[['&',['section_id','=',section_id],['user_id', '=', id]]], {'fields':  ['id','section_id']})
       
        if check_answred_before!=[]:
            
     
            
            response = json.dumps({ 'data': [], 'message': 'تمت الأجابة مسبقا على هذا الأختبار '})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
            
                
        
        if(body != None ):
            for image in body:
                blob = image.read()
                size += len(blob) 
                image_file_name=image.filename
            
                image_type = image.filename.split(".") 
                types =['jpeg','JPEG','png','PNG','jpg','JPG']
                if image_type[-1] == 'pdf' or image_type[-1] =='PDF':
                    image_file_name=image.filename
                    time_stamp = str(time.time())
                    fields['image_file_name']=image_file_name.replace(" ", "")

            
                    # module_path = "/home/vps112/odoo_16/torbetodoo/torbet_app/static/" #servar

                    module_path = _abs_rout(self ,data)+"static/test"#loc
                    isExist = os.path.exists(module_path)

                    if isExist == False:
                        os.mkdir(module_path)
                    # blob = image.read()
                    section_image= base64.encodebytes(blob)
                    with open(os.path.join(module_path, time_stamp + fields['image_file_name']), "wb+") as f:
                        f.write(base64.b64decode(section_image))
                        fields["image_full_url"] = module_path + '/' + \
                        time_stamp+image_file_name.replace(" ", "")
                    write = models.execute_kw(self.db, uid, self.password, 'section_quize_result', 'create', [{'user_id':id,'pdf_file': section_image ,'file_name':image_file_name,'section_id':section_id,'file_type':'pdf'}])
                    response = json.dumps({ 'data':[],'message': 'تم رفع الحل ' })
                    return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
                if image_type[-1] not in types :
                
                    response = json.dumps({ 'data': [], 'message':'يرجى رفع صورة من نمط jpeg  png  jpg  '})
                    return Response(
                    response, status=400,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
               
                if size > 71922050:
                    response = json.dumps({ 'data': [], 'message':'حجم الصورة كبير'})
                    return Response(
                    response, status=400,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
                image_file_name=image.filename
                time_stamp = str(time.time())
                fields['image_file_name']=image_file_name.replace(" ", "")

        
                # module_path = "/home/vps112/odoo_16/torbetodoo/torbet_app/static/" #servar

                module_path = _abs_rout(self ,data)+"static/test"#loc
                isExist = os.path.exists(module_path)

                if isExist == False:
                    os.mkdir(module_path)
                # blob = image.read()
                section_image= base64.encodebytes(blob)
                

                
                with open(os.path.join(module_path, time_stamp + fields['image_file_name']), "wb+") as f:
                    f.write(base64.b64decode(section_image))
                fields["image_full_url"] = module_path + '/' + \
                time_stamp+image_file_name.replace(" ", "")
                
                loctions.append(fields["image_full_url"])


            # 
                
            
        
        else:
            
            fields['image_file_name']=""
            fields["section_image"]=""
            return True
        if loctions != [] : 
            image_2_pdf=[]
            image_1 = Image.open(loctions[0])
            new_image = image_1.resize((1000, 1500))
            im_1 = new_image.convert('RGB')
            counter = 0 
            for location in loctions:
                image_2 = Image.open(location)
                new_image = image_2.resize((1000, 1500))
                im_2 = new_image.convert('RGB')
                if counter != 0:
                    image_2_pdf.append(im_2)
                counter +=1
            
            
            
            module_path1='/home/ubuntu/taleb_odoo16/talebodoo/taleb/static/section_quize_resalt'
            
            isExist = os.path.exists(module_path1)

            if isExist == False:
                os.mkdir(module_path1)
                # blob = image.read()
                # section_image= base64.encodebytes(blob)
            x=im_1.save(r'/home/ubuntu/taleb_odoo16/talebodoo/taleb/static/section_quize_resalt/'+time_stamp+'sd.pdf', save_all=True, append_images=image_2_pdf)
            file = open('/home/ubuntu/taleb_odoo16/talebodoo/taleb/static/section_quize_resalt/'+time_stamp+'sd.pdf', "rb")
            out = file.read()

            file.close()

            gentextfile = base64.b64encode(out)
            file_name = time_stamp+'sd.pdf'
        write = models.execute_kw(self.db, uid, self.password, 'section_quize_result', 'create', [{'user_id':id,'pdf_file': gentextfile ,'file_name':file_name,'section_id':section_id,'file_type':'pdf'}])
        section_quize=models.execute_kw(self.db, uid, self.password, 'section_quize', 'search_read', [[['section_id' , '=' , section_id]]], {
                                        'fields': ['id','correction_file_path','section_id']})
        if section_quize==[]:
            
            response = json.dumps({ 'data': [], 'message':'حدث خطأ'})
            return Response(
                    response, status=400,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
                
        for image_location in loctions:
                if os.path.exists(image_location):
                    os.unlink(image_location)
        response = json.dumps({ 'data':[{'correction_file_path':section_quize[0]['correction_file_path']}],'message': 'تم رفع الحل ' })
        return Response(
        response, status=200,
        headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
    

    @http.route('/add_report',  auth="public",csrf=False, website=True, methods=['POST'])
    def add_report(self, **kw):
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        authe = request.httprequest.headers
        
        
        body =json.loads(request.httprequest.data)
        try:
            token = authe['Authorization'].replace('Bearer ', '')
            dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
        except Exception as e:
            response = json.dumps({ 'data': [], 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        
        
        user_id = dec_token['id']
        if verfiy_token.verfiy_token (self,token,str(user_id)) ==False:
            
            response = json.dumps({ 'data': [], 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        
        
        
        uid = common.authenticate(self.db,self.username, self.password, {})
        
        if "comment_id" in body:
            
            comment_id = int(body['comment_id'])
        else :
            response = json.dumps({ 'data': [], 'message': 'comment_id feild required!'})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        if "comment" in body :
        
            comment = body['comment']
        else :
             response = json.dumps({ 'data': [], 'message': 'comment feild required!'})
             return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
            
        # enquiries
        try:
            denouncement=models.execute_kw(self.db, uid, self.password, 'denouncement', 'search_read', [[['related_comment' , '=' , comment_id]]], {
                                        'fields': ['id','denouncement_ids']})
            
           
            if denouncement!=[]:
                new_report=models.execute_kw(self.db, uid, self.password, 'denouncement_details', 'create', [{'user_id': user_id ,'comment':comment,'denouncement_id':denouncement[0]['id']}])
                if new_report:
                    response = json.dumps({'data':[],"message":" تم رفع الإبلاغ"})
                    return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
                else :
                    response = json.dumps({'data':[],"message":" حدث خطأ عند أضافة التبليغ"})
                    return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
                    
            else :
                try:
                    new_denouncement=models.execute_kw(self.db, uid, self.password, 'denouncement', 'create', [{'related_comment': comment_id }])
                    new_report=models.execute_kw(self.db, uid, self.password, 'denouncement_details', 'create', [{'user_id': user_id ,'comment':comment,'denouncement_id':new_denouncement}])
                    response = json.dumps({'data':[],"message":"   تم رفع الابلاغ  "})
                    return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
                except:
                    response = json.dumps({'data':[],"message":"    معرف التعليق غير موجود   "})
                    return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
                    
        except:
            response = json.dumps({'data':[],"message":" حدث خطأ"})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
    @http.route('/delete_comment',  auth="public",csrf=False, website=True, methods=['DELETE'])
    def delete_comment(self, id,**kw):
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        authe = request.httprequest.headers
        try:
            
            token = authe['Authorization'].replace('Bearer ', '')
            dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
        except Exception as e:
            response = json.dumps({ 'data': [], 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        user_id=dec_token['id']
        student_comment=models.execute_kw(self.db,uid,self.password,'enquiries','search_read', [['&',['id' , '=' , id],['pending','=',True]]], {'fields': ['pending','user_id','comment','enquiry_id','replay_enquiry_ids','image_path','create_date']})
        if student_comment==[]:
            response = json.dumps({ 'data': [], 'message': 'التعليق غير موجود أو تم الرد عليه '})
            return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
        # print("student comment ")
        # print(student_comment)
        if student_comment[0]['user_id'][0]==user_id:
            try:
                models.execute_kw(self.db, uid, self.password, "enquiries", 'unlink', [[id]])
            except :
                 response = json.dumps({ 'data': [], 'message': 'حدث خطأ'})
                 return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
            response = json.dumps({ 'data': [], 'message': 'تم حذف السؤال بنجاح '})
            return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
        else :
            response = json.dumps({ 'data': [], 'message': ' ليس لديك صلاحيات لحذف هذا السؤال '})
            return Response(
                    response, status=403,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
                    
    @http.route('/edit_comment',  auth="public",csrf=False, website=True, methods=['POST'])
    def edit_comment(self,**kw):
        size=0.0
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        authe = request.httprequest.headers
        comment_images=[]
        try:
            
            token = authe['Authorization'].replace('Bearer ', '')
            dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
        except Exception as e:
            response = json.dumps({ 'data': [], 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        # body =json.loads(request.httprequest.data)
        images=request.httprequest.files.getlist('images[]')
        user_id=dec_token['id']
        id=int(kw['comment_id'])
        student_comment=models.execute_kw(self.db,uid,self.password,'enquiries','search_read', [['&',['id' , '=' , id],['pending','=',True]]], {'fields': ['pending','user_id','comment','enquiry_id','replay_enquiry_ids','image_path','create_date','image_ids']})
        if student_comment==[]:
            response = json.dumps({ 'data': [], 'message': 'التعليق غير موجود أو تم الرد عليه '})
            return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
        
        if student_comment[0]['user_id'][0]==user_id:
            # try:
                
            comment=kw['comment']

            models.execute_kw(self.db, uid, self.password, 'enquiries', 'write', [[id], {'comment':comment}])
            
            image_2_delete = models.execute_kw(self.db, uid, self.password, 'comment.images', 'search', [[['comment_id', '=', id]]])
            for image in image_2_delete:
                models.execute_kw(self.db, uid, self.password, "comment.images", 'unlink', [[image]])
            if images and images != []:
                student_comment[0]['image_ids'] = []
                for image in images:
                    blob = image.read()
                    size += len(blob) 
            
            
                    if size >  5300000:
                        response = json.dumps({ 'data': [], 'message':'حجم الصور كبير'})
                        return Response(
                        response, status=400,
                        headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
                    comment_image= base64.encodebytes(blob)
                    comment_images.append({
                        'image' : comment_image,
                        'comment_id':id
                    })
            if comment_images:
                for i in comment_images:
                    
                    new_comment_images = models.execute_kw(self.db, uid, self.password, 'comment.images', 'create', [i])

            response = json.dumps({ 'data': [], 'message': 'تم تعديل التعليق بنجاح'})
            return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
        else :
            response = json.dumps({ 'data': [], 'message': ' ليس لديك صلاحيات لتعديل هذا السؤال '})
            return Response(
                    response, status=403,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
    
    
                    )
    @http.route('/rate_video',  auth="public",csrf=False, website=True, methods=['POST'])
    def rate_video(self, **kw):
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        authe = request.httprequest.headers
        
        
        
        try:
            token = authe['Authorization'].replace('Bearer ', '')
            dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
        except Exception as e:
            response = json.dumps({ 'jsonrpc': '2.0', 'message': str(e)})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        
        body =json.loads(request.httprequest.data)
        user_id = int(dec_token['id'])
        comment=body['comment']
        rating = float(body['rating'])
        if rating >5:
            response = json.dumps({ 'data': [], 'message': 'يرجى ادخال قيمة بين ال0 و ال5!'})
            return Response(
            response, status=400,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        session_id=int(body['session_id'])
        if verfiy_token.verfiy_token (self,token,str(user_id)) ==False:
            
            response = json.dumps({ 'data': [], 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        
        can_rate=True
        user_rates=models.execute_kw(self.db, uid, self.password, 'video.rate', 'search_read', [[['video' , '=' , session_id]]], {
                                        'fields': ['id','video_rate_value']})
        if user_rates!=[]:
            for i in user_rates[0]['video_rate_value']:
                rate_value_info=models.execute_kw(self.db, uid, self.password, 'video_rate.value', 'search_read', [[['id' , '=' , i]]], {
                                            'fields': ['id','user_id']})
                
                if rate_value_info[0]['user_id'][0]==user_id:
                    can_rate=False
        if can_rate :
            try:
                get_session_rate_rec=models.execute_kw(self.db, uid, self.password, 'video.rate', 'search_read', [[['video','=',session_id]]], {
                                        'fields': ['id','video']})
                if get_session_rate_rec!=[]:
                    
                    rate_id=int(get_session_rate_rec[0]['id'])
                  
                    #rate_id    comment    user_id     rataing
                    models.execute_kw(self.db, uid, self.password, 'video_rate.value', 'create', [{'comment': comment,'rate_id':rate_id,'user_id':user_id,'rataing':rating}])
                else :
                    # print("else")
                    new_rec=models.execute_kw(self.db, uid, self.password, 'video.rate', 'create', [{'video':session_id}])
                    models.execute_kw(self.db, uid, self.password, 'video_rate.value', 'create', [{'comment': comment,'rate_id':int(new_rec),'user_id':user_id,'rataing':rating}])
                    
                
                
            except :
                
                response = json.dumps({ 'data': [], 'message': 'رقم الجلسة غير موجود'})
                return Response(
                response, status=404,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )   
            
            response = json.dumps({ 'data': [], 'message': 'تم رفع التقييم بنجاح'})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        else :
            response = json.dumps({ 'data': [], 'message': 'يوجد تقييم سابق للجلسة'})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )

               
                
        