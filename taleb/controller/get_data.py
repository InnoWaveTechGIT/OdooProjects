from odoo import http
# from werkzeug.wrappers import Response
import asyncio
import logging
# from datetime import datetime
import xmlrpc.client as xmlrpclib
import random
import json
import math
from odoo.http import request ,Response
# from odoo.http import JsonRequest
import jwt
import requests
from bs4 import BeautifulSoup
from datetime import datetime as dt, timedelta
from odoo import http
from datetime import datetime, date
from odoo import http
from dateutil.relativedelta import relativedelta
from . import verfiy_token
from decimal import Decimal
import ast
import os
import time
from os import environ
from dotenv import load_dotenv
load_dotenv()


_logger = logging.getLogger(__name__)
def Char2minutes(self,data):

    #  my_time = '9715:56:46'
    factors = (60, 1, 1/60)

    t1 = sum(i*j for i, j in zip(map(int, data.split(':')), factors))
    t2 = sum(map(mul, map(int, data.split(':')), factors))



    return t1
def munites2string(self,num):
    a = timedelta(seconds=num*60)


    return str(a)
    # datetime.timedelta(0, 65)



def false2empty(self,data):
        result = {}
        result1 = []
        for i in data:
            for key, value in i.items():
                if(value is False and key !=  "is_default" and key != 'is_active' and key !='is_seen' and key != 'is_public' and key != 'is_watched' and key != 'is_subscribtion' and key!='quiz' and key!='is_purchased'  and key!='quiz_subscribtion'):
                    value = ''
                result[key] = value
            result1.append(result)
            result = {}

        return result1

def _subscribtion(self,data):
        for i in data:
            if i['is_subscribtion'] != True and i['is_public'] != True:
                i['embeded_code'] = ''
        return data



def _nocomment(self,data):
        result = []
        for i in range(len(data)):


            if data[i]['comment'] != False:
                result.append(data[i])
            else:
                pass


        return result



