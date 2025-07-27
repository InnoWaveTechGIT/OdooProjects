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
class Our_Patners(models.Model):
    _name = 'our.partner'
    _description = 'Our Partner'

    name = fields.Char(string='Name', required=True)
    image = fields.Binary(string='Image')
    image_file_name = fields.Char("File Name")
    image_path = fields.Char(string="Image Url")
    image_full_url = fields.Char(string="Image Full Url")
    @api.model
    def create(self, vals):
        
        module_path= ''
        
        time_stamp = str(time.time())
        data = os.path.dirname(os.path.abspath(__file__))
        mod =_abs_rout(self ,data)
        if "image_file_name" in vals and vals['image_file_name']!= False:
            if "image_file_name" in vals and "image" in vals and vals["image_file_name"] != False and vals["image"] != False:
                try:

                    time_stamp = str(time.time())
                    module_path = _abs_rout(self ,data)+"static/our_partners_image"#loc
          
                    isExist = os.path.exists(module_path)
                    if isExist == False:
                        os.mkdir(module_path)
                    
                    with open(os.path.join(module_path, time_stamp + vals["image_file_name"].replace(" ", "")), "wb+") as f:
                        f.write(base64.b64decode(vals["image"]))
                except Exception as e:
                        pass

                vals["image_full_url"] = module_path + '/' + \
                time_stamp + vals["image_file_name"].replace(" ", "")
                vals["image_path"] = "/taleb/static/our_partners_image/" + \
                time_stamp + vals["image_file_name"].replace(" ", "")
                
      
       
        return super().create(vals)
    def write(self, vals):
        module_path= ''
        
        time_stamp = str(time.time())
        data = os.path.dirname(os.path.abspath(__file__))
        mod =_abs_rout(self ,data)
        

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
                module_path = mod +"static/our_partners_image"#loc
                isExist = os.path.exists(module_path)
                
                if isExist == False:
                    os.mkdir(module_path)

                    
              
                with open(os.path.join(module_path, time_stamp + vals["image_file_name"].replace(" ", "")), "wb+") as f:
                    f.write(base64.b64decode(vals["image"]))
              

            except Exception as e:
                pass
            vals["image_full_url"] = module_path + '/' + \
            time_stamp + vals["image_file_name"].replace(" ", "")

            vals["image_path"] = "/taleb/static/our_partners_image/" + \
            time_stamp + vals["image_file_name"].replace(" ", "")

     

        
        return super().write(vals)
        

    