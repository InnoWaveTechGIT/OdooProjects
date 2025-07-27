from odoo import models,api, fields,_
import requests
import json
import logging
from odoo.exceptions import ValidationError
import os
import time
from datetime import datetime
import base64
from . import send_notification
import jwt
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import hashlib
import hashlib
from odoo import http
from Crypto.Util.Padding import pad, unpad
import re
import sys
import random
from odoo.http import request ,Response
import threading
import string
_logger = logging.getLogger(__name__)
def post_last_request(self, body, headers, values):
        url ='https://upload.dacast.com'
        files=[
            ('file',(values['video_file_name'],open(values["video_full_url"],'rb'),'application/octet-stream'))
        ]
        response = requests.request("POST",url,headers=headers, data=body, files=files)


def encrypt_filetest(self , key, input_file, output_file):
    cipher = AES.new(key, AES.MODE_CBC)
    output_file = output_file + '.enc'
    with open(input_file, 'rb') as file_in:
        with open(output_file, 'wb') as file_out:
            file_out.write(cipher.iv)
            while True:
                chunk = file_in.read(4096)
                if len(chunk) == 0:
                    break
                elif len(chunk) % 16 != 0:
                    chunk = pad(chunk, 16)
                file_out.write(cipher.encrypt(chunk))


def generate_random_string(length):
    # define the characters to use for the string (lowercase letters only)
    characters = string.ascii_lowercase
    
    # generate the random string
    random_string = ''.join(random.choice(characters) for i in range(length))
    
    return random_string



def encrypt_file(self,key, in_filename, out_filename=None, chunksize=64 * 1024):
    if not out_filename:
        out_filename = in_filename + '.encrypted'
    key = b'ali_ammar_1997@@'
    iv = hashlib.sha256(key).digest()[:AES.block_size]

    with open(in_filename, 'rb') as file_in:
        data = file_in.read()

    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphered_data = cipher.encrypt(pad(data, AES.block_size))
    encoded_data = base64.b64encode(ciphered_data) 
    try : 
        with open(out_filename, 'wb') as file_out:
            file_out.write(encoded_data)  # Write the varying length ciphertext to the file (this is the encrypted data)
            return True
    except Exception as e:
                        print('asdasdasd')
    
    
    
def _abs_rout(self,data):
    path1=''
    

    abs = os.path.dirname(os.path.abspath(__file__))
    abs_sp =abs.split("/")
    
    for i in abs_sp:
        if i !='models':
            path1 += i +'/'
    return path1


