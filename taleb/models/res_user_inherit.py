from odoo import models,api, fields,_
from odoo.exceptions import ValidationError
import re
import os
import time
import base64
def _abs_rout(self,data):
    path1=''
    abs = os.path.dirname(os.path.abspath(__file__))
    abs_sp =abs.split("/")
    for i in abs_sp:
        if i !='models':
            path1 += i +'/'
    return path1
class UserInherit(models.Model):
    _inherit = 'res.users'

    
    father_name = fields.Char(string='Father name')
    country_id = fields.Many2one('res.country' , string = 'Country')
    calling_code = fields.Integer(related='country_id.phone_code')
    state_id = fields.Many2one('res.country.state', string="State", domain="[('country_id', '=', country_id)]")
    location_id = fields.Many2one('location', string="Location", domain="[('location_id', '=', state_id)]")
    is_active = fields.Boolean(string="Is Active")
    email_is_active = fields.Boolean(string="Email Is Active")
    email= fields.Char(string='Father name')
    points = fields.Integer(string ='Points')
    subscription_ids = fields.One2many('subscription','user_id',string="Subscription")
    phone = fields.Char(string='phone')
    personal_image = fields.Binary(string='Image')
    image_file_name = fields.Char("File Name")
    image_path = fields.Char(string="Image Url",default='')
    image_full_url = fields.Char(string="Image Full Url")
    user_type= fields.Selection(
        [('student', 'Student'), ('teacher', 'Teacher'),('promoter','Promoter')], string="User Type")
    courses_results_ids = fields.One2many('course.result' , 'course_result_id' , string='Course Result')
    student_id=fields.Integer(string="student_id")
    student_class_id=fields.Many2one('student.class',string="صف الطالب")
    student_course_ids= fields.Many2many('courses', string="مواد الطالب", compute="compute_student_courses")
    
    @api.depends('student_class_id', 'user_type')
    def compute_student_courses(self):
        for rec in self:
            if rec.user_type != 'student':
                rec.student_course_ids = None
            else:
                if 'تاسع' in rec.student_class_id.name:
                    rec.student_course_ids = self.env['courses'].search([('subject_class', '=', 'تاسع')])
                if 'علمي' in rec.student_class_id.name:
                    rec.student_course_ids = self.env['courses'].search([('subject_class', '=', 'بكلوريا علمي')])
                if 'أدبي' in rec.student_class_id.name:
                    rec.student_course_ids = self.env['courses'].search([('subject_class', '=', 'بكلوريا أدبي')])
                    

