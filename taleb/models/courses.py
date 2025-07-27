from odoo import models,api, fields,_
from odoo.exceptions import ValidationError
from datetime import datetime ,date,timedelta
import re
import os
import time
import base64
import requests
import json
from dateutil.relativedelta import relativedelta

def _abs_rout(self,data):
        path1=''

        abs = os.path.dirname(os.path.abspath(__file__))
        abs_sp =abs.split("/")
        for i in abs_sp:
            if i !='models':
                path1 += i +'/'
        return path1


class CoursesTaleb(models.Model):
    _name = 'courses'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "this module is for courses"
    _order = 'course_number asc'
    
    _log_access = True
    name = fields.Char(string='Course Name',required = True,track_visibility='always')
    is_publish =fields.Boolean(string='Is Publish')
    brief = fields.Char(string='Brief ')
    teacher_id = fields.Many2one('teacher',string='Teacher',ondelete='cascade',required = True)
    teacher_name = fields.Char(related = 'teacher_id.teacher_name',string='Teacher Name')
    rate = fields.Float(string='Rate',default=5)
    number_of_rater = fields.Integer(string='Number Of Raters')
    date_of_create =fields.Date(string='Create Date')
    about_this_course =fields.Text(string='About This Course',required = True)
    skills_id = fields.Many2many('skills',string='Skills To Earn')
    course_sections_ids =fields.One2many('section', 'course_id', string='Sections')
    cost = fields.Integer(string='Cost',required = True)
    # cost2 = fields.Integer(string='Installment Cost 2',required = True)
    # cost4 = fields.Integer(string='Installment Cost 4',required = True)
    # cost5= fields.Integer(string='Installment Cost 5',required = True)
    expiration_month = fields.Integer(string='Expiration')
    number_of_student = fields.Integer(string='Number Of Student',default=0,readonly = True)
    subject_class = fields.Selection(
        [('تاسع', 'تاسع'), ('بكلوريا علمي', 'بكلوريا علمي '), ('بكلوريا أدبي', 'بكلوريا أدبي')], string="Subject Class",required = True) 
    image = fields.Binary(string='Image',required = True)
    image_file_name = fields.Char("Image File Name")
    active = fields.Boolean(default=True)
    image_path = fields.Char(string="Image Url")
    course_image_full_url = fields.Char(string="Image Full Url")
    dacast_id =fields.Char(string= 'Dacast ID')
    course_length = fields.Char(string= 'Course Length')
    duration = fields.Float(string='Duration')
    packages=fields.One2many('package.courses','course_id' , string = 'Packages')
    course_number=fields.Integer(string='Course Number', required=True)
    session_status_ids = fields.One2many('session_status', 'course_name')
    
    
    # @api.depends('course_sections_ids.session_ids.usercourseprogress_ids.progress')
    # def _compute_total_progress(self):
    #     for record in self:
    #         record.total_progress = sum(section.session_ids.mapped('usercourseprogress_ids.progress') for section in record.section_ids)

    # total_progress = fields.Float(compute='_compute_total_progress', string="Total Progress")
    
    
    # @api.constrains('name')
    # def change_name(self):
    #    for rec in self :
    #         print('rec >>>>' , rec)
    #         now = datetime.now()

    #         # Subtract two minutes from the current time
    #         two_minutes_ago = now - timedelta(minutes=2)
    #         if rec.write_date > two_minutes_ago:
    #             vid_id = rec.dacast_id
    #             url = "https://developer.dacast.com/v2/folder/%s" % vid_id
    #             payload = {
    #                 "name":rec.name,
    #                 "parent_id":""
    #             }
    #             headers = {
    #                 "accept": "application/json",
    #                 "X-Format": "default",
    #                 "content-type": "application/json",
    #                 "X-Api-Key": "1682575625dKkmM5tM9uCY1K5Qa3wuVBP43PjcN8xg"
    #             }

    #             response = requests.put(url, json=payload , headers=headers)
    #             print(response.text)
    # @api.model
    # def create(self, vals):
        
    #     print('self.skills_id' , self.skills_id)
    #     print('self.skills_id' , len(self.skills_id))
    #     data = os.path.dirname(os.path.abspath(__file__))

    #     if "teacher_id" in vals:
    #         teacher_data = self.env['teacher'].search([('id' , '=' , vals['teacher_id'])])
    #         teacher_data.number_of_courses += 1
    #     if "name" in vals :
    #         url = "https://developer.dacast.com/v2/folder"
    #         payload = {"full_path": vals["name"]}
    #         headers = {
    #             "accept": "application/json",
    #             "X-Format": "default",
    #             "content-type": "application/json",
    #             "X-Api-Key": "1682575625dKkmM5tM9uCY1K5Qa3wuVBP43PjcN8xg"
    #         }

    #         response = requests.post(url, json=payload, headers=headers)
            
         
    #         data = json.loads(response.text)
           
    #         vals['dacast_id'] = data['id']
    #     if "image_file_name" in vals and vals['image_file_name']!= False:
    #         if "image_file_name" in vals and "image" in vals and vals["image_file_name"] != False and vals["image"] != False:
    #             try:

    #                 time_stamp = str(time.time())
    #                 module_path = _abs_rout(self ,data)+"static/course_image"#loc
                   
    #                 isExist = os.path.exists(module_path)
                   
    #                 if isExist == False:
    #                     os.mkdir(module_path)
    #                 # module_path = "/home/vps112/odoo_16/torbetodoo/torbet_app/static/course_image" #servar
    #                 with open(os.path.join(module_path, time_stamp + vals["image_file_name"].replace(" ", "")), "wb+") as f:
    #                     f.write(base64.b64decode(vals["image"]))
    #             except Exception as e:
    #                 pass

    #             vals["course_image_full_url"] = module_path + '/' + \
    #             time_stamp + vals["image_file_name"].replace(" ", "")
    #             vals["image_path"] = "/taleb/static/course_image/" + \
    #             time_stamp + vals["image_file_name"].replace(" ", "")
    #             # print("4444444444 ")
    #     values=super().create(vals)  
    #     values.message_subscribe(partner_ids=[self.env.user.partner_id.id])  
    #     print('self.skills_id' , values.skills_id)
    #     print('values.skills_id' , len(values.skills_id))
    #     return values
        
    # def write(self, vals):
    #     if "teacher_id" in vals:
    #         teacher_data = self.env['teacher'].search([('id' , '=' , vals['teacher_id'])])
    #         teacher_data.number_of_courses += 1



       
    #     data = os.path.dirname(os.path.abspath(__file__))
    #     mod =_abs_rout(self ,data)
    #     module_path=''
    #     time_stamp=''
      
      
    #     if "image_file_name" in vals and "image" in vals and vals["image_file_name"] != False and vals["image"] != False:
    #         try:
            

    #             old_image = self.course_image_full_url
    #             if old_image:
    #                 if os.path.exists(old_image):
    #                     os.unlink(old_image)


    #                 time_stamp = str(time.time())

    #             if vals["image_file_name"] == "" and vals['image'] == "" :
    #                 vals["course_image_full_url"] = ""
    #                 vals["image_path"] = ''
    #                 super().write(vals)
    #                 return True

    #             # module_path = "/home/vps112/odoo_16/torbetodoo/torbet_app/static/course_image"#server
    #             module_path = mod +"static/course_image"#loc
    #             isExist = os.path.exists(module_path)
               
    #             if isExist == False:
    #                 os.mkdir(module_path)
    #             with open(os.path.join(module_path, time_stamp + vals["image_file_name"].replace(" ", "")), "wb+") as f:
    #                 f.write(base64.b64decode(vals["image"]))

    #         except Exception as e:
    #             pass
    #         vals["course_image_full_url"] = module_path + '/' + \
    #         time_stamp + vals["image_file_name"].replace(" ", "")

    #         vals["image_path"] = "/taleb/static/course_image/" + \
    #         time_stamp + vals["image_file_name"].replace(" ", "")

           

    #     # print(vals)
    #     super().write(vals)
    #     # print('pvcdsvdr')

    #     return True