class CourseVideo(models.Model):
    _name = 'course.video'
    _description = "this module is for course.video"
    _rec_name = 'Title'

    _order='video_order'
    title=fields.Char(string="Video Name", index=True, required=True, translate=True)
    section_id = fields.Many2one('section' , string ='section' ,required = True,domain="[('course_id', '=', course_id)]")
    course_id = fields.Many2one('courses' , string='Course' ,required = True ,ondelete='cascade')
    course_enquiry_ids =fields.One2many('enquiries', 'enquiry_id', string='Enquiries')
    embeded_code = fields.Char(string='Embeded Code', readonly = True)
    dacast_id = fields.Char(string='Dacast id', readonly = True)
    quiz_ids = fields.One2many('video.quiz' , 'quiz_id' , string='Quiz IDs')
    duration = fields.Char(string='Duration', readonly = True)
    video = fields.Binary(string='Session',required = True)
    video_file_name = fields.Char("File Name", readonly = True)
    video_path = fields.Char(string="Video Url", readonly = True)
    video_full_url = fields.Char(string="Video Full Url", readonly = True)
    is_public = fields.Boolean(string= 'Is Public')
    video_cipher = fields.Text(string="Video Cipher")
    video_size = fields.Char(string="Video Size", readonly = True)
    video_file_full_url = fields.Char(string="Video File Full Url")
    video_file_path = fields.Char(string="Video File Url")
    script_code=fields.Char(string='Script Code', readonly = True)
    Title=fields.Char(string="Title")
    video_order=fields.Integer(string="Video order",required = True)
    refrences=fields.One2many('refrences' , 'session_id' , string='Refrences')
    active = fields.Boolean(default=True)
    script_code_flutter =fields.Char(string='Script Code Flutter', readonly = True)

    @api.model
    def create(self, vals):
        vals['title']=generate_random_string(10)
        module_path = ''
        course_name = self.env['courses'].search([('id', '=',vals["course_id"])])
        section_name = self.env['section'].search([('id', '=',vals["section_id"])])
        path = course_name.name + '/' + section_name.name
        # url = 'https://developer.dacast.com/v2/vod'
        # headers = {
        #     "accept": "application/json",
        #     "X-Format": "default",
        #     "content-type": "application/json",
        #     "X-Api-Key": "1682575625dKkmM5tM9uCY1K5Qa3wuVBP43PjcN8xg"
        # }       
        # payload = '''{
        #                 "source":"%s",
        #                 "upload_type": "ajax",
        #                 "callback_url":"https://admin.talebeduction.com/dacast_data"
        #             }''' %vals['title']
        # req = requests.post(url, headers=headers,data=payload)
        
        data=os.path.dirname(os.path.abspath(__file__))
        if "video_file_name" in vals and vals['video_file_name']!= False:
            
            if "video_file_name" in vals and "video" in vals and vals["video_file_name"] != False and vals["video"] != False:
                try:

                    time_stamp = str(time.time())
                    module_path = _abs_rout(self ,data)+"static/session_video"#loc
                    isExist = os.path.exists(module_path)
                    file_name =generate_random_string(10)
                    vals['video_file_name']=file_name
                    
                    if isExist == False:
                        os.mkdir(module_path)
                    
                    with open(os.path.join(module_path, time_stamp + vals["video_file_name"].replace(" ", "") + '.mp4'), "wb+") as f:
                        f.write(base64.b64decode(vals["video"]))
                except Exception as e:
                        print('asdasdasd')
                # blob = vals['video'].read() 
                size = len(vals['video']) 
                vals['video_size']=size/1024
                vals["video_file_path"] = module_path, time_stamp + vals["video_file_name"].replace(" ", "") + '.mp4'
                vals['video_full_url'] =  module_path +"/" + \
                time_stamp + vals["video_file_name"].replace(" ", "")
                vals["video_file_full_url"] = "/taleb/static/session_video/" + \
                time_stamp + vals["video_file_name"].replace(" ", "")+'.mp4'
                vals["video_path"] = "/taleb/static/session_video/" + \
                time_stamp + vals["video_file_name"].replace(" ", "")
                key = b'ali_ammar_1997@@'
                # encrypt_file(self ,key,vals["video_full_url"],vals["video_file_full_url"])
        values=super().create(vals)
        # for value in values:
        #         if value.course_id:
        #             subscription_ids = self.env['subscription'].search([('course_id', '=', value.course_id.id)])
        #             for subscription_id in subscription_ids:
        #                 if subscription_id :
        #                     subscription_id.write({
        #                         'purchased_sessions_ids': [(0, 0, {
        #                             'user_id': subscription_id.user_id.id, 
        #                             'session_id': value.id,
        #                             'course_id': value.course_id.id
        #                             }
        #                         )]
        #                     })

    #     url ='https://upload.dacast.com'
    #     body =json.loads(req.text)
    #     files=[
  	# ('file',(values['video_file_name'],open(values["video_full_url"],'rb'),'application/octet-stream'))
	# ]
    #     headers = {
    #         "accept": "application/json",
    #         "X-Format": "default",
            
    #         "X-Api-Key": "1682575625dKkmM5tM9uCY1K5Qa3wuVBP43PjcN8xg"
    #     }  

    #     response = requests.request("POST",url,headers=headers, data=body, files=files)
        
        # thread1 = threading.Thread(target=encrypt_file, args=(key,vals["video_full_url"],vals["video_file_full_url"]))
        # thread2 = threading.Thread(target=post_last_request, args=([],body, headers, values))
        # thread1.start()
        # thread2.start()
        # thread1.join()
        # thread2.join()
        os.unlink(values["video_full_url"])
        return values


    # def unlink(self):
        
  

    #     x= super(CourseVideo,self).unlink()
    #     for rec in self:
                
    #         url = "https://developer.dacast.com/v2/videos/a55408cb-262f-755f-f2b5-6c7311d8712b"

    #         headers = {
    #             "accept": "text/plain",
    #             "X-Format": "default",
    #             "X-Api-Key": "1682575625dKkmM5tM9uCY1K5Qa3wuVBP43PjcN8xg"
    #         }

    #         response = requests.delete(url, headers=headers)
    #     return x


    def write(self, vals):
       
        
        module_path = ''
        course_name = self.env['courses'].search([('id', '=',self.course_id.id)])
        section_name = self.env['section'].search([('id', '=',self.section_id.id)])
        path = course_name.name + '/' + section_name.name
        
        data=os.path.dirname(os.path.abspath(__file__))
        if "video_file_name" in vals and vals['video_file_name']!= False:
            
            if "video_file_name" in vals and vals["video_file_name"] != False:
                try:
                    isExist = os.path.exists(self.video_file_full_url)
                  
                    
                    if isExist == True:
                        os.unlink(self.video_file_full_url)
                    time_stamp = str(time.time())
                    module_path = _abs_rout(self ,data)+"static/session_video"#loc
                    isExist = os.path.exists(module_path)
                    vals['title']=generate_random_string(10)
                    file_name =vals['title']
                    vals['video_file_name']=file_name
                    # url = 'https://developer.dacast.com/v2/vod'
                    # headers = {
                    #     "accept": "application/json",
                    #     "X-Format": "default",
                    #     "content-type": "application/json",
                    #     "X-Api-Key": "1682575625dKkmM5tM9uCY1K5Qa3wuVBP43PjcN8xg"
                    # }       
                    # payload = '''{
                    #                 "source":"%s",
                    #                 "upload_type": "ajax",
                    #                 "callback_url":"https://admin.talebeduction.com/dacast_data"
                    #             }''' %vals['title']
                    # req = requests.post(url, headers=headers,data=payload)
        
                    if isExist == False:
                        os.mkdir(module_path)
                    
                    with open(os.path.join(module_path, time_stamp + vals["video_file_name"].replace(" ", "") + '.mp4'), "wb+") as f:
                        f.write(base64.b64decode(vals['video']))
                except Exception as e:
                        return e
                # blob = vals['video'].read() 
                size = len(self.video) 
                vals['video_size']=size/1024
                vals["video_file_path"] = "/taleb/static/session_video/" + \
                time_stamp + vals["video_file_name"].replace(" ", "")+'.mp4'
                vals['video_full_url'] =  module_path +"/" + \
                time_stamp + vals["video_file_name"].replace(" ", "")
                vals["video_file_full_url"] = module_path + '/' + \
                time_stamp +'.mp4'
                vals["video_path"] = "/taleb/static/session_video/" + \
                time_stamp + vals["video_file_name"].replace(" ", "")
                key = b'ali_ammar_1997@@'
                # encrypt_file(self ,key,vals["video_full_url"],vals["video_file_full_url"])
        
            #     url ='https://upload.dacast.com'
            #     body =json.loads(req.text)
            #     files=[
            # ('file',(vals['video_file_name'],open(vals["video_full_url"],'rb'),'application/octet-stream'))
            # ]
            #     headers = {
            #         "accept": "application/json",
            #         "X-Format": "default",
                    
            #         "X-Api-Key": "1682575625dKkmM5tM9uCY1K5Qa3wuVBP43PjcN8xg"
            #     }  

            #     response = requests.request("POST",url,headers=headers, data=body, files=files)
            #     vals['embeded_code'] = ''
            #     vals['script_code'] = ''
            #     vals['dacast_id'] = False
        # thread1 = threading.Thread(target=encrypt_file, args=(key,vals["video_full_url"],vals["video_file_full_url"]))
        # thread2 = threading.Thread(target=post_last_request, args=([],body, headers, values))
        # thread1.start()
        # thread2.start()
        # thread1.join()
        # thread2.join()
        values = super().write(vals)
        # if values :
        #     try:
        #         for value in self:
                    
        #             if value.course_id:
        #                 subscription_ids = self.env['subscription'].search([('course_id', '=', value.course_id.id)])
        #                 for subscription_id in subscription_ids:
        #                     # Check if user and session ID already exist
        #                     existing_purchase = self.env['purchased_sessions'].search([
        #                         ('user_id', '=', subscription_id.user_id.id),
        #                         ('session_id', '=', value.id),
        #                         ('course_id', '=', value.course_id.id)
        #                     ])
        #                     if existing_purchase:
        #                         continue  # Skip adding the line if it already exists
                            
        #                     # Add the line to purchased_sessions_ids
        #                     else:
        #                         subscription_id.write({
        #                         'purchased_sessions_ids': [(0, 0, {
        #                             'user_id': subscription_id.user_id.id, 
        #                             'session_id': value.id,
        #                             'course_id': value.course_id.id
        #                         })]
        #                     })
            # except Exception as e:
            #     pass
        return values
    
    def video_to_server(self):
        course_videos = self.env['course.video'].search([])
        try  :
            data=os.path.dirname(os.path.abspath(__file__))
            time_stamp = str(time.time())
            module_path = _abs_rout(self ,data)+"static/session_video"#loc
            isExist = os.path.exists(module_path)
            if isExist == False:
                os.mkdir(module_path)
            for course_video in course_videos:                
                with open(os.path.join(module_path, time_stamp + course_video.video_file_name), "wb+") as f:
                    f.write(base64.b64decode(course_video.video))
                course_video.video_file_path= "/taleb/static/session_video/" + \
                        time_stamp +course_video.video_file_name 
                course_video.video_file_full_url = module_path + '/' + \
                        time_stamp +course_video.video_file_name 
                key = b'ali_ammar_1997@@'
                course_video.video_full_url =  module_path +"/" + \
                        time_stamp + course_video.video_file_name
                return course_video.video_file_path
        except Exception as e:
                return str(e)
    # @api.constrains('dacast_id')
    # def get_empeded_cod(self):
    #     data = []
    #     url = "https://developer.dacast.com/v2/vod/%s/embed/iframe"%self.dacast_id
    #     url1="https://developer.dacast.com/v2/vod/%s/embed/javascript"%self.dacast_id

    #     payload={}
    #     headers = {
    #         "accept": "application/json",
    #         "X-Format": "default",
    #         "content-type": "application/json",
    #         "X-Api-Key": "1682575625dKkmM5tM9uCY1K5Qa3wuVBP43PjcN8xg"
    #     }     

    #     response = requests.request("GET", url, headers=headers, data=payload)
    #     data =json.loads(response.text)
    #     code = data['code']
    #     self.update({
    #         'embeded_code' : code
    #     })
    #     payload1={}
    #     response1=requests.request("GET",url1,headers=headers,data=payload1)
    #     data1 =json.loads(response1.text)
    #     script_code = data1['code']
    #     content_id_pattern = re.compile(r'contentId=([a-zA-Z0-9\-]+)')
    #     script_code=content_id_pattern.search(script_code)
    #     script_code=script_code.group(1)
        
    #     self.update({
    #         'script_code' : script_code
            
    #     })


    #     return True
    
    # def set_dacast_id(self):
        
    #     data=os.path.dirname(os.path.abspath(__file__))
    #     sessions = self.env['course.video'].search([('dacast_id', 'in',['',False])])
    #     for session in self:
                
    #             try:
    #                 time_stamp = str(time.time())
    #                 module_path = _abs_rout(self ,data)+"static/session_video"#loc
    #                 isExist = os.path.exists(module_path)
    #                 if isExist == False:
    #                     os.mkdir(module_path)
    #                 with open(os.path.join(module_path, time_stamp + session.video_file_name.replace(" ", "")), "wb+") as f:
    #                     f.write(base64.b64decode(session.video))
    #             except Exception as e:
    #                     return e
    #             size = len(session.video) 
    #             session.video_size=size/1024
    #             session.video_file_path = "/taleb/static/session_video/" + \
    #             time_stamp +'.mp4'
    #             session.video_full_url =  module_path +"/" + \
    #             time_stamp + session.video_file_name.replace(" ", "")
    #             session.video_file_full_url = module_path + '/' + \
    #             time_stamp +'.mp4'
    #             session.video_path = "/taleb/static/session_video/" + \
    #             time_stamp + session.video_file_name.replace(" ", "")
    #             key = b'ali_ammar_1997@@'
    #             encrypt_file(self ,key,session.video_full_url,session.video_file_full_url)
    #             url = 'https://developer.dacast.com/v2/vod'
    #             headers = {
    #                 "accept": "application/json",
    #                 "X-Format": "default",
    #                 "content-type": "application/json",
    #                 "X-Api-Key": "1682575625dKkmM5tM9uCY1K5Qa3wuVBP43PjcN8xg"
    #             }       
    #             payload = '''{
    #                             "source":"%s",
    #                             "upload_type": "ajax",
    #                             "callback_url":"https://admin.talebeduction.com/dacast_data"
    #                         }''' %session.title
    #             req = requests.post(url, headers=headers,data=payload)
    #             url ='https://upload.dacast.com'
    #             body =json.loads(req.text)
    #             files=[
    #         ('file',(session.video_file_name,open(session.video_full_url,'rb'),'application/octet-stream'))
    #         ]
    #             headers = {
    #                 "accept": "application/json",
    #                 "X-Format": "default",
                    
    #                 "X-Api-Key": "1682575625dKkmM5tM9uCY1K5Qa3wuVBP43PjcN8xg"
    #             }  

    #             response = requests.request("POST",url,headers=headers, data=body, files=files)
    #             session.update({
    #                 "embeded_code": "",
    #                 "script_code": "",
    #                 "dacast_id": False
    #             })
              
    # @api.depends('script_code')
    # def set_script_for_flutter(self):
    #     for rec in self :
    #         if rec.script_code:
    #             code = '''<!DOCTYPE html>
    #     <html><head>
    #         <meta  name="viewport" content="width=device-width", initial-scale="1.0">
    #         <script 
    #         id="dacast-script"
    #         src="https://player.dacast.com/js/player.js?contentId=%s" 
    #         type="application/javascript" async 
    #         class="dacast-video"></script></head><body>
            
    #         <script type="text/javascript">
    #             window.onload = start_player();
    #             function start_player () {
    #                 const datast_script = document.getElementById("dacast-script")
    #                 datast_script.onload = () => {

    #                     const myPlayer = window["dacast"]("%s", document.getElementById("dacast-video-player"));  
    #                 }
    #             }

    #         </script>
    #         <div id="dacast-video-player"></div>
    #     </body></html>

    #     ''' %rec.script_code
    #             rec.update({
    #                 'script_code_flutter' : code
                    
    #             })

            
    #     return True
