from odoo import models,api, fields,_
import os
import time
import base64
from odoo.exceptions import ValidationError

def _abs_rout(self,data):
    path1=''
    abs = os.path.dirname(os.path.abspath(__file__))
    abs_sp =abs.split("/")
    for i in abs_sp:
        if i !='models':
            path1 += i +'/'
    return path1

class HeroSection(models.Model):
    _name = 'hero.section'
    _description = "this module is for hero.section"

    name = fields.Char("File Name" ,default='Hero Section')
    title=fields.Html(string='Title',required = True)
    hero_section_image = fields.Binary(string='Image')
    image_file_name = fields.Char("File Name")
    image_path = fields.Char(string="Image Url")
    image_full_url = fields.Char(string="Image Full Url")


    @api.model
    def create(self, vals):
       
        x = self.env['hero.section'].search_count([('id', '!=', False)])
        if x > 0:
            raise ValidationError(
                _('''لا يمكنك انشاء أكثر من سجل
يوجد سجل آخر يرجى حذفه و انشاء سجل جديد أو التعديل على السجل الموجود
:)
                
                '''))
     
        data = os.path.dirname(os.path.abspath(__file__))
        if "image_file_name" in vals and vals['image_file_name']!= False:
            if "image_file_name" in vals and "hero_section_image" in vals and vals["image_file_name"] != False and vals["hero_section_image"] != False:
                try:

                    time_stamp = str(time.time())
                    module_path = _abs_rout(self ,data)+"static/hero_section_images"#loc
          
                    isExist = os.path.exists(module_path)
                    if isExist == False:
                        os.mkdir(module_path)
                    # module_path = "/home/vps112/odoo_16/torbetodoo/torbet_app/static/hero_section_images" #servar
                    with open(os.path.join(module_path, time_stamp + vals["image_file_name"].replace(" ", "")), "wb+") as f:
                        f.write(base64.b64decode(vals["hero_section_image"]))
                except Exception as e:
                    pass

                vals["image_full_url"] = module_path + '/' + \
                time_stamp + vals["image_file_name"].replace(" ", "")
                vals["image_path"] = "/taleb/static/hero_section_images/" + \
                time_stamp + vals["image_file_name"].replace(" ", "")
        values=super().create(vals)
        return values
        
    def write(self, vals):
        module_path= ''
     
        time_stamp = str(time.time())
        data = os.path.dirname(os.path.abspath(__file__))
        mod =_abs_rout(self ,data)
        if('image_1920' in vals):
            pass
     
        if('hero_section_image' in vals):
            pass

        if "image_file_name" in vals and "hero_section_image" in vals and vals["image_file_name"] != False and vals["hero_section_image"] != False:
            try:
               
                old_image = self.image_full_url
                if old_image:
                    if os.path.exists(old_image):
                        os.unlink(old_image)


                    

                if vals["image_file_name"] == "" and vals['hero_section_image'] == "" :
                    vals["image_full_url"] = ""
                    vals["image_path"] = ''
                    super().write(vals)
                    return True

                # module_path = "/home/vps112/odoo_16/torbetodoo/torbet_app/static/hero_section_images"#server
                module_path = mod +"static/hero_section_images"#loc
                isExist = os.path.exists(module_path)
             
                if isExist == False:
                    os.mkdir(module_path)

                    
                with open(os.path.join(module_path, time_stamp + vals["image_file_name"].replace(" ", "")), "wb+") as f:
                    f.write(base64.b64decode(vals["hero_section_image"]))
              

            except Exception as e:
                pass
            vals["image_full_url"] = module_path + '/' + \
            time_stamp + vals["image_file_name"].replace(" ", "")

            vals["image_path"] = "/taleb/static/hero_section_images/" + \
            time_stamp + vals["image_file_name"].replace(" ", "")

      

        # print(vals)
        super().write(vals)
        # print('pvcdsvdr')

        return True