class SectionQuize(models.Model):
    _name="section_quize"
    _description=" model describe the tests for section "
    name = fields.Char()
    pdf_file = fields.Binary(string="PDF File")
    course_id = fields.Many2one('courses' , string='Course' ,required = True ,ondelete='cascade')
    section_id = fields.Many2one('section' , string ='section' ,required = True,domain="[('course_id', '=', course_id)]")
    file_path = fields.Char(string="File Url", readonly = True)
    file_full_url = fields.Char(string="File Full Url", readonly = True)
    file_name = fields.Char("File Name", readonly = True)
    correction_file=fields.Binary(string=" Correction PDF File")
    correction_file_path=fields.Char(string=" Correction File Url", readonly = True)
    correction_file_full_url=fields.Char(string=" Correction File Full Url", readonly = True)
    correction_file_name=fields.Char(string=" Correction File Name", readonly = True)
    
    
    correct=fields.Char(string="Ff Url", readonly = True)
    @api.constrains('pdf_file')
    def _check_is_pdf(self):
        for rec in self:
            if rec.pdf_file:
                file_name, file_extension = os.path.splitext(rec.file_name)
                if file_extension.lower() != '.pdf':
                    raise ValidationError("File must be a PDF file.")
    
    @api.constrains('section_id')
    def check_unique_section(self):
        for record in self:
            record.validate_section()
    def validate_section(self):
        rec_number=self.env['section_quize'].search_count([('section_id', '=',self.section_id.id)])
        if rec_number>1:
            raise ValidationError(_("quize for this course already exist "))
    
    
    @api.model
    def create(self, vals):
        module_path = ''
        section_id=self.env['section'].search([('id','=',vals['section_id'])])
        course_name=section_id.course_id.name+'/'+section_id.name
        path=course_name
        data=os.path.dirname(os.path.abspath(__file__))
        if "file_name" in vals and vals['file_name']!= False:
            if "file_name" in vals and "pdf_file" in vals and vals["file_name"] != False and vals["pdf_file"] != False:
                
                try:

                    time_stamp = str(time.time())
                    module_path = _abs_rout(self ,data)+"static/section_quize"#loc
                    isExist = os.path.exists(module_path)
                    if isExist == False:
                        os.mkdir(module_path)
                 
                    with open(os.path.join(module_path, time_stamp  + vals["file_name"].replace(" ", "")), "wb+") as f:
                        f.write(base64.b64decode(vals["pdf_file"]))
                except Exception as e:
                        pass
                vals["file_full_url"] = module_path + '/' + \
                time_stamp + vals["file_name"].replace(" ", "")
                vals["file_path"] = "/taleb/static/section_quize/" + \
                time_stamp + vals["file_name"].replace(" ", "")
        if "correction_file_name" in vals and vals['correction_file_name']!= False:
            
            
            if "correction_file_name" in vals and "correction_file" in vals and vals["correction_file_name"] != False and vals["correction_file"] != False:
                
                try:

                    time_stamp = str(time.time())
                    module_path = _abs_rout(self ,data)+"static/correction_section_quize"#loc
                    isExist = os.path.exists(module_path)
                    if isExist == False:
                        os.mkdir(module_path)
                 
                    with open(os.path.join(module_path, time_stamp  + vals["correction_file_name"].replace(" ", "")), "wb+") as f:
                        f.write(base64.b64decode(vals["correction_file"]))
                except Exception as e:
                        pass

                vals["correction_file_full_url"] = module_path + '/' + \
                time_stamp + vals["correction_file_name"].replace(" ", "")
                vals["correction_file_path"] = "/taleb/static/correction_section_quize/" + \
                time_stamp + vals["correction_file_name"].replace(" ", "")
        values=super().create(vals)
        return values
    def write(self, vals):
        
        data = os.path.dirname(os.path.abspath(__file__))
        mod =_abs_rout(self ,data)
        module_path=''
        time_stamp=''
        if "file_name" in vals and "pdf_file" in vals and vals["file_name"] != False and vals["pdf_file"] != False:
            try:
                
                old_section = self.file_full_url
                if old_section:
                    if os.path.exists(old_section):
                        os.unlink(old_section)


                    time_stamp = str(time.time())

                if vals["file_name"] == "" and vals['pdf_file'] == "" :
                        vals["file_full_url"] = ""
                        vals["file_path"] = ''
                        super().write(vals)
                        return True

                    # 
                module_path = mod +"static/section_quize"#loc
                isExist = os.path.exists(module_path)
                    
                if isExist == False:
                    os.mkdir(module_path)
                with open(os.path.join(module_path, time_stamp + vals["file_name"].replace(" ", "")), "wb+") as f:
                        f.write(base64.b64decode(vals["pdf_file"]))    
                    

            except Exception as e:
                    print("There was an error saving the binary file: ", str(e))
            vals["file_full_url"] = module_path + '/' + \
                time_stamp + vals["file_name"].replace(" ", "")

            vals["file_path"] = "/taleb/static/section_quize/" + \
                time_stamp + vals["file_name"].replace(" ", "")
            
        if "correction_file_name" in vals and "correction_file" in vals and vals["correction_file_name"] != False and vals["correction_file"] != False:
            try:
                
                old_section = self.file_full_url
                if old_section:
                    if os.path.exists(old_section):
                        os.unlink(old_section)


                    time_stamp = str(time.time())

                if vals["correction_file_name"] == "" and vals['correction_file'] == "" :
                        vals["correction_file_full_url"] = ""
                        vals["correction_file_path"] = ''
                        super().write(vals)
                        return True

                    # 
                module_path = mod +"static/correction_section_quize"#loc
                isExist = os.path.exists(module_path)
                    
                if isExist == False:
                    os.mkdir(module_path)
                with open(os.path.join(module_path, time_stamp + vals["correction_file_name"].replace(" ", "")), "wb+") as f:
                        f.write(base64.b64decode(vals["correction_file"]))    
                    

            except Exception as e:
                    pass
            vals["correction_file_full_url"] = module_path + '/' + \
                time_stamp + vals["correction_file_name"].replace(" ", "")

            vals["correction_file_path"] = "/taleb/static/section_quize/" + \
                time_stamp + vals["correction_file_name"].replace(" ", "")



            # print(vals)
        values=super().write(vals)
            # print('pvcdsvdr')

        return values
        
    def unlink(self):
        
        old_section = self.file_full_url
        if old_section:
            
            if os.path.exists(old_section):
                    os.unlink(old_section)
       
        x=super(SectionQuize,self).unlink()
        return x  
            
           
            
            
    
        

            
           