#     def get_dacast_id(self):
#         try:

#             duration = 0.0
#             headers = {
#                 "accept": "application/json",
#                 "X-Format": "default",
#                 "content-type": "application/json",
#                 "X-Api-Key": "1682575625dKkmM5tM9uCY1K5Qa3wuVBP43PjcN8xg"
#             } 
            
#             for rec in self:
#                 course_name = self.env['courses'].search([('id', '=',rec.course_id['id'])])
#                 section_name = self.env['section'].search([('id', '=',rec.section_id['id'])])
#                 se =rec.title
#                 print('se '  , se)
#                 url= 'https://developer.dacast.com/v2/vod?title='+se
#                 print('url '  , url)
#                 response = requests.get(url, headers=headers )
#                 data =json.loads(response.text)
#                 print('data >>'  , data)
#                 if data['data']:
#                     if data['data'][0]:
#                         if data['data'][0]['id']:
#                             vid_id =data['data'][0]['id']
#                             vid_duration =data['data'][0]['duration']

#                             vid_duration =datetime.strptime(vid_duration, "%H:%M:%S")
#                             total_min = vid_duration.hour*60 + vid_duration.minute+ vid_duration.second/60   
#                             section_name.duration += total_min
#                             url1 ='https://developer.dacast.com/v2/vod/%s' % vid_id