class GetData(http.Controller):
    url = os.getenv('URL')
    db = os.getenv('db')
    username = os.getenv('username')
    password = os.getenv('password')
    
    async def execute_kw_and_continue(self , session_id):
        # Your existing code
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        response = models.execute_kw(self.db, uid, self.password, 'course.video', 'write', [[session_id], {'video_file_name': "asdwe"}])
        return response

    def run_code(self,session_id):
        # Create a new event loop
        loop = asyncio.new_event_loop()
        
        # Set the new event loop as the current event loop
        asyncio.set_event_loop(loop)
        
        # Run the function and wait for it to complete
        loop.run_until_complete(self.execute_kw_and_continue(session_id))
        
        # Close the event loop
        loop.close()


    @http.route('/student_class',  auth="public",csrf=False, website=True, methods=['GET'])
    def student_class(self,idd= None, **kw):
        response = ''

        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        std_class = models.execute_kw(self.db, uid, self.password, 'student.class', 'search_read', [[['id' , '!=' , False]]], {'fields': ['name']})
        
        if len(std_class) > 0:
            response = json.dumps({"data":std_class,'message': 'معلومات الأسساتذة '})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )

        else:
            response = json.dumps({"data":[],'message': 'لا يوجد '})
            return Response(
            response, status=404,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
    @http.route('/get_teachers',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_teachers(self,idd= None, **kw):
        response = ''

        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        techer_id = models.execute_kw(self.db, uid, self.password, 'teacher', 'search_read', [[['id' , '!=' , False]]], {'fields': ['courses_ids','number_of_student','number_of_courses','number_of_rater','teacher_name','teacher_image','rate','number_of_rater','specialization','description']})
        
        if len(techer_id) > 0:
            techer_id = false2empty(self ,techer_id)
            response = json.dumps({"data":{'teachers':techer_id},'message': 'معلومات الأسساتذة '})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )

        else:
            response = json.dumps({"data":[],'message': 'لا يوجد أساتذة'})
            return Response(
            response, status=404,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
    @http.route('/get_teacher',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_teacher(self,id= None, **kw):
        response = ''
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        if id == None:
            response = json.dumps({"data":[],'message': 'لا يوجد أستاذ'})
            return Response(
            response, status=404,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )

        else:
            # check empty path for teacher and make it
            teachers=models.execute_kw(self.db, uid, self.password, 'res.users', 'search_read', [[['image_path' , '=',False]]], {'fields': ['user_type','image_path']})
            if teachers!=[]:
                for teacher in teachers:
                    try :
                        if teacher['user_type']=='teacher':
                        
                            models.execute_kw(self.db, uid, self.password, 'res.users', 'write', [[int(teacher['id'])], {'image_path':"/taleb/static/default/teacher.png"}])
                        else :
                            models.execute_kw(self.db, uid, self.password, 'res.users', 'write', [[int(teacher['id'])], {'image_path':"/taleb/static/default/student.png"}])
                            
                    except:
                        pass

            techer_id = models.execute_kw(self.db, uid, self.password, 'teacher', 'search_read', [[['id' , '=' , id]]], {'fields': ['number_of_rater','number_of_courses','number_of_student','teacher_name','teacher_image','rate','number_of_rater','specialization','description']})

            if len(techer_id) > 0:
                techer_id = false2empty(self ,techer_id)
                response = json.dumps({"data":{'teacher':techer_id[0]},'message': 'معلومات الأسستاذ '})
                return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )

            else:
                response = json.dumps({"data":[],'message': 'لا يوجد أستاذ'})
                return Response(
                response, status=404,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )

    
    @http.route('/get_session_by_id',  auth="public",csrf=False, website=True, methods=['GET']) 
    def get_session_by_id(self,id= None, **kw): 
        Comments=[] 
        if id != None: 
            id = int(id) 
        authe = request.httprequest.headers 
        try: 
            token = authe['Authorization'].replace('Bearer ', '') 
            dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"]) 
 
        except Exception as e: 
             
            common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url)) 
            models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url)) 
            uid = common.authenticate(self.db,self.username, self.password, {}) 
            session_details = models.execute_kw(self.db, uid, self.password, 'course.video', 'search_read', [[['id' , '=' , id]]], {'fields': ['Title','script_code','title','is_public','course_id','dacast_id','duration','embeded_code','quiz_ids','course_enquiry_ids','video_file_path','video_size']}) 
 
            if len(session_details) >0 and session_details[0]['is_public'] == True: 
                if session_details[0]['quiz_ids'] != []: 
                    quiz = True 
                else : 
                    quiz = False 
                session_details[0]['course_name']=session_details[0]['course_id'][1] 
                session_details[0]['course_id']=session_details[0]['course_id'][0] 
 
                try : 
                    del session_details[0]['course_enquiry_ids'] 
                    del session_details[0]['quiz_ids'] 
                except : 
                    pass 
                session_details[0]['is_subscribtion'] = False 
                session_details[0]['is_watched'] = False 
                 
                session_details[0]['is_purchased'] = False 
                session_details = false2empty(self ,session_details) 
                session_details = _subscribtion(self ,session_details) 
                session_details[0]['quiz'] = quiz 
                session_details[0]['image_size'] = 5 
 
                response = json.dumps({"data":session_details[0],'message': 'بيانات الجلسة'}) 
                return Response( 
                response, status=200, 
                headers=[('Content-Type', 'application/json')] 
            ) 
            else: 
                response = json.dumps({"data":session_details[0],'message': 'لايمكنك الوصول'}) 
                return Response( 
                response, status=401, 
                headers=[('Content-Type', 'application/json')] 
            ) 
        is_purchased=False 
        user_id = dec_token['id'] 
        if verfiy_token.verfiy_token (self,token,str(user_id)) ==False: 
 
            response = json.dumps({ 'data': [], 'message': 'Unauthorized!'}) 
            return Response( 
            response, status=401, 
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)] 
        ) 
        login=dec_token['login'] 
 
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url)) 
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url)) 
        uid = common.authenticate(self.db,self.username, self.password, {}) 

        session_details = models.execute_kw(self.db, uid, self.password, 'course.video', 'search_read', [[['id' , '=' , id]]], {'fields': ['Title','script_code','quiz_ids','title','is_public','course_id','dacast_id','duration','embeded_code','course_enquiry_ids','video_size','video_file_path']}) 
         
        is_subscribtion= models.execute_kw(self.db, uid, self.password, 'subscription', 'search_read', [['&',['status','=',True],['user_id' , '=' , user_id]] ],{'fields': ['user_id','course_id']}) 
        subs_id=0 
        if is_subscribtion != []: 
            for i in is_subscribtion: 
                if i['course_id'][0] == session_details[0]['course_id'][0] : 
                    session_details[0]['is_subscribtion'] = True 
                    subs_id=int(i['id']) 
                    break 
 
        if len(session_details) >0 : 
            if session_details[0]['quiz_ids'] != []: 
                    quiz = True 
            else : 
                    quiz = False 
            session_details[0]['course_name']=session_details[0]['course_id'][1] 
            session_details[0]['course_id']=session_details[0]['course_id'][0] 
 
        try : 
            del session_details[0]['course_enquiry_ids'] 
 
        except : 
            pass 
        session_details[0]['image_size'] = 5 
        is_watched=models.execute_kw(self.db, uid, self.password, 'session_status', 'search_read', [['&',['user_id','=',user_id],['session_id' , '=' , id]]], {'fields': ['is_watched']}) 
 
        if is_watched!=[]: 
            session_details[0]['is_watched'] = True 
        else : 
            session_details[0]['is_watched'] = False 
 
        if len(session_details) > 0: 
 
            if 'is_subscribtion' in session_details[0] : 
                pass 
            else: 
                session_details[0]['is_subscribtion'] = False 
            session_details = false2empty(self ,session_details) 
            session_details = _subscribtion(self ,session_details) 
            session_details[0]['quiz'] = quiz 
         
        if session_details[0]['is_subscribtion']==True: 
             
            check_purchased=models.execute_kw(self.db, uid, self.password, 'purchased_sessions', 'search_read', [['&',['user_id','=',user_id],['session_id' , '=' , id],['purchased_sessions_id','=',subs_id]]], {'fields': ['id']}) 
             
            if check_purchased==[]: 
                 
                is_purchased=False 
            else : 
                 
                is_purchased=True 
             
        session_details[0]['is_purchased']=is_purchased 
             
        # if session_details[0]['is_purchased']==False: 
        #     session_details[0]['video_file_path']="" 
        # if session_details[0]['script_code']  != False or session_details[0]['script_code']  != '':
        #     script = session_details[0]['script_code']
        #     print('script >>>>>>>>>' , script)
        #     code = '''<!DOCTYPE html>
        #     <html><head>
        #         <meta  name="viewport" content="width=device-width", initial-scale="1.0">
        #         <script 
        #         id="dacast-script"
        #         src="https://player.dacast.com/js/player.js?contentId={}" 
        #         type="application/javascript" async 
        #         class="dacast-video"></script></head><body>
                
        #         <script type="text/javascript">
        #             window.onload = start_player();
        #             function start_player () {
        #                 const datast_script = document.getElementById("dacast-script")
        #                 datast_script.onload = () => {

        #                     const myPlayer = window["dacast"]({}, document.getElementById("dacast-video-player"));  
        #                 }
        #             }

        #         </script>
        #         <div id="dacast-video-player"></div>
        #     </body></html>

        #     '''.format(script, script)
        #     session_details[0]['script_code_flutter'] = code
        # else :
        #     session_details[0]['script_code_flutter'] =''

        response = json.dumps({"data":session_details[0],'message': 'بيانات الجلسة'}) 
        return Response( 
        response, status=200, 
        headers=[('Content-Type', 'application/json')] 
    )

    @http.route('/get_quiz',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_quiz(self,id= None, **kw):
        response = []
        false_answers=[]
        correct_stu_ans = []
        resault=0
        session_name = ''
        subscribtion =False
        authe = request.httprequest.headers
        try:
            token = authe['Authorization'].replace('Bearer ', '')
            dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])

        except Exception as e:
            response = json.dumps({"data":[],'message': 'لا يمكنك الوصول للاختبار'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})

        user_id = int(dec_token['id'])
        # if verfiy_token.verfiy_token (self,token,str(user_id)) ==False:

        #     response = json.dumps({ 'data': [], 'message': 'Unauthorized!'})
        #     return Response(
        #     response, status=401,
        #     headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        # )
        id=int(id)
        quiz_try = models.execute_kw(self.db, uid, self.password, 'resault', 'search_read', [['&',['session_id' , '=', id ],['user_id' , '=', user_id ]]], {'fields': ['try_counter','false_answers','correct_stu_ans','resault']})
        if quiz_try != []:
            number_of_tries = quiz_try[0]['try_counter']
            false_answers = quiz_try[0]['false_answers']
            correct_stu_ans = quiz_try[0]['correct_stu_ans']
            resault = quiz_try[0]['resault']
        else:
            number_of_tries =3
            false_answers=[]
            resault = -1
        if id == None:
            response = json.dumps({"data":[],'message': 'لا يوجد اختبار'})
            return Response(
            response, status=404,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )

        else:
            quiz_ids = models.execute_kw(self.db, uid, self.password, 'course.video', 'search_read', [[['id' , '=' , id]]], {'fields': ['Title','quiz_ids','course_id','is_public']})
            session_name = quiz_ids[0]['Title']
            is_subscribtion= models.execute_kw(self.db, uid, self.password, 'subscription', 'search_read', [['&',['status','=',True],['user_id' , '=' , user_id]] ],{'fields': ['user_id','course_id']})

            if is_subscribtion != []:
                for i in is_subscribtion:
                    if i['course_id'][0] == quiz_ids[0]['course_id'][0] :
                        subscribtion =True
                        break
                    else :

                        subscribtion =False
                        
                        quiz_subscribtion = models.execute_kw(self.db,uid, self.password, 'quiz.subscribe', 'search_read', [[['user_id', '=', user_id]]],{'fields':['course_id']} )

                        if quiz_subscribtion:
                            if quiz_ids[0]['course_id'][0] in quiz_subscribtion[0]['course_id']:

                                subscribtion =True
                                break
                            else:
                                subscribtion =False
                        else:
                            subscribtion =False
            else :

                quiz_subscribtion = models.execute_kw(self.db,uid, self.password, 'quiz.subscribe', 'search_read', [[['user_id', '=', user_id]]],{'fields':['course_id']} )
                
                if quiz_subscribtion:
                    if quiz_ids[0]['course_id'][0] in quiz_subscribtion[0]['course_id']:

                        subscribtion =True
                    else:
                        subscribtion =False
                else:
                    subscribtion =False
            if quiz_ids != []:
                if   subscribtion == True or quiz_ids[0]['is_public']==True :
                    for i in quiz_ids[0]['quiz_ids']:
                        quiz_id = models.execute_kw(self.db, uid, self.password, 'video.quiz', 'search_read', [[['id' , '=' , i]]], {'fields': ['question','answer1','answer2','answer3','answer4','hint']})
                        response.append(quiz_id[0])
                    if len(quiz_id) > 0:
                        response = false2empty(self ,response)
                        if  type(false_answers) != list:
                            false_answers = ast.literal_eval(false_answers)
                        if  type(correct_stu_ans) != list:
                            correct_stu_ans = ast.literal_eval(correct_stu_ans)
                        
                        for question in response:
                            new_question = BeautifulSoup(question["question"],'html.parser')
                            new_question_images = new_question.find_all('img')
                            for img in new_question_images:
                               if img.get('src', img.get('dfr-src')) != None:
                                    img['src'] = 'https://admin.talebeduction.com' + img['src']
                            question["question"] = str(new_question)
                            
                            new_answer1 = BeautifulSoup(question["answer1"],'html.parser')
                            new_answer1_images = new_answer1.find_all('img')
                            for img in new_answer1_images:
                                if img.get('src', img.get('dfr-src')) != None:
                                    img['src'] = 'https://admin.talebeduction.com' + img['src']
                            question["answer1"] = str(new_answer1)

                            new_answer2 = BeautifulSoup(question["answer2"],'html.parser')
                            new_answer2_images = new_answer2.find_all('img')
                            for img in new_answer2_images:
                                print("========================= the img", img)
                                if img.get('src', img.get('dfr-src')) != None:
                                    img['src'] = 'https://admin.talebeduction.com' + img['src']
                            question["answer2"] = str(new_answer2)

                            if question["answer3"] != "":
                                new_answer3 = BeautifulSoup(question["answer3"],'html.parser')
                                new_answer3_images = new_answer3.find_all('img')
                                for img in new_answer3_images:
                                    if img.get('src', img.get('dfr-src')) != None:
                                        img['src'] = 'https://admin.talebeduction.com' + img['src']
                                question["answer3"] = str(new_answer3)
                                
                            if question["answer4"] != "":
                                new_answer4 = BeautifulSoup(question["answer4"],'html.parser')
                                new_answer4_images = new_answer4.find_all('img')
                                for img in new_answer4_images:
                                    if img.get('src', img.get('dfr-src')) != None:
                                        img['src'] = 'https://admin.talebeduction.com' + img['src']
                                question["answer4"] = str(new_answer4)
                       
                        response = json.dumps({"data":{'quiz':response,'number_of_tries':number_of_tries,'false_answers':false_answers ,'correct_stu_ans' :correct_stu_ans,'result':resault , 'session_name':session_name} ,'message': 'الإختبار '})
                        
                        return Response(
                        response, status=200,
                        headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )

                    else:
                        response = json.dumps({"data":[],'message': 'لا يوجد اختبار'})
                        return Response(
                        response, status=404,
                        headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
            
                else :
                    response = json.dumps({"data":[],'message': ' ليس لديك وصول الى هذا الاختبار'})
                    return Response(
                    response, status=404,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
            
            else:
                    response = json.dumps({"data":[],'message': ' لا يوجد اختبار أو ليس لديك وصول الى هذا الاختبار'})
                    return Response(
                    response, status=404,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
    @http.route('/get_why_us',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_why_us(self,idd= None, **kw):
        response = ''
        print( 'asdasdasd' , self.url , self.db , self.password)
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        print('uid ' , uid)
        why_us_data = models.execute_kw(self.db, uid, self.password, 'why.us', 'search_read', [[['id' , '!=' , False]]], {'fields': ['title','brief','video_path']})

        if len(why_us_data) > 0:
            why_us_data = false2empty(self ,why_us_data)
            response = json.dumps({"data":{'WhyUs':why_us_data},'message': 'لماذا نحن '})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )

        else:
            response = json.dumps({"data":[],'message': 'No Data'})
            return Response(
            response, status=404,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )

    @http.route('/get_article',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_article(self,idd= None, **kw):
        response = ''
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        article_id = models.execute_kw(self.db, uid, self.password, 'daily.article', 'search', [[['id' , '!=' , False]]])
        today_article_id = max(article_id)
        today_article =  models.execute_kw(self.db, uid, self.password, 'daily.article', 'search_read', [[['id' , '=' ,today_article_id]]], {'fields': ['title','write_date']})

        try:
            


            response = json.dumps({"data":today_article[0] , 'message' : 'مقولة اليوم'})

            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )

        except:
            return Response(
            response, status=500,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )

    @http.route('/get_top_courses',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_top_courses(self, page= int(1), **kw):
        response = ''

        page = int(page)

        if page == None:
            page = int(1)
        else:
            pass


        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        courses_id = models.execute_kw(self.db, uid, self.password, 'courses', 'search_read', [['&',['is_publish' , '=' , True],['number_of_student' , '!=' , 0]]],{'fields':['name','image_path','number_of_rater','rate', 'number_of_student','teacher_id','date_of_create','number_of_rater','subject_class'], 'offset': (page-1)*5, 'limit': 5, 'order': 'number_of_student desc'})

        x = 0
        for i in courses_id:
            teacher_id = i['teacher_id'][0]

            teacher_name = i['teacher_id'][1]

            courses_id[x]['teacher_id'] = teacher_id
            courses_id[x]['teacher_name'] = teacher_name

            x+= 1
        try:
            courses_id = false2empty(self ,courses_id)
            response = json.dumps({"data":{'courses':courses_id},'message': 'الكورسات الأكثر إشتراكا'})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )

        except:
            response = json.dumps({"data":[],'message': 'لا يوجد كورسات'})
            return Response(
            response, status=404,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )

    @http.route('/get_top_student_by_course_id',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_top_student_by_course_id(self, id = None,**kw):
        response = []
        id = int(id)
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})

        course_value =models.execute_kw(self.db, uid, self.password, 'course.result', 'search_read', [[['course_id' , '=' , id]]],{'fields':['course_result_id','result'] , 'limit': 5, 'order': 'result desc'})

        if course_value != []:
            for i in course_value:
                image_path = models.execute_kw(self.db, uid, self.password, 'res.users', 'search_read', [[['id' , '=' , i['course_result_id'][0]]]],{'fields':['image_path']})

                i['image_path'] = image_path[0]['image_path']
                i['user_name'] = i['course_result_id'][1]
                del i['course_result_id']

        try:
            course_value = false2empty(self ,course_value)
            response = json.dumps({"data":{'student':course_value},'message': 'الطلاب الخمس الأوائل'})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )

        except:
            response = json.dumps({"data":[],'message': 'لا يوجد كورسات'})
            return Response(
            response, status=404,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )
    @http.route('/get_sections_by_id',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_sections_by_id(self,id=None, **kw):
        response = ''
        section_data=[]
        course_grade=0
        section_quiz=False
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        authe = request.httprequest.headers
        id = int(id)
        try:
            print(1)
            token = authe['Authorization'].replace('Bearer ', '')
            dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
            print(1)
            courses_id = models.execute_kw(self.db, uid, self.password, 'courses', 'search_read', [['&',['is_publish' , '=' , True],['id' , '=' , id]]],{'fields':['name','course_sections_ids']})
            print('courses_id' , courses_id)
            if courses_id != []:
                
                section_ids = courses_id[0]['course_sections_ids']


                for i in section_ids:
                    section_quiz=False
                    data = models.execute_kw(self.db, uid, self.password, 'section', 'search_read', [[['id' , '=' , i]]],{'fields':['name','brief','cost','duration']})
                    # session_count = models.execute_kw(self.db, uid, self.password, 'course.video', 'search_count', [[['section_id' , '=' , i]]])
                    # data[0]['session_count'] = session_count
                    # get sessions for this section
                    # check section_quizz 
                    check_quiz=models.execute_kw(self.db, uid, self.password, 'section_quize', 'search_read', [[['section_id' , '=' , int(data[0]['id'])]]], {'fields': ['file_path']})
                    if check_quiz!=[]:
                        section_quiz=True
            
                    

                    data[0]['quiz']=section_quiz
                    #end check section quiz 
                    session_ids = models.execute_kw(self.db, uid, self.password, 'course.video', 'search_read', [[['section_id' , '=' , i]]],{'fields':['Title','id','title','duration','quiz_ids','is_public','video_size','video_file_path']}) 
                    
                    data[0]['session_count'] = len(session_ids)
                    data[0]['sessions']=session_ids
                    
                    # is_subscribtion = request.env['purchased_sections'].search(['&',('user_id' , '=' ,int(dec_token['id'])),('section_id' '=' ,int(i) )])
                    is_subscribtion = models.execute_kw(self.db,uid, self.password, 'purchased_sections', 'search_count', [['&',['user_id', '=', int(dec_token['id'])],['section_id','=',int(i) ]]] )
                    # is_subscribtion = models.execute_kw(self.db, uid, self.password, 'purchased_sections', 'search', [['&',['user_id' , '=' ,int(dec_token['id'])],['section_id' '=' ,int(i) ]]]) 
                    if is_subscribtion == 0:
                        data[0]['is_subscribtion']=False
                        data[0]['quiz_subscribtion']=False
                        quiz_subscribtion = models.execute_kw(self.db,uid, self.password, 'quiz.subscribe', 'search_read', [[['user_id', '=', int(dec_token['id'])]]],{'fields':['course_id']} )
                        # courses_id = models.execute_kw(self.db, uid, self.password, 'courses', 'search_read', [[['is_publish' , '=' , True]]],{'fields':['name','course_sections_ids']})
                        # print('quiz_subscribtion  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> |||||||||||||||||||||||||| ????????????? >>>>>>>' , quiz_subscribtion)
                        if quiz_subscribtion:
                            if int(courses_id[0]['id']) in quiz_subscribtion[0]['course_id']:
                                data[0]['quiz_subscribtion']=True
                            else:
                                data[0]['quiz_subscribtion']=False
                        else:
                            data[0]['quiz_subscribtion']=False
                    else:
                        data[0]['is_subscribtion']=True
                        data[0]['quiz_subscribtion']=True
                    session_public = models.execute_kw(self.db,uid, self.password, 'course.video', 'search_count', [[['is_public', '=', True],['section_id','=',int(i) ]]] )
                    session_section_public = models.execute_kw(self.db,uid, self.password, 'course.video', 'search_count', [[['section_id','=',int(i) ]]] )
                    if session_public == session_section_public and  session_public != 0:
                        data[0]['is_subscribtion']=True
                    # end get_sessions
                    section_data.append(data[0])
                number_of_sections=len(section_ids)
        except Exception as e:
            courses_id = models.execute_kw(self.db, uid, self.password, 'courses', 'search_read', [['&',['is_publish' , '=' , True],['id' , '=' , id]]],{'fields':['name','course_sections_ids']})

            if courses_id != []:

                section_ids = courses_id[0]['course_sections_ids']


                for i in section_ids:
                    data = models.execute_kw(self.db, uid, self.password, 'section', 'search_read', [[['id' , '=' , i]]],{'fields':['name','brief','duration']})
                    # session_count = models.execute_kw(self.db, uid, self.password, 'course.video', 'search_count', [[['section_id' , '=' , i]]])
                    # data[0]['session_count'] = session_count
                    # get sessions for this section
                    # check section_quizz 
                    print('data ' , data)
                    check_quiz=models.execute_kw(self.db, uid, self.password, 'section_quize_result', 'search_read', [[['section_id' , '=' , int(data[0]['id'])]]], {'fields': ['file_path']})
                    if check_quiz!=[]:
                        section_quiz=True
            
                    section_quiz=False

                    data[0]['quiz']=section_quiz
                    #end check section quiz 
                    session_ids = models.execute_kw(self.db, uid, self.password, 'course.video', 'search_read', [[['section_id' , '=' , i]]],{'fields':['Title','id','title','duration','quiz_ids','is_public','video_size','video_file_path']}) 
                    
                    data[0]['session_count'] = len(session_ids)
                    data[0]['sessions']=session_ids
                    data[0]['is_subscribtion']=False
                    data[0]['quiz_subscribtion']=False
                    
                    # end get_sessions
                    section_data.append(data[0])

                number_of_sections=len(section_ids)


        try:
            print('section_data' , section_data)
            section_data = false2empty(self ,section_data)
            response = json.dumps({"data":{'sections':section_data,'number_of_sections':number_of_sections},'message': 'أقسام الكورس'})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )

        except:
            response = json.dumps({"data":[],'message': 'لا يوجد كورسات'})
            return Response(
            response, status=404,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )
        

    @http.route('/get_course_by_id',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_course_by_id(self,id=None, **kw):
        response = ''
        skills=[]
        can_cancle=False
        course_data=[]
        course_grade=0
        is_subscribtion=False
        number_of_sessions = 0
        authe = request.httprequest.headers

        try:
            token = authe['Authorization'].replace('Bearer ', '')

            dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])




        except Exception as e:


            common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
            models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
            uid = common.authenticate(self.db,self.username, self.password, {})
            courses_id = models.execute_kw(self.db, uid, self.password, 'courses', 'search_read', [[['id' , '=' , id]]],{'fields':['name','rate','number_of_rater','date_of_create','skills_id','teacher_id','cost','image_path','teacher_name','brief','expiration_month','number_of_student','about_this_course','duration']})
            number_of_sessions =models.execute_kw(self.db, uid, self.password, 'course.video', 'search_read', [[['course_id' , '=' , courses_id[0]['id']]]], {
                                        'fields': ['id']})
            number_of_sessions=len(number_of_sessions)
            for i in range(len(courses_id[0]["skills_id"])):
                x = models.execute_kw(self.db, uid, self.password, 'skills', 'search_read', [[['id' , '=' , courses_id[0]["skills_id"][i]]]],{'fields':['name']})

                skills.append(x[0]['name'])

            courses_id[0]["skills_id"] = skills
            courses_id[0]["teacher_id"] = courses_id[0]["teacher_id"][0]
            try:
                courses_id = false2empty(self ,courses_id)
                response = json.dumps({"data":{'courses':courses_id[0],"is_subscribtion":is_subscribtion,'course_grade':course_grade,'can_cancle_subcribtion':can_cancle ,'number_of_sessions' : number_of_sessions},'message': 'تفاصيل الكورس'})
                return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
            )

            except:
                response = json.dumps({"data":[],'message': 'لا يوجد كورسات'})
                return Response(
                response, status=404,
                headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
            )
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        courses_id = models.execute_kw(self.db, uid, self.password, 'courses', 'search_read', [[['id' , '=' , id]]],{'fields':['name','rate','number_of_rater','date_of_create','skills_id','teacher_id','image_path','teacher_name','brief','cost','expiration_month','number_of_student','about_this_course','duration']})

        user_id = int(dec_token['id'])
        if verfiy_token.verfiy_token (self,token,str(user_id)) ==False:

            response = json.dumps({ 'data': [], 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        try:

            subscription_ids = models.execute_kw(self.db, uid, self.password, 'subscription', 'search_read', [['&',['course_id' , '=' , courses_id[0]['id']],['user_id' , '=' , user_id]]],{'fields':['id','points','start_date']})

            number_of_sessions =models.execute_kw(self.db, uid, self.password, 'course.video', 'search_read', [[['course_id' , '=' , courses_id[0]['id']]]], {
                                        'fields': ['id']})
        except:
            response = json.dumps({ 'data': [], 'message': 'الكورس غير موجود'})
            return Response(
            response, status=404,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )

        number_of_watched_session= models.execute_kw(self.db, uid, self.password, 'session_status', 'search_read', [['&',['user_id','=',user_id],['course_name' , '=' , courses_id[0]['id']],['is_watched','=',True]]], {'fields': ['session_id']})
        number_of_sessions=len(number_of_sessions)

        number_of_watched_session=len(number_of_watched_session)
        if number_of_sessions >0:
            percentage = (number_of_watched_session / number_of_sessions) * 100
            percentage=math.floor(percentage)
        else :
            percentage=1

        if subscription_ids !=[]:
            is_subscribtion=True

        for i in range(len(courses_id[0]["skills_id"])):
             x = models.execute_kw(self.db, uid, self.password, 'skills', 'search_read', [[['id' , '=' , courses_id[0]["skills_id"][i]]]],{'fields':['name']})

             skills.append(x[0]['name'])

        courses_id[0]["skills_id"] = skills
        courses_id[0]["teacher_id"] = courses_id[0]["teacher_id"][0]

        if percentage <5 :
            if subscription_ids!=[]:
                current_date = datetime.now().date()

                start= datetime.strptime(subscription_ids[0]['start_date'], '%Y-%m-%d').date()

                date_difference = relativedelta(current_date,start)
                days_since_date = date_difference.days
                if days_since_date <2:
                    can_cancle=True
                else :
                    can_cancle=False




        else :
            can_cancle=False


        try:

            x = models.execute_kw(self.db, uid, self.password, 'resault', 'search_read', [['&',['course_id','=',id],['user_id' , '=' , user_id]]],{'fields':['resault']})
            if x:
                if x[0]:
                    course_grade = x[0]['resault']

            courses_id = false2empty(self ,courses_id)
            response = json.dumps({"data":{'courses':courses_id[0],'is_subscribtion':is_subscribtion,'course_grade':course_grade,'can_cancle_subcribtion':can_cancle,'number_of_sessions' : number_of_sessions},'message': 'تفاصيل الكورس'})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )

        except:
                response = json.dumps({"data":[],'message': 'لا يوجد كورسات'})
                return Response(
                response, status=404,
                headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
            )
    @http.route('/get_search_courses',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_search_courses(self, search= None, **kw):
        response = ''
        resault =[]
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        courses_id = models.execute_kw(self.db, uid, self.password, 'courses', 'search_read', [[['id' , '!=' , False]]],{'fields':['name','brief','image_path','rate', 'number_of_rater','number_of_student','subject_class','teacher_name','date_of_create','number_of_rater']})
        for i in courses_id:

            if search in i['name'] or search in str(i['teacher_name']) or search in str(i['subject_class']):
                resault.append(i)


        try:
            resault = false2empty(self ,resault)
            response = json.dumps({"data":{'courses':resault},'message': 'نتائج البحث'})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )

        except:
            response = json.dumps({"data":[],'message': 'لا يوجد كورسات'})
            return Response(
            response, status=404,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )


    @http.route('/get_explore_courses',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_explore_courses(self, page=None, search= None, **kw):
        response = ''
        resault =[]
        check_page=False
        # page=int(page)

        if page == None:
            page = int(1)
            check_page=True
        else:
            
            page = int(page)
            check_page=False
            
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        if check_page==False:
            courses_id = models.execute_kw(self.db, uid, self.password, 'courses', 'search_read', [['&',['is_publish','=', True],['subject_class' , '=' , search]]],{'fields':['name','image_path','rate','number_of_rater', 'number_of_student','subject_class','teacher_name','date_of_create','number_of_rater','brief','cost','course_number'], 'offset': (page-1)*5, 'limit': 5, 'order': 'course_number asc'})
        else :
            
            courses_id = models.execute_kw(self.db, uid, self.password, 'courses', 'search_read', [['&',['is_publish','=', True],['subject_class' , '=' , search]]],{'fields':['name','image_path','rate','number_of_rater', 'number_of_student','subject_class','teacher_name','date_of_create','number_of_rater','brief','cost','course_number'],'order': 'course_number asc'})


        try:
            courses_id = false2empty(self ,courses_id)
            response = json.dumps({"data":{'courses':courses_id},'message': 'نتائج البحث'})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )

        except:
            response = json.dumps({"data":[],'message': 'لا يوجد كورسات'})
            return Response(
            response, status=404,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )
    
    @http.route('/get_explore_packages',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_explore_packages(self, page= int(1), search= None, **kw):
        response = ''
        resault =[]
        page = int(page)

        if page == None:
            page = int(1)
        else:
            pass
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        # packages_ids = models.execute_kw(self.db, uid, self.password, 'packages', 'search_read', [['subject_class' , '=' , search]],{'fields':['name']})
        packages_ids=models.execute_kw(self.db, uid, self.password, 'packages', 'search_read', [[['subject_class','=',search]]],{'fields': ['name','new_price','old_price','image_path','brief','subject_class']})
        print("Packages")
        print(packages_ids)


        try:
            packages_ids = false2empty(self ,packages_ids)
            response = json.dumps({"data":{'packages':packages_ids},'message': 'نتائج البحث'})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )

        except:
            response = json.dumps({"data":[],'message': 'لا يوجد حزم'})
            return Response(
            response, status=404,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )

    @http.route('/get_sessions_by_section_id',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_sessions_by_section_id(self, id= None, **kw):
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        uid = common.authenticate(self.db, self.username, self.password, {})
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        response = ''
        resault =[]
        course_id={}
        authe = request.httprequest.headers
        id=int(id)
        try:

            token = authe['Authorization'].replace('Bearer ', '')
            dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])

        except Exception as e:
            session_ids = models.execute_kw(self.db, uid, self.password, 'course.video', 'search_read', [[['id' , '!=' , False]]],{'fields':['Title','id','title','section_id','course_id','duration','quiz_ids','is_public']})
            section_info=models.execute_kw(self.db, uid, self.password, 'section', 'search_read', [[['id' , '=' , id]]],{'fields':['name','brief','course_id']})


            section_info[0]['course_id'] = int(section_info[0]['course_id'][0])
            session_id = []
            for i in session_ids:
                section_id = int(i['section_id'][0])


                i['is_subscribtion'] = False
                i['quiz_subscribtion']=False
                if section_id == id :
                    del i['section_id']

                    i['number_of_quizes']=len(i['quiz_ids'])
                    del i['quiz_ids']
                    # is_watched=models.execute_kw(self.db, uid, self.password, 'session_status', 'search_read', [['&',['user_id','=',user_id],['session_id' , '=' , int(i['id'])]]], {'fields': ['is_watched']})


                    i['is_watched'] = False

                    resault.append(i)
            if resault == []:
                response = json.dumps({"data":[],'message': 'لا يوجد جلسات'})
                return Response(
                response, status=404,
                headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
            )

            course_id=resault[0]['course_id'][0]
            for r in resault:
                del r['course_id']

            course_info=models.execute_kw(self.db, uid, self.password, 'courses', 'search_read', [[['id' , '=' , course_id]]],{'fields':['name','teacher_name','date_of_create','about_this_course',]})
            course_info=false2empty(self,course_info)
            section_info[0]['number_of_videos']=len(resault)
            section_info=false2empty(self,section_info)





            try:
                resault = false2empty(self ,resault)
                response = json.dumps({"data":{'videos':resault,'course':course_info[0],'section':section_info[0]},'message': 'الجلسات الخاصة بهذا القسم'})
                return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
            )

            except:
                response = json.dumps({"data":[],'message': 'لا يوجد جلسات'})
                return Response(
                response, status=404,
                headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
            )


        user_id = int(dec_token['id'])
        if verfiy_token.verfiy_token (self,token,str(user_id)) ==False:

            response = json.dumps({ 'data': [], 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )

        session_ids = models.execute_kw(self.db, uid, self.password, 'course.video', 'search_read', [[['id' , '!=' , False]]],{'fields':['Title','id','title','section_id','course_id','duration','quiz_ids','is_public','video_file_path','video_size']})
        section_info=models.execute_kw(self.db, uid, self.password, 'section', 'search_read', [[['id' , '=' , id]]],{'fields':['name','brief','course_id']})
        section_info[0]['course_id'] =  int(section_info[0]['course_id'][0])

        subscription_ids = models.execute_kw(self.db, uid, self.password, 'purchased_sections', 'search_read', [['&',['section_id' , '=' , section_info[0]['id']],['user_id' , '=' , user_id]]],{'fields':['id']})
        session_id = []
        for i in session_ids:

            section_id = int(i['section_id'][0])

            if subscription_ids != []:
                i['is_subscribtion'] = True
                i['quiz_subscribtion']=True
            else:
                i['is_subscribtion'] = False
                i['quiz_subscribtion']=False
                quiz_subscribtion = models.execute_kw(self.db,uid, self.password, 'quiz.subscribe', 'search_read', [[['user_id', '=', int(dec_token['id'])]]],{'fields':['name','course_id']} )
                if quiz_subscribtion:
                    if section_info[0]['course_id'] in quiz_subscribtion[0]['course_id']:
                        i['quiz_subscribtion']=True
                    else:
                        i['quiz_subscribtion']=False
            if section_id == id :
                del i['section_id']
                i['number_of_quizes']=len(i['quiz_ids'])
                del i['quiz_ids']
                
                is_watched=models.execute_kw(self.db, uid, self.password, 'session_status', 'search_read', [['&',['user_id','=',user_id],['session_id' , '=' , int(i['id'])]]], {'fields': ['is_watched']})

                if is_watched!=[]:
                    i['is_watched'] = True
                else :
                    i['is_watched'] = False

                resault.append(i)
        if resault == []:
            response = json.dumps({"data":[],'message': 'لا يوجد جلسات'})
            return Response(
            response, status=404,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )

        course_id=resault[0]['course_id'][0]
        for r in resault:
            del r['course_id']
        course_info=models.execute_kw(self.db, uid, self.password, 'courses', 'search_read', [[['id' , '=' , course_id]]],{'fields':['name','teacher_name','date_of_create','about_this_course',]})
        course_info=false2empty(self,course_info)


        section_info[0]['number_of_videos']=len(resault)
        section_info=false2empty(self,section_info)
        section_quiz=False
        check_quiz=models.execute_kw(self.db, uid, self.password, 'section_quize_result', 'search_read', [[['section_id' , '=' , int(id)]]], {'fields': ['file_path']})
        if check_quiz!=[]:
            section_quiz=True
        

        section_info[0]['quiz']=section_quiz
        try:
            resault = false2empty(self ,resault)
            response = json.dumps({"data":{'videos':resault,'course':course_info[0],'section':section_info[0]},'message': 'الجلسات الخاصة بهذا القسم'})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )

        except:
            response = json.dumps({"data":[],'message': 'لا يوجد جلسات'})
            return Response(
            response, status=404,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )


    @http.route('/get_course_raters',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_course_raters(self, page= int(1), id= None, **kw):
        response = ''
        resault =[]
        id = int(id)
        page = int(page)

        if page == None:
            page = int(1)
        else:
            pass
        authe = request.httprequest.headers

        try:
            token = authe['Authorization'].replace('Bearer ', '')
            dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])

        except Exception as e:
            # common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
            # uid = common.authenticate(self.db, self.username, self.password, {})
            # models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
            # course = models.execute_kw(self.db, uid, self.password, 'rate', 'search_read', [[['course_id' , '=' , id]]],{'fields':['id','rate_value']})



            # if course != []:
            #     if course[0]['rate_value'] :
            #         for i in course[0]['rate_value']:
            #             rate_id =  i
            #             rate = models.execute_kw(self.db, uid, self.password, 'rate.value', 'search_read', [[['id' , '=' , i] ]],{'fields':['id','rataing' ,'comment','date_of_create', 'user_id' ,'image_path'], 'offset': (page-1)*5, 'limit': 5, 'order': 'id desc'})
            #             user_rated=True
            #             for j in rate :




            #                 j['user_name'] = j['user_id'][1]
            #                 j['user_id'] = j['user_id'][0]

            #             resault.append(rate[0])



            # try:
            #     courses_id = models.execute_kw(self.db, uid, self.password, 'courses', 'search_read', [[['id','=', id]]],{'fields':['rate','number_of_rater']})
            #     resault = _nocomment(self ,resault)
            #     resault = false2empty(self ,resault)
            #     response = json.dumps({"data":{'rate' : courses_id[0]['rate'] ,'number_of_rater':courses_id[0]['number_of_rater'],'rates':resault,'user_rated':user_rated},'message': 'التقييمات الخاصة بهذا الكورس'})
            #     return Response(
            #     response, status=200,
            #     headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
            # )

            # except:
                response = json.dumps({"data":{'rates' :[]},'message': 'لا يوجد تقييمات'})
                return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
            )


        user_id = dec_token['id']
        login=dec_token['login']
        user_rated=False



        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        uid = common.authenticate(self.db, self.username, self.password, {})
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        course = models.execute_kw(self.db, uid, self.password, 'rate', 'search_read', [[['course_id' , '=' , id]]],{'fields':['id','rate_value']})



        if course != []:
            if course[0]['rate_value'] :
                for i in course[0]['rate_value']:
                    rate_id =  i



                    rate = models.execute_kw(self.db, uid, self.password, 'rate.value', 'search_read', [[['id' , '=' , i],['user_id' , '=' , user_id]]],{'fields':['id','rataing' ,'comment','date_of_create', 'user_id' ,'image_path'], 'offset': (page-1)*5, 'limit': 5, 'order': 'id desc'})
                    if rate != []:
                        if rate[0]['user_id'][0]==user_id:
                                user_rated=True
                        for j in rate :




                            j['user_name'] = j['user_id'][1]
                            j['user_id'] = j['user_id'][0]

                        resault.append(rate[0])



        try:
            courses_id = models.execute_kw(self.db, uid, self.password, 'courses', 'search_read', [[['id','=', id]]],{'fields':['rate','number_of_rater']})
            resault = false2empty(self ,resault)
            response = json.dumps({"data":{'rate' : courses_id[0]['rate'] ,'number_of_rater':courses_id[0]['number_of_rater'],'rates':resault,'user_rated':user_rated},'message': 'التقييمات الخاصة بهذا الكورس'})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )

        except:
            response = json.dumps({"data":[],'message': 'لا يوجد تقييمات'})
            return Response(
            response, status=404,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )


    @http.route('/get_teacher_raters',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_teacher_raters(self, page= int(1), id= None, **kw):
        response = ''
        resault =[]
        page = int(page)

        if page == None:
            page = int(1)
        else:
            pass
        authe = request.httprequest.headers

        try:
            token = authe['Authorization'].replace('Bearer ', '')
            dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])

        except Exception as e:

            user_rated=True

            # id = int(id)
            # common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
            # uid = common.authenticate(self.db, self.username, self.password, {})
            # models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
            # teacher = models.execute_kw(self.db, uid, self.password, 'teacher_rate', 'search_read', [[['teacher_id' , '=' , id]]],{'fields':['id','rate_value']})

            # if teacher != []:
            #     if teacher[0]['rate_value'] :
            #         for i in teacher[0]['rate_value']:
            #             rate_id =  i


            #             rate = models.execute_kw(self.db, uid, self.password, 'teacher.value', 'search_read', [[['id' , '=' , i]]],{'fields':['id','rataing' ,'comment','date_of_create', 'user_id' ]})

            #             for j in rate :


            #                 j['user_name'] = j['user_id'][1]
            #                 j['user_id'] = j['user_id'][0]

            #             resault.append(rate[0])



            # try:
            #     teacher_id = models.execute_kw(self.db, uid, self.password, 'teacher', 'search_read', [[['id','=', id]]],{'fields':['rate','number_of_rater']})
            #     resault = false2empty(self ,resault)
            #     response = json.dumps({"data":{'rate' : teacher_id[0]['rate'] ,'number_of_rater':teacher_id[0]['number_of_rater'],'rates':resault,'user_rated':user_rated},'message': 'التقييمات الخاصة بهذا الأستاذ'})
            #     return Response(
            #     response, status=200,
            #     headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
            # )

            # except:
            response = json.dumps({"data":[],'message': 'لا يوجد جلسات'})
            return Response(
            response, status=404,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )


        user_id = dec_token['id']
        login=dec_token['login']
        user_rated=False

        id = int(id)
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        uid = common.authenticate(self.db, self.username, self.password, {})
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        teacher = models.execute_kw(self.db, uid, self.password, 'teacher_rate', 'search_read', [[['teacher_id' , '=' , id]]],{'fields':['id','rate_value']})

        if teacher != []:
            if teacher[0]['rate_value'] :
                for i in teacher[0]['rate_value']:
                    rate_id =  i


                    rate = models.execute_kw(self.db, uid, self.password, 'teacher.value', 'search_read', [[['id' , '=' , i]]],{'fields':['id','rataing' ,'comment','date_of_create', 'user_id' ], 'offset': (page-1)*5, 'limit': 5, 'order': 'id desc'})
                    if rate != []:
                        
                        for j in rate :
                            if j['user_id'][0]==user_id:
                                user_rated=True

                            j['user_name'] = j['user_id'][1]
                            j['user_id'] = j['user_id'][0]
                        if rate[0]['user_id'][0]==user_id:
                            user_rated=True
                            resault.append(rate[0])



        try:
            teacher_id = models.execute_kw(self.db, uid, self.password, 'teacher', 'search_read', [[['id','=', id]]],{'fields':['rate','number_of_rater']})
            resault = false2empty(self ,resault)
            response = json.dumps({"data":{'rate' : teacher_id[0]['rate'] ,'number_of_rater':teacher_id[0]['number_of_rater'],'rates':resault,'user_rated':user_rated},'message': 'التقييمات الخاصة بهذا الأستاذ'})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )

        except:
            response = json.dumps({"data":[],'message': 'لا يوجد جلسات'})
            return Response(
            response, status=404,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )

    @http.route('/get_simillar_courses',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_simillar_courses(self,id= None, **kw):
        response = ''
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        if id == None:
            response = json.dumps({"data":[],'message': 'لا يوجد كورسات'})
            return Response(
            response, status=404,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )

        else:

            courses_id = models.execute_kw(self.db, uid, self.password, 'courses', 'search_read', [[['id' , '=' , id]]], {'fields': ['subject_class']})


            if courses_id[0]:
                if courses_id[0]['subject_class']:
                    courses_data = models.execute_kw(self.db, uid, self.password, 'courses', 'search_read', [['&',['id' , '!=' , id],['is_publish' ,'=', True],['subject_class' ,'=', courses_id[0]['subject_class']]]], {'fields': ['subject_class' ,'name','brief','teacher_name','rate','number_of_rater','about_this_course','date_of_create','cost','number_of_student','image_path']})


                    if len(courses_data) > 0:
                        courses_data = false2empty(self ,courses_data)
                        response = json.dumps({"data":{'courses':courses_data},'message': 'معلومات الكورسات المشابهة '})
                        return Response(
                        response, status=200,
                        headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )

                    else:
                        response = json.dumps({"data":[],'message': 'لا يوجد كورسات مشابهة'})
                        return Response(
                        response, status=404,
                        headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
            else:
                        response = json.dumps({"data":[],'message': 'لا يوجد كورسات مشابهة'})
                        return Response(
                        response, status=404,
                        headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )


    @http.route('/get_simillar_demend_courses',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_simillar_demend_courses(self,id= None, **kw):
        response = ''
        response_data= []
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

        user_id = dec_token['id']
        if verfiy_token.verfiy_token (self,token,str(user_id)) ==False:

            response = json.dumps({ 'data': [], 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        login=dec_token['login']
        user_rated=False

        id = int(id)


        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        uid = common.authenticate(self.db, self.username, self.password, {})
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        if id == None:
            response = json.dumps({"data":[],'message': 'لا يوجد كورسات'})
            return Response(
            response, status=404,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )

        else:

            courses_id = models.execute_kw(self.db, uid, self.password, 'courses', 'search_read', [[['id' , '=' , id]]], {'fields': ['subject_class']})



            if courses_id[0]:
                if courses_id[0]['subject_class']:
                    courses_data = models.execute_kw(self.db, uid, self.password, 'courses', 'search_read', [['&',['id' , '!=' , id],['is_publish' ,'=', True],['subject_class' ,'=', courses_id[0]['subject_class']]]], {'fields': ['subject_class' ,'name','brief','cost','teacher_name','rate','number_of_rater','about_this_course','cost','number_of_student','image_path']})

                    for course_data in courses_data:


                        courses_sub = models.execute_kw(self.db, uid, self.password, 'subscription', 'search_read', [['&',['user_id' , '!=' , user_id],['course_id' ,'=', id]]])


                        if courses_sub != []:
                            response_data.append(course_data)
                        else:
                            pass
                    if len(response_data) > 0:
                        response_data = false2empty(self ,response_data)
                        response = json.dumps({"data":{'courses':response_data},'message': 'معلومات الكورسات المشابهة '})
                        return Response(
                        response, status=200,
                        headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )

                    else:
                        response = json.dumps({"data":[],'message': 'لا يوجد كورسات مشابهة'})
                        return Response(
                        response, status=404,
                        headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
            else:
                        response = json.dumps({"data":[],'message': 'لا يوجد كورسات مشابهة'})
                        return Response(
                        response, status=404,
                        headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )


    @http.route('/get_user_notification',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_user_notification(self,page= int(1), **kw):
        limit=7
        response = ''
        page = int(page)
        resault =[]
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

        user_id = int(dec_token['id'])
        if verfiy_token.verfiy_token (self,token,str(user_id)) ==False:

            response = json.dumps({ 'data': [], 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        uid = common.authenticate(self.db, self.username, self.password, {})
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        notifications = models.execute_kw(self.db, uid, self.password, 'notifications', 'search_read', [[['user_id' , '=' , user_id]]],{'fields':['data','comment','is_seen'],'offset': (int(page)-1)*5, 'limit': limit, 'order': 'id desc'})
        notification = models.execute_kw(self.db, uid, self.password, 'notifications', 'search_read', [[['user_id' , '=' , user_id]]],{'fields':['data','comment','is_seen']})
        record_per_page=limit
        for noti in notifications :
            noti['data']=ast.literal_eval(noti['data'])



        notifications=false2empty(self ,notifications)
        total=len(notification)
        if notifications != []:
            response = json.dumps({ 'data': notifications,'total_records':total,'record_per_page':record_per_page ,'message': 'الإشعارات'})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )

        else:
            response = json.dumps({ 'data': [], 'message': 'لايوجد اشعارات'})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )


    @http.route('/get_hero_section',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_hero_section(self,idd= None, **kw):
        response = ''

        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        hero_section = models.execute_kw(self.db, uid, self.password, 'hero.section', 'search_read', [[['id' , '!=' , False]]], {'fields': ['title','image_path']})

        if len(hero_section) > 0:
            hero_section = false2empty(self ,hero_section)
            response = json.dumps({"data":{'hero_section':hero_section[0]},'message': 'معلومات الصفحة الرئيسية '})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )

        else:
            response = json.dumps({"data":[],'message': 'معلومات الصفحة الرئيسية '})
            return Response(
            response, status=404,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )


    @http.route('/get_coupon_discount',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_coupon_discount(self,code=None,course_id=None,**kw):
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
        if course_id != None:
            course_id = int(course_id)
        else:
            response = json.dumps({"data":[],'message': 'لا يوجد معلومات'})
            return Response(
            response, status=404,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        if code == None:
            response = json.dumps({"data":[],'message': 'لا يوجد معلومات'})
            return Response(
            response, status=404,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        else:
            data =models.execute_kw(self.db, uid, self.password, 'promotion.code', 'search_read', [[['promotion_code' , '=', code]]] , {'fields': ['course_ids', 'discount_percentage','is_valid','user_id']})
            if data != [] and course_id in data[0]['course_ids'] and data[0]['is_valid'] == True:
              
                # data=models.execute_kw(self.db, uid, self.password, 'promotion.code', 'search_read', [[['package_promotion.code' , '=', code]]] , {'fields': ['course_ids', 'discount_percentage']})
                models.execute_kw(self.db, uid, self.password, 'promotion.code.user', 'create', [{'promotion_id': data[0]['user_id'][0], 'user_id': user_id }])
                response = json.dumps({"data":data[0],'message': 'معلومات الكوبون '})
                return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
            else:
                response = json.dumps({"data":[],'message': 'هذا الرمز غير فعال، ربما انتهت صلاحيته!'})
                return Response(
                response, status=404,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )

    @http.route('/get_session_comments',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_session_comments(self,id,**kw):
        Comments=[]
        id=int(id)
        x=0
        authe = request.httprequest.headers
        try:
            token = authe['Authorization'].replace('Bearer ', '')

            dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
        except Exception as e:
            common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
            models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
            uid = common.authenticate(self.db,self.username, self.password, {})
            session_details = models.execute_kw(self.db, uid, self.password, 'course.video', 'search_read', [[['id' , '=' , id]]], {'fields': ['Title','title','course_id','quiz_ids','course_enquiry_ids',]})
            rep={}
            print('session_details' ,session_details)
            if len(session_details) >0 :
                if session_details[0]['quiz_ids'] != []:
                    quiz = True
                    # my_grade =
                else :
                    quiz = False
                session=session_details[0]

                if len(session['course_enquiry_ids'])>0:
                    for comment_id in session['course_enquiry_ids']:
                        comments={}
                        rep={}
                        comment_info=models.execute_kw(self.db, uid, self.password, 'enquiries', 'search_read', [['&',['id' , '=' , comment_id],['pending','=',False]]], {'fields': ['replay_enquiry_ids','user_id','comment','enquiry_id','replay_enquiry_ids','image_path','create_date','image_ids']})
                        print('comment_info' , comment_info)
                        if comment_info !=[]:
                            comments['user_name']=comment_info[0]['user_id'][1]
                            comments['user_id']=comment_info[0]['user_id'][0]
                            comments['comment']=comment_info[0]['comment']
                            comments['id']=comment_info[0]['id']
                            comments['image_path']=comment_info[0]['image_path']
                            comments['create_date']=comment_info[0]['create_date']
                            comments['images'] = []
                            if comment_info[0]['image_ids']:
                                for image in comment_info[0]['image_ids']:
                                    image_info =models.execute_kw(self.db, uid, self.password, 'comment.images', 'search_read', [[['id' , '=' , image]]], {'fields': ['image_url']})
                                    comments['images'].append({
                                        'image' : image_info[0]['image_url']
                                    })
                            del comment_info[0]['image_ids']
                                
                            if len(comment_info[0]['replay_enquiry_ids'])>0:
                                print("comment_info[0]['replay_enquiry_ids']" , comment_info[0]['replay_enquiry_ids'])
                                reply=comment_info[0]['replay_enquiry_ids'][0]
                                print('reply' , reply)
                                reply_info=models.execute_kw(self.db, uid, self.password, 'replay_enquiry', 'search_read', [[['id' , '=' , reply]]], {'fields': ['image_path','user_id','comment','replay_id','status','comment_id','create_date','image_url1' ,'image_url2','image_url3','image_url4','image_url5']})
                                rep['user_name']=reply_info[0]['user_id'][1]
                                user_id=reply_info[0]['user_id'][0]
                                rep['id']=reply_info[0]['id']
                                rep['comment']=reply_info[0]['comment']
                                rep['image_path']=reply_info[0]['image_path']
                                rep['status']=reply_info[0]['status']
                                rep['create_date']=reply_info[0]['create_date']
                                if reply_info[0]['comment_id'] != False:
                                    rep['comment_id']=reply_info[0]['comment_id'][0]
                                    rep['comment_body']=reply_info[0]['comment_id'][1]
                                else:
                                    rep['comment_id']=''
                                    rep['comment_body']=''
                                user_type=models.execute_kw(self.db, uid, self.password, 'res.users', 'search_read', [[['id' , '=' , user_id]]], {'fields': ['user_type']})
                                rep['user_type']=user_type[0]['user_type']
                                print('rep' , rep)
                                print("comments['reply']" , comments)
                            comments['reply']=rep
                            Comments.append(comments)

                session['Comments']=Comments
                session['Comments'] = false2empty(self ,session['Comments'])

            try :
                del session_details[0]['course_enquiry_ids']
                del session_details[0]['quiz_ids']
            except :
                pass
            if Comments==[]:
                response = json.dumps({"data":[],'message': ' لا يوجد أسئلة على هذه الجلسة'})
                return Response(
                response, status=200,
            headers=[('Content-Type', 'application/json')])
            response = json.dumps({"data":Comments,'message': 'التعليقات  والردور على الجلسة'})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json')])

        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        session_details = models.execute_kw(self.db, uid, self.password, 'course.video', 'search_read', [[['id' , '=' , id]]], {'fields': ['Title','title','course_id','quiz_ids','course_enquiry_ids',]})
        user_id = int(dec_token['id'])

        pending_comments=[]
        if len(session_details) >0 :
            if session_details[0]['quiz_ids'] != []:
                quiz = True
                # my_grade =
            else :
                quiz = False
            for session in session_details :
                if len(session['course_enquiry_ids'])>0:
                    for id in session['course_enquiry_ids']:
                        pending_comment=models.execute_kw(self.db,uid,self.password,'enquiries','search_read', [['&',['id' , '=' , id],['pending','=',True]]], {'fields': ['pending','user_id','comment','enquiry_id','replay_enquiry_ids','image_path','create_date','image_ids']})
                        if pending_comment!=[] and pending_comment[0]['user_id']!= False and pending_comment[0]['user_id'][0]==user_id :
                            pending_comment[0]['user_name']=pending_comment[0]['user_id'][1]
                            pending_comment[0]['user_id']=pending_comment[0]['user_id'][0]
                            del pending_comment[0]['replay_enquiry_ids']
                            del pending_comment[0]['enquiry_id']
                            pending_comment[0]['images']=[]
                            if pending_comment[0]['image_ids']:
                                for image in pending_comment[0]['image_ids']:
                                    image_info =models.execute_kw(self.db, uid, self.password, 'comment.images', 'search_read', [[['id' , '=' , image]]], {'fields': ['image_url']})
                                    pending_comment[0]['images'].append({
                                        'image' : image_info[0]['image_url']
                                    })
                            pending_comments.append(pending_comment[0])
                    for comment_id in session['course_enquiry_ids']:

                        comment_info=models.execute_kw(self.db, uid, self.password, 'enquiries', 'search_read', [['&',['id' , '=' , comment_id],['pending','=',False]]], {'fields': ['replay_enquiry_ids','user_id','comment','enquiry_id','replay_enquiry_ids','image_path','create_date','image_ids']})
                        comments={}
                        rep={}
                        if comment_info !=[]:
                            comments['user_name']=comment_info[0]['user_id'][1]
                            comments['user_id']=comment_info[0]['user_id'][0]
                            comments['comment']=comment_info[0]['comment']
                            comments['id']=comment_info[0]['id']
                            comments['image_path']=comment_info[0]['image_path']
                            comments['create_date']=comment_info[0]['create_date']
                            comments['images']=[]
                            if comment_info[0]['image_ids']:
                                for image in comment_info[0]['image_ids']:
                                    image_info =models.execute_kw(self.db, uid, self.password, 'comment.images', 'search_read', [[['id' , '=' , image]]], {'fields': ['image_url']})
                                    comments['images'].append({
                                        'image' : image_info[0]['image_url']
                                    })
                            del comment_info[0]['image_ids']
                            
                            if len(comment_info[0]['replay_enquiry_ids'])>0:
                                reply=comment_info[0]['replay_enquiry_ids'][0]
                                reply_info=models.execute_kw(self.db, uid, self.password, 'replay_enquiry', 'search_read', [[['id' , '=' , reply]]], {'fields': ['image_path','user_id','comment','replay_id','status','comment_id','create_date','image_url1' ,'image_url2','image_url3','image_url4','image_url5' ]})
                                rep['user_name']=reply_info[0]['user_id'][1]
                                user_id=reply_info[0]['user_id'][0]
                                rep['id']=reply_info[0]['id']
                                rep['comment']=reply_info[0]['comment']
                                rep['image_path']=reply_info[0]['image_path']
                                rep['status']=reply_info[0]['status']
                                rep['create_date']=reply_info[0]['create_date']
                                if reply_info[0]['comment_id'] != False:
                                    rep['comment_id']=reply_info[0]['comment_id'][0]
                                    rep['comment_body']=reply_info[0]['comment_id'][1]
                                else:
                                    rep['comment_id']=''
                                    rep['comment_body']=''
                                user_type=models.execute_kw(self.db, uid, self.password, 'res.users', 'search_read', [[['id' , '=' , user_id]]], {'fields': ['user_type']})
                                rep['user_type']=user_type[0]['user_type']

                            comments['reply']=rep
                            Comments.append(comments)
                session['Comments']=Comments
                session['Comments'] = false2empty(self ,session['Comments'])

        try :
            del session_details[0]['course_enquiry_ids']
            del session_details[0]['quiz_ids']
        except :
            pass




        pending_comments=false2empty(self ,pending_comments)
        if pending_comments!=[] or Comments!=[]:
            response = json.dumps({"data":[{"Questions":Comments},{"Pending_Questions":pending_comments}],'message': 'التعليقات  والردور على الجلسة'})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json')]
        )
        else :
            response = json.dumps({"data":[],'message': 'لا يوجد أسئلة على الجلسة '})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json')]
        )





    @http.route('/get_student_rate',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_student_rate(self,course_id,**kw):
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        authe = request.httprequest.headers

        # body =json.loads(request.httprequest.data)
        try:
            token = authe['Authorization'].replace('Bearer ', '')

            dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])


        except Exception as e:
            response = json.dumps({ 'jsonrpc': '2.0', 'message': 'Unauthorized!'})
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

        rate=-1
        course_id=int(course_id)
        try:
            course_value =models.execute_kw(self.db, uid, self.password, 'course.result', 'search_read', [[['course_id' , '=' , course_id]]],{'fields':['course_result_id','result'], 'order': 'result desc'})
        except:
            response = json.dumps({ 'jsonrpc': '2.0', 'message': ' حدث خطأ'})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        if course_value==[]:
            response = json.dumps({ 'jsonrpc': '2.0', 'message': 'الكورس غير موجود'})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )

        for i in range(len(course_value)):
            if course_value[i]['course_result_id'][0]==user_id:
                rate=i
        if rate >-1:
            response = json.dumps({"data":{'rate':int(rate+1)},'message': 'ترتيب الطالب'})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        else :
            response = json.dumps({"data":{},'message': 'لا يوجد نتيجة متعلقة بهذا الطالب'})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )



    @http.route('/get_session_video',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_session_video(self,path=None,id=int,session_ids=None,**kw):
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        authe = request.httprequest.headers
        range_header = request.httprequest.headers.get('Range')
        token = int(id)
        
        try:
            authe = request.httprequest.headers
            token = authe['Authorization'].replace('Bearer ', '')
            
            dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
        except Exception as e:
            response = json.dumps({ 'jsonrpc': '2.0', 'message': 'Unauthorized!'})
            return Response(
            response, status=400,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        id = int(id)
        session_id = session_ids
        if session_id != None:
            session_id = int(session_id)
        user_id = int(dec_token['id'])
        if verfiy_token.verfiy_token (self,token,str(user_id)) ==False:

            response = json.dumps({ 'data': [], 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )

        session_video = models.execute_kw(self.db, uid, self.password, 'course.video', 'search_read', [[['id' , '=' , session_id]] ],{'fields': ['is_public']})
        is_subscribtion= models.execute_kw(self.db, uid, self.password, 'subscription', 'search_read', [['&',['status','=',True],['course_id','=',id],['user_id' , '=' , user_id]] ],{'fields': ['user_id','course_id']})
        if session_video != [] :
            is_public = session_video[0]['is_public']
        if is_subscribtion != [] or is_public == True:
            file_name = '/home/ubuntu/taleb_odoo16/talebodoo'+path
            # file_name = '/home/ali/taleb/custom/talebodoo'+path
            

            try:
                if range_header:
                    range_header = int(range_header)
                    start_byte = range_header 

                    with open(file_name, 'rb') as file:
                        blob = file.read()
                        size = len(blob)
                        file.seek(start_byte-1)
                        content = file.read(size - start_byte + 1)
                        content_type = 'resume-download'
                   

                    return Response(content)
                else:
                    isExist = os.path.isfile(file_name)
                    if isExist:
                        with open(file_name, 'rb') as infile:
                            blob = infile.read()
                            size = len(blob)
                        content_type = None
                        try:
                            return Response(blob,headers=[('Content-Type', 'application/json'), ('Content-Length', size)])
                        except:
                            response = json.dumps({ 'data': [], 'message': ' لايمكن الوصول الى الملف'})
                            return Response(
                            response, status=200,
                            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                                        )
                    else:
                        session_video= models.execute_kw(self.db, uid, self.password, 'course.video', 'search_read', [[['id','=',session_id]]],{'fields': ['video']})
                        if session_video != []:
                            video_update=request.env['course.video'].sudo().video_to_server(session_id , 'asdwwwsss')
                            time.sleep(7)
                            session_video_after_update= models.execute_kw(self.db, uid, self.password, 'course.video', 'search_read', [[['id','=',session_id]] ],{'fields': ['video_file_path']} )
                            file_name = '/home/ubuntu/taleb_odoo16/talebodoo'+video_update
                            try:
                                if range_header:
                                    range_header = int(range_header)
                                    start_byte = range_header # Your logic to parse the range header

                                    with open(file_name, 'rb') as file:
                                        blob = file.read()
                                        size = len(blob)
                                        file.seek(start_byte-1)
                                        content = file.read(size - start_byte + 1)
                                        content_type = 'resume-download'
                                    return Response(content)
                                else:
                                    with open(file_name, 'rb') as infile:
                                        blob = infile.read()
                                        size = len(blob)
                                    content_type = None
                                    try:
                                        content_type = blob.content_type
                                    except:
                                        pass
                                    return Response(blob,  mimetype=content_type,headers=[('Content-Type', 'application/json'), ('Content-Length', size)])

                            except Exception as e:
                                response = json.dumps({ 'data': [], 'message': ' لايمكن الوصول الى الملف ليس لديك اشتراك'})
                                return Response(
                                response, status=300,
                                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                                            )

                    

            except Exception as e:
                response = json.dumps({ 'data': [], 'message': str(e)})
                return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                            )
                session_video= models.execute_kw(self.db, uid, self.password, 'course.video', 'search_read', [[['id','=',session_id]]],{'fields': ['video']})
                if session_video != []:
                    self.run_code(session_id)
                    session_video_after_update= models.execute_kw(self.db, uid, self.password, 'course.video', 'search_read', [[['id','=',session_id]] ],{'fields': ['video_file_path']} )
                    file_name = '/home/ubuntu/taleb_odoo16/talebodoo'+session_video_after_update[0]['video_file_path']
                    try:
                        if range_header:
                            range_header = int(range_header)
                            start_byte = range_header # Your logic to parse the range header

                            with open(file_name, 'rb') as file:
                                blob = file.read()
                                size = len(blob)
                                file.seek(start_byte-1)
                                content = file.read(size - start_byte + 1)
                                content_type = 'resume-download'
                            return Response(content)
                        else:
                            with open(file_name, 'rb') as infile:
                                blob = infile.read()
                                size = len(blob)
                            content_type = None
                            try:
                                content_type = blob.content_type
                            except:
                                pass
                            return Response(blob,  mimetype=content_type,headers=[('Content-Type', 'application/json'), ('Content-Length', size)])

                    except Exception as e:
                        response = json.dumps({ 'data': [], 'message': ' لايمكن الوصول الى الملف ليس لديك اشتراك'})
                        return Response(
                        response, status=200,
                        headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                                    )
        else:
            response = json.dumps({ 'data': [], 'message': ' لايمكن الوصول الى الملف ليس لديك اشتراك'})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                        )




    @http.route('/get_promocode_details', cors="*", method=["GET"], auth="public", csrf=False)
    def get_course(self, **kw):
        data=[]

        if 'id' in kw:
            id = int(kw['id'])
            courses = request.env['courses'].sudo().search_read([('id','=',id)],fields=['id','cost'])

            if courses != []:
                old_cost = int(courses[0]['cost'])
                if 'code' in kw:
                    code = kw['code']
                    promo_code = request.env['promotion.code'].sudo().search_read([('promotion_code','=',code)],fields=['discount_percentage','is_valid','course_ids'])
                    print('promo_code >>>>>>>>>>>')
                    print(promo_code)
                    discount_percentage =int(promo_code[0]['discount_percentage'])
                    new_cost = old_cost - (old_cost * (discount_percentage/100))
                    if promo_code[0]['course_ids']:
                        if id not in promo_code[0]['course_ids']:
                            response = json.dumps({ 'data': [], 'message': 'هذا الكود غير صالح في هذا الكورس'})
                            return Response(
                            response, status=200,
                            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])
                        else:
                            response = json.dumps({ 'data': {'old_cost':old_cost,"new_cost":new_cost,'discount_percentage':discount_percentage}, 'message': 'تفاصيل الكود المدخل'})
                            return Response(
                            response, status=200,
                            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])
                    else:
                        response = json.dumps({ 'data': [], 'message': 'هذا الكود غير صالح في هذا الكورس'})
                        return Response(
                        response, status=200,
                        headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])
                else:
                    response = json.dumps({ 'data': [], 'message': 'يرجى إدخال الكود للتأكد من صلاحيته'})
                    return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])

            else:
                response = json.dumps({ 'data': [], 'message': 'معرف الكورس غير صالح'})
                return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                        )
        else:
            response = json.dumps({ 'data': [], 'message': 'يرجى إدخال معرف الكورس'})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                        )
    @http.route('/get_our_partner',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_our_partner(self, **kw):
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        partners=models.execute_kw(self.db, uid, self.password, 'our.partner', 'search_read', [[['id','!=',False]]], {
                                        'fields': ['name','image_path']})
        partners=false2empty(self,partners)

        if partners!=[]:
             response = json.dumps({'data':{'partners':partners},"message":"شركاؤنا "})

             return Response(
                 response,
                     status=200,
                    headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
                )

        else :
            response = json.dumps({"message":"لا يوجد بيانات " })
            return Response(
                 response,
                     status=200,
                    headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
                )
    @http.route('/get_video_rates',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_video_rates(self,id,page=int(1),**kw):
        page-int(page)
        authe = request.httprequest.headers
        try:
            token = authe['Authorization'].replace('Bearer ', '')
            dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])

        except Exception as e:

            user_rated=True
            response = json.dumps({"data":[],'message': 'لا يوجد تقييمات جلسات'})
            return Response(
            response, status=403,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        user_id = dec_token['id']
        login=dec_token['login']
        user_rated=False
        rate_rec=models.execute_kw(self.db, uid, self.password, 'video.rate', 'search_read', [[['video','=',int(id)]]], {
                                        'fields': ['video_rate_value']})


        rates_info=[]
        sum=0
        limit=7
        if rate_rec!=[]:
            if  len(rate_rec[0]['video_rate_value']):
                for rate in rate_rec[0]['video_rate_value']:
                    rate_value=models.execute_kw(self.db, uid, self.password, 'video_rate.value', 'search_read', [[['id','=',int(rate)]]], {
                                        'fields': ['rataing','image_path','comment','rate_id','user_id']})
                    del rate_value[0]['rate_id']
                    rate_value[0]['user_name']=rate_value[0]['user_id'][1]
                    rate_value[0]['user_id']=rate_value[0]['user_id'][0]

                    if len(rate_value[0]['comment'])>0 and rate_value[0]['user_id'] == user_id:
                            
                            rate_value[0]['user_rated'] = False
                            rates_info.append(rate_value[0])
                if rates_info==[]:

                    response = json.dumps({"message":"لا يوجد تقييمات للجلسة " })
                    return Response(
                 response,
                     status=200,
                    headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
                )

                rates_info=false2empty(self,rates_info)
                for r in rates_info:
                    sum=sum+float(r['rataing'])
                average=sum/len(rates_info)
                average=round(average, 1)

                response = json.dumps({'data':{'rate':average,'rates':rates_info},"message":"التقييمات على الجلسة "})

                return Response(
                 response,
                     status=200,
                    headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
                )
            else :

                response = json.dumps({"message":"لا يوجد تقييمات للجلسة " })
                return Response(
                 response,
                     status=200,
                    headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
                )
        else :

            response = json.dumps({"message":"لا يوجد تقييمات للجلسة " })
            return Response(
                 response,
                     status=200,
                    headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
                )
    @http.route('/get_packages',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_packages(self,**kw):

        
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        uid = common.authenticate(self.db, self.username, self.password, {})
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        packages= models.execute_kw(self.db, uid, self.password, 'packages', 'search_read', [[['id','!=',-1]]],{'fields': ['name','new_price','old_price','image_path','brief']})
        packages=false2empty(self,packages)
        if packages!=[]:

            response = json.dumps({'data':{'packages':packages},"message":"حزم الدورات"})

            return Response(
                 response,
                     status=200,
                    headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
                )


        else :
            response = json.dumps({'data':{'packages':[]},"message":"لم تتم أضافة حزم بعد"})

            return Response(
                 response,
                     status=200,
                    headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
                )

    @http.route('/get_package_details',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_package_details(self, package_id,**kw):
        package_id=int(package_id)
        is_subscribtion=False
        courses=[]
        authe = request.httprequest.headers
        try:
            token = authe['Authorization'].replace('Bearer ', '')
            dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])

        except Exception as e:
            common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
            models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
            uid = common.authenticate(self.db,self.username, self.password, {})
            #continue to get package details without token 
            package_details= models.execute_kw(self.db, uid, self.password, 'packages', 'search_read', [[['id','=',package_id]]],{'fields': ['package_courses','name','new_price','old_price','image_path','brief']})
            
            if package_details!=[]:
                if package_details[0]['package_courses']!=[]:
                    for course in package_details[0]['package_courses'] :
                        get_package=models.execute_kw(self.db, uid, self.password, 'package.courses', 'search_read', [[['id','=',course]]],{'fields': ['course_id','image_path','teacher_name','rate','cost','name','brief','number_of_rater']})
                        del get_package[0]['id']
                        get_package[0]['course_id']=get_package[0]['course_id'][0]

                        courses.append(get_package[0])
                package_details[0]['courses']=courses
                del package_details[0]['package_courses']

            else :
                response = json.dumps({ 'jsonrpc': '2.0', 'message': 'رقم الحزمة غير موجود'})
                return Response(
                response, status=404,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
            response = json.dumps({'data':{'package_info':package_details,'is_subscribtion':is_subscribtion},"message":" تفاصيل الحزمة  "})

            return Response(
                    response,
                        status=200,
                        headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
                )
            
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        uid = common.authenticate(self.db, self.username, self.password, {})
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        courses=[]
        user_id = dec_token['id']
        
        check_subs=models.execute_kw(self.db,uid, self.password, 'package_subscription_payments', 'search_read', [['&',['user_id', '=', user_id],['Package','=',package_id]]],{'fields': ['id','pyment_number','Package_payment_tracker_ids','number_of_payments']})
        if check_subs!=[]:
            is_subscribtion=True
            
            
        package_details= models.execute_kw(self.db, uid, self.password, 'packages', 'search_read', [[['id','=',package_id]]],{'fields': ['package_courses','name','new_price','old_price','image_path','brief']})
        if package_details!=[]:
            if package_details[0]['package_courses']!=[]:
                for course in package_details[0]['package_courses'] :
                    print("course")
                    print(course)
                    get_package=models.execute_kw(self.db, uid, self.password, 'package.courses', 'search_read', [[['id','=',course]]],{'fields': ['course_id','image_path','teacher_name','rate','cost','name','brief','number_of_rater']})
                    del get_package[0]['id']
                    get_package[0]['course_id']=get_package[0]['course_id'][0]

                    courses.append(get_package[0])
            package_details[0]['courses']=courses
            del package_details[0]['package_courses']

        else :
            response = json.dumps({ 'jsonrpc': '2.0', 'message': 'رقم الحزمة غير موجود'})
            return Response(
            response, status=404,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        response = json.dumps({'data':{'package_info':package_details,'is_subscribtion':is_subscribtion},"message":" تفاصيل الحزمة  "})

        return Response(
                 response,
                     status=200,
                    headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
               )
    @http.route('/get_package_coupon_discount',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_package_coupon_discount(self,code=None,package_id = None , **kw):

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
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        if package_id != None:
            package_id = int(package_id)
        if code == None:
            response = json.dumps({"data":[],'message': 'لا يوجد معلومات'})
            return Response(
            response, status=404,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        else:
            data =models.execute_kw(self.db, uid, self.password, 'package_promotion.code', 'search_read', [[['promotion_code' , '=', code]]] , {'fields': ['package_ids', 'discount_percentage','is_valid','user_id']})
            if data != [] and package_id in data[0]['package_ids'] and data[0]['is_valid'] == True:
                # data=models.execute_kw(self.db, uid, self.password, 'promotion.code', 'search_read', [[['package_promotion.code' , '=', code]]] , {'fields': ['course_ids', 'discount_percentage']})
                models.execute_kw(self.db, uid, self.password, 'promotion.code.user', 'create', [{'promotion_id': data[0]['user_id'][0], 'user_id': user_id }])
                response = json.dumps({"data":data[0],'message': 'معلومات الكوبون '})
                return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
            else:
                response = json.dumps({"data":[],'message': 'هذا الرمز غير فعال، ربما انتهت صلاحيته!'})
                return Response(
                response, status=404,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
    @http.route('/get_refrences',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_refrences(self,id= None, **kw):
        
        response = ''
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        if id == None:
            response = json.dumps({"data":[],'message': 'لا يوجد مراجع'})
            return Response(
            response, status=404,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        

        else:
            id=int(id)
            try :
                

                session_refrences = models.execute_kw(self.db, uid, self.password, 'course.video', 'search_read', [[['id' , '=' , id]]], {'fields': ['refrences']})
            except :
                
                response = json.dumps({"data":[],'message': 'معرف الجلسة غير صحيح '})
                return Response(
                response, status=404,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
                
            

            if len(session_refrences) > 0:
                refrences=[]
                for refrences_id in session_refrences[0]['refrences']:
                    refrenece_info=models.execute_kw(self.db, uid, self.password, 'refrences', 'search_read', [[['id' , '=' , int(refrences_id)]]], {'fields': ['refrence_name','content','file_path']})
                    refrences.append(refrenece_info[0])
                refrences=false2empty(self ,refrences)
                if refrences==[]:
                    
                    response = json.dumps({"data":[],'message': 'لا يوجد مراجع'})
                    return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
                else :       
                    response = json.dumps({"data":{'refrences':refrences},'message': 'مراجع الجلسة '})
                    return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )

            else:
                response = json.dumps({"data":[],'message': 'لا يوجد مراجع'})
                return Response(
                response, status=404,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
    
    @http.route('/get_platform_version',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_platform_version(self,platform_type= None, **kw):
        if platform_type != None:
            platform_id = request.env['platform.control'].sudo().search([('platform_type' , '=' ,platform_type)])
            if len(platform_id) != 0 :
                if platform_id.android_url == False:
                    platform_id.android_url = ''
                if platform_id.ios_url == False:
                    platform_id.ios_url = ''
                if platform_id.what_new == False:
                    platform_id.what_new = ''
                    
                response = json.dumps({"data":{"min" : platform_id.min_version, "max" : platform_id.max_version,'android_url' :platform_id.android_url , 'ios_url' :platform_id.ios_url,'what_new' : platform_id.what_new },'message': 'المعلومات الخاصة بلاتفورم'})
                return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
            else:
                response = json.dumps({"data":{"min" : "", "max" : ""},'message': 'المعلومات الخاصة بلاتفورم'})
                return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )

                


        else:
            response = json.dumps({"data":[],'message': 'يرجى تحديد نوع البلاتفورم'})
            return Response(
            response, status=400,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