# cron action
    @api.model
    def set_student_class_level_scheduled_action(self):
        user_ids = self.env['res.users'].sudo().search([])
        for user_id in user_ids:
            subscription_ids = self.env['subscription'].sudo().search([('user_id', '=', user_id.id)])
            ninth_grade = 0
            twelveth_grade = 0
            if subscription_ids:
                for subscription_id in subscription_ids:
                    if subscription_id.course_id.subject_class == 'تاسع':
                        ninth_grade += 1
                    else:
                        twelveth_grade += 1
            else:
                session_status_ids = self.env['session_status'].sudo().search([('user_id', '=', user_id.id)])
                for session_status_id in session_status_ids:
                    if session_status_id.course_name.subject_class == 'تاسع':
                        ninth_grade += 1
                    else:
                        twelveth_grade += 1

            if ninth_grade > 0 or twelveth_grade > 0:
                if ninth_grade > twelveth_grade:
                    user_id.sudo().write({'student_class_id': 1})
                elif ninth_grade < twelveth_grade:
                    user_id.sudo().write({'student_class_id': 2})

    @api.constrains('email')
    def check_email_taleb(self):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        # pass the regular expression
        # and the string into the fullmatch() method
        if(re.fullmatch(regex, self.email)):
           pass
        else:
             raise ValidationError(_('email is not valid'))
        return True
    
    @api.constrains('active')
    def archive_files(self):
        print('self.active >>>>>>>>>>>',self.active)
        subscribtions = self.env['subscription'].search(['&' , ('active' ,'!=',self.active),('user_id' , '=' ,self.id)])
        for subscribtion in subscribtions:
            subscribtion.active = self.active
        enquiries = self.env['enquiries'].search(['&' , ('active' ,'!=',self.active),('user_id' , '=' ,self.id)])
        for enquirie in enquiries:
            enquirie.active = self.active
        rates =  self.env['rate.value'].search(['&' , ('active' ,'!=',self.active),('user_id' , '=' ,self.id)])
        for rate in rates:
            rate.active = self.active
        video_rates =  self.env['video_rate.value'].search(['&' , ('active' ,'!=',self.active),('user_id' , '=' ,self.id)])
        for video_rate in video_rates:
            video_rate.active = self.active
        teacher_rates =  self.env['teacher.value'].search(['&' , ('active' ,'!=',self.active),('user_id' , '=' ,self.id)])
        for teacher_rate in teacher_rates:
            teacher_rate.active = self.active
        
        session_statuss =  self.env['session_status'].search(['&' , ('active' ,'!=',self.active),('user_id' , '=' ,self.id)])
        for session_status in session_statuss:
            session_status.active = self.active
        courses_status =  self.env['course_status'].search(['&' , ('active' ,'!=',self.active),('user_id' , '=' ,self.id)])
        for course_status in courses_status:
            course_status.active = self.active
        sections_status =  self.env['section_status'].search(['&' , ('active' ,'!=',self.active),('user_id' , '=' ,self.id)])
        for section_status in sections_status:
            section_status.active = self.active
        
        
        
        
    

    @api.model
    def create(self, vals):
        
        data = os.path.dirname(os.path.abspath(__file__))
        if "image_file_name" in vals and vals['image_file_name']!= False:
            if "image_file_name" in vals and "personal_image" in vals and vals["image_file_name"] != False and vals["personal_image"] != False:
                try:

                    time_stamp = str(time.time())
                    module_path = _abs_rout(self ,data)+"static/personal_images"#loc
          
                    isExist = os.path.exists(module_path)
                    if isExist == False:
                        os.mkdir(module_path)
                    # module_path = "/home/vps112/odoo_16/torbetodoo/torbet_app/static/personal_images" #servar
                    with open(os.path.join(module_path, time_stamp + vals["image_file_name"].replace(" ", "")), "wb+") as f:
                        f.write(base64.b64decode(vals["personal_image"]))
                except Exception as e:
                        print('asdasdasd')

                vals["image_full_url"] = module_path + '/' + \
                time_stamp + vals["image_file_name"].replace(" ", "")
                vals["image_path"] = "/taleb/static/personal_images/" + \
                time_stamp + vals["image_file_name"].replace(" ", "")
                # print("4444444444 ")
        else :
            if vals['user_type']=='teacher':
                
                vals['image_path']='/taleb/static/default/teacher.png'
            elif vals['user_type']=='student':
                
                vals['image_path']='/taleb/static/default/student.png'
                
            
        values=super().create(vals)
      
        if values.user_type == 'teacher':
           
            value = {
            'name':values.id,
            }
       
            self.env['teacher'].create(value)
        if values.user_type == 'promoter':
        
            value = {
            'name':values.id,
            }

            self.env['promoters'].create(value)
        return values

        
        
    def write(self, vals):
        module_path= ''
     
        time_stamp = str(time.time())
        data = os.path.dirname(os.path.abspath(__file__))
        mod =_abs_rout(self ,data)
      

        if "image_file_name" in vals and "personal_image" in vals and vals["image_file_name"] != False and vals["personal_image"] != False:
            try:
                print('self.image_full_url')
                print(self.image_full_url)

                old_image = self.image_full_url
                if old_image:
                    if os.path.exists(old_image):
                        os.unlink(old_image)


                    

                if vals["image_file_name"] == "" and vals['personal_image'] == "" :
                    vals["image_full_url"] = ""
                    vals["image_path"] = ''
                    super().write(vals)
                    return True

                # module_path = "/home/vps112/odoo_16/torbetodoo/torbet_app/static/personal_images"#server
                module_path = mod +"static/personal_images"#loc
                isExist = os.path.exists(module_path)
             
                if isExist == False:
                    os.mkdir(module_path)

                    
                with open(os.path.join(module_path, time_stamp + vals["image_file_name"].replace(" ", "")), "wb+") as f:
                    f.write(base64.b64decode(vals["personal_image"]))
              

            except Exception as e:
                pass
            vals["image_full_url"] = module_path + '/' + \
            time_stamp + vals["image_file_name"].replace(" ", "")

            vals["image_path"] = "/taleb/static/personal_images/" + \
            time_stamp + vals["image_file_name"].replace(" ", "")

      

        # print(vals)
        super().write(vals)
        # print('pvcdsvdr')

        return True
    def unlink(self):    
        for rec in self: 
                 
            if rec.id != 107: 
                x= super(UserInherit,rec).unlink() 
            else: 
                 raise ValidationError( 
                _('''You can't delete this account!!''')) 
        return x
    
    
    
class BlockStudent(models.Model):
    _name = 'block.student'
    _description = "this module is for block or unblock student "
    user_id = fields.Many2one('res.users' , string='User')
    block=fields.Boolean(string="Block")
   