#                             rec.duration = total_min
#                             rec.dacast_id = vid_id
                            
#                             course_duration = self.env['section'].search([('course_id', '=',rec.course_id['id'])])
#                             for i in course_duration :
#                                 duration += i.duration
#                             course_name.duration = duration
#                             folder_id = section_name.dacast_id
#                             payload = {"folder_ids": [folder_id]}
#                             response = requests.put(url1, json=payload ,headers=headers)
#         except Exception as e:
#             raise ValidationError(
#                 _('''
# يتم معالجة الفيديو على السيرفر 
#                   برجاء المحاولة لاحقا               
#                 '''))
#     @api.constrains('write_date')
#     def check_id_num(self):
#         for rec in self:
#             x = self.env['course.video'].search_count([('title', '=', rec.title)])
#             if x > 1:
#                 raise ValidationError(
#                     _('''هناك جلسة بنفس العنوان يرجى تغيير العنوان
#     :)
                    
#                     '''))
        

    

class EnquiryTaleb(models.Model):
    _name = 'enquiries'
    _description = "Course Video Comment"
    _rec_name = 'comment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    user_id = fields.Many2one('res.users' , string='User', default=lambda self: self.env.user.id , ondelete= 'cascade')
    course_id = fields.Many2one('courses',string='Course ',readonly = True)
    comment = fields.Text(string='Comment')
    enquiry_id = fields.Many2one('course.video' , string='Course Video')
    replay_enquiry_ids =fields.One2many('replay_enquiry', 'replay_id', string='Enquiries')
    image_path = fields.Char(related="course_id.image_path")
    teacher_id = fields.Integer()
    image__=fields.Binary(related='course_id.image')
    reports_ids =fields.One2many('denouncement', 'related_comment', string='denouncements')
    f_token = fields.Text(string='Fire Base Token')
    pending=fields.Boolean(default=True)
    active = fields.Boolean(default=True)
    image_ids = fields.One2many('comment.images' , 'comment_id' , string='Images')

    @api.constrains('replay_enquiry_ids')
    def set_teacher_id(self):
        for rec in self:
            if len(rec.replay_enquiry_ids) == 0:
                rec.pending = True

    @api.constrains('course_id')
    def set_teacher_id(self):
        for rec in self : 
            rec.update({
                'teacher_id' : rec.course_id.teacher_id.name.id})
        
    @api.model
    def create(self, vals):
        if "enquiry_id" in vals and vals['enquiry_id']!= False:
            session_id=self.env['course.video'].search([('id','=',vals['enquiry_id'])])
            token=self.env['user.token'].search([('user_id','=',vals['user_id'])])
            user_id=session_id.course_id['teacher_id']['name']['id']
            vals['course_id']=session_id.course_id['id']
            vals['f_token']=token.fire_base
        values =super().create(vals)
        todos = {   
        'res_id': values.id,    
        'res_model_id': self.env['ir.model'].sudo().search([('model', '=', 'enquiries')]).id,
        'user_id': user_id,
        'summary': 'New Comment Recieved now ',
        'note': '',
        'activity_type_id': 4,
        'date_deadline': datetime.today(),
        }   

        data=self.env['mail.activity'].sudo().create(todos)

        
        return values

    def write(self, vals):
        if "user_id" in vals and vals['user_id']!= False:
            token=self.env['user.token'].search([('user_id','=',vals['user_id'])])
            vals['f_token']=token.fire_base
        if "enquiry_id" in vals and vals['enquiry_id']!= False:
            
            session_id=self.env['course.video'].search([('id','=',vals['enquiry_id'])])

            vals['course_id']=session_id.course_id['id']

        values =super().write(vals)
        return values

