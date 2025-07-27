from odoo import models,api, fields,_
from odoo.exceptions import ValidationError
import re
import os
import time
import base64
import requests
import json
from odoo.exceptions import UserError
from . import send_notification
def _abs_rout(self,data):
    path1=''

    abs = os.path.dirname(os.path.abspath(__file__))
    abs_sp =abs.split("/")
    for i in abs_sp:
        if i !='models':
            path1 += i +'/'
    return path1
class Packages(models.Model):
    
    _name='packages'
    _description='this model for define a package of courses'
    package_courses=fields.One2many('package.courses','package_id' , string = 'Courses')
    name = fields.Char(string='Package Name',required=True)
    old_price=fields.Float(string='Old price')
    new_price=fields.Float(string='New Price')
    image = fields.Binary(string='Image',required = True)
    image_file_name = fields.Char("Image File Name" )
    image_path = fields.Char(string="Image Path" )
    image_full_url = fields.Char(string="Image Full Url")
    brief = fields.Char(string='brife') 
    cost2=fields.Integer(string='cost2')
    cost4 = fields.Integer(string='Cost 4',required = True)
    cost5=fields.Integer(string='cost5')
    active = fields.Boolean(default=True)
    
    expiration_month = fields.Integer(string='Expiration')
    subject_class = fields.Selection(
        [('تاسع', 'تاسع'), ('بكلوريا علمي', 'بكلوريا علمي '), ('بكلورياxc أدبي', 'بكلوريا أدبي')], string="Subject Class",required = True)
    
    
    @api.model
    def create(self, vals):
        data = os.path.dirname(os.path.abspath(__file__))

        if "image_file_name" in vals and vals['image_file_name']!= False:
            if "image_file_name" in vals and "image" in vals and vals["image_file_name"] != False and vals["image"] != False:
                try:

                    time_stamp = str(time.time())
                    module_path = _abs_rout(self ,data)+"static/package_images"#loc
                   
                    isExist = os.path.exists(module_path)
                   
                    if isExist == False:
                        os.mkdir(module_path)
                    # module_path = "/home/vps112/odoo_16/torbetodoo/torbet_app/static/course_image" #servar
                    with open(os.path.join(module_path, time_stamp + vals["image_file_name"].replace(" ", "")), "wb+") as f:
                        f.write(base64.b64decode(vals["image"]))
                except Exception as e:
                        pass
                vals["image_full_url"] = module_path + '/' + \
                time_stamp + vals["image_file_name"].replace(" ", "")
                vals["image_path"] = "/taleb/static/package_images/" + \
                time_stamp + vals["image_file_name"].replace(" ", "")
        values=super().create(vals)        
        return values
        
    def write(self, vals):
        data = os.path.dirname(os.path.abspath(__file__))
        mod =_abs_rout(self ,data)
        module_path=''
        time_stamp=''
      
        time_stamp = str(time.time())
        if "image_file_name" in vals and "image" in vals and vals["image_file_name"] != False and vals["image"] != False:
            try:
            

                old_image = self.image_full_url
                if old_image:
                    if os.path.exists(old_image):
                        os.unlink(old_image)

                if vals["image_file_name"] == "" and vals['image'] == "" :
                    vals["image_full_url"] = ""
                    vals["image_path"] = ''
                    super().write(vals)
                    return True

                # module_path = "/home/vps112/odoo_16/torbetodoo/torbet_app/static/course_image"#server
                module_path = mod +"static/package_images"#loc
                isExist = os.path.exists(module_path)
               
                if isExist == False:
                    os.mkdir(module_path)
                with open(os.path.join(module_path, time_stamp + vals["image_file_name"].replace(" ", "")), "wb+") as f:
                    f.write(base64.b64decode(vals["image"]))

            except Exception as e:
                print("There was an error saving the binary file: ", str(e))
            vals["image_full_url"] = module_path + '/' + \
            time_stamp + vals["image_file_name"].replace(" ", "")

            vals["image_path"] = "/taleb/static/package_images/" + \
            time_stamp + vals["image_file_name"].replace(" ", "")

           

        # print(vals)
        super().write(vals)
        # print('pvcdsvdr')

        return True
class PackageCourses(models.Model):
    _name='package.courses'
    _description='this model for relate courses with packages'
    package_id=fields.Many2one('packages',string="Package",ondelete='cascade',readonly = True)
    course_id=fields.Many2one('courses',string='Courses',ondelete='cascade')
    cost=fields.Integer(related = 'course_id.cost',string='Course Cost')
    rate=fields.Float(related='course_id.rate',string='Course Rate')
    teacher_name=fields.Char(related='course_id.teacher_name',string='teacher name')
    image_path=fields.Char(related='course_id.image_path',string='image path')
    name=fields.Char(related='course_id.name',string='Course Name')
    duration=fields.Float(related='course_id.duration',string='Duration')
    brief=fields.Char(related='course_id.brief',string="brief")
    number_of_rater=fields.Integer(related='course_id.number_of_rater' ,string="number_of_rater")