class EnquiryTaleb(models.Model):
    # make notfication to commented user 
    _name = 'comment.images'
    _description = "this module is for testing purpose only, it was created by Eng Ali Ammar"

    comment_id = fields.Many2one('enquiries')
    image=fields.Binary(string='Image')
    image_url = fields.Char("image url", compute='_compute_image_url')

    @api.depends('image')
    def _compute_image_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        print('base_url' , base_url)
        for obj in self:
            if obj.image:
                obj.image_url= base_url + '/web/image?' + 'model=comment.images&id=' + str(obj.id) + '&field=image'
            else :
                obj.image_url= ''
class EnquiryTaleb(models.Model):
    # make notfication to commented user 
    _name = 'replay_enquiry'
    _description = "this module is for testing purpose only, it was created by Eng Ali Ammar"
    _rec_name = 'comment'

    user_id = fields.Many2one('res.users' , string='User', default=lambda self: self.env.user)
    comment = fields.Text(string='Comment' ,required=True)
    replay_id = fields.Many2one('enquiries' , string='Replay')
    image_path = fields.Char(related="user_id.image_path")
    status = fields.Selection(
        [('1', 'سؤال غير مفهوم'), ('2', 'سؤال تمت الإجابة عنه')], string="Status")
    comment_id = fields.Many2one('enquiries' , string='Old Comment')
    image_1 = fields.Binary('image one')
    image_2 = fields.Binary('image Two')
    image_3 = fields.Binary('image Three')
    image_4 = fields.Binary('image Four')
    image_5 = fields.Binary('image Five')
    image_url1 = fields.Char("image url", compute='_compute_image_url')
    image_url2 = fields.Char("image url", compute='_compute_image_url2')
    image_url3 = fields.Char("image url", compute='_compute_image_url3')
    image_url4 = fields.Char("image url", compute='_compute_image_url4')
    image_url5 = fields.Char("image url", compute='_compute_image_url5')

    @api.depends('image_1')
    def _compute_image_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        print('base_url' , base_url)
        for obj in self:
            if obj.image_1:
                obj.image_url1= base_url + '/web/image?' + 'model=replay_enquiry&id=' + str(obj.id) + '&field=image_1'
            else :
                obj.image_url1= ''
    @api.depends('image_2')
    def _compute_image_url2(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        print('base_url' , base_url)
        for obj in self:
            if obj.image_2:
                obj.image_url2= base_url + '/web/image?' + 'model=replay_enquiry&id=' + str(obj.id) + '&field=image_2'
            else :
                obj.image_url2= ''
    
    @api.depends('image_3')
    def _compute_image_url3(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        print('base_url' , base_url)
        for obj in self:
            if obj.image_3:
                obj.image_url3= base_url + '/web/image?' + 'model=replay_enquiry&id=' + str(obj.id) + '&field=image_3'
            else :
                obj.image_url3= ''
    
    @api.depends('image_4')
    def _compute_image_url4(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for obj in self:
            if obj.image_4:
                obj.image_url4= base_url + '/web/image?' + 'model=replay_enquiry&id=' + str(obj.id) + '&field=image_4'
            else :
                obj.image_url4= ''
    
    @api.depends('image_5')
    def _compute_image_url5(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        print('base_url' , base_url)
        for obj in self:
            if obj.image_5:
                obj.image_url5= base_url + '/web/image?' + 'model=replay_enquiry&id=' + str(obj.id) + '&field=image_5'
            else :
                obj.image_url5= ''
    @api.model
    def create(self, vals):

        if 'status' in vals and vals['status'] == '1':
            vals['comment']=  'سؤال غير مفهوم'

        if 'status' in vals and vals['status'] == '2':
            vals['comment']= 'سؤال تمت الإجابة عنه'

        values =super().create(vals)
        session_id=self.env['enquiries'].search([('id','=',vals['replay_id'])])
        
        
        if len(session_id.replay_enquiry_ids)>1:
            raise ValidationError("تم الأجابة على هذا السؤال مسبقا")
            
        
        session_id.pending=False
        dt = session_id.user_id
        
        user_type=self.env['res.users'].search([('id','=',self.env.user.id)])
        user_type=user_type.user_type
        
        if (user_type!='teacher'):
            raise ValidationError("يجب ان تسجل من حساب أستاذ لتتمكن من الأجابة")
            
        token =self.env['user.token'].sudo().search([('user_id','=',dt.id)])
        f_token = token.fire_base
        reply_id = values.id
        session_title = session_id.enquiry_id.Title
        comment_id = vals['replay_id']
        course_id =session_id.course_id['id']
        course=self.env['courses'].search([('id','=',int(course_id))])
        course_title=course.name
        video =session_id.enquiry_id['id']
        section=self.env['course.video'].search([('id','=',video)])
        comment_user=session_id.user_id['id']
        
        user_name =values.user_id['name']
        comment = values.comment
        session_id=session_id.enquiry_id.id
        title ='قام %s بالرد على تعليقك' %(user_name)
        payload = {
        "comment_id":comment_id,
        "session_id":session_id,
        "session_title" : session_title,
        "course_id":course_id,
        "reply_id":reply_id,
        'title' :title,
        'section_id':section.id,
        'course_title':course_title,

        "comment":comment,
        "notification_type":"Comment"
    }
        noti_data={
            'user_id':comment_user,
            'data':payload,
            'notification_type':"Comment"
        }
        self.env['notifications'].sudo().create(noti_data)
        send_notification.send_notification(self,f_token,payload)

        mail_activity = self.env['mail.activity'].sudo().search([('res_id' , '=' ,values.replay_id.id )])
        mail_activity.action_feedback(feedback="good job!")
        return values
    
    def write(self, vals):
        if 'status' in vals and vals['status'] == '1':
            vals['comment']=  'سؤال غير مفهوم'

        if 'status' in vals and vals['status'] == '2':
            vals['comment']= 'سؤال تمت الإجابة عنه'

        values =super().write(vals)
        return values