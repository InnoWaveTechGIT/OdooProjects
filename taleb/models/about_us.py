from odoo import models,api, fields,_
import re
import os
import time
import base64 

def _abs_rout(self,data):
        path1=''
        print('Absolute directoryname: ',
        os.path.dirname(os.path.abspath(__file__)))

        abs = os.path.dirname(os.path.abspath(__file__))
        abs_sp =abs.split("/")
        print (type(abs_sp))
        for i in abs_sp:
            if i !='models':
                path1 += i +'/'
            print(path1)
        return path1

class AboutUsTaleb(models.Model):
    _name = 'about.us'
    _description = "this module is for about.us"
    _rec_name = 'title'
    title = fields.Char(string='Title')
    brief = fields.Html(string='brief ')
    face_book = fields.Char(string='Face Book')
    linked_in = fields.Char(string='Linked In')
    instagram = fields.Char(string='Instagram')

    first_image = fields.Binary(string='First Image')
    first_image_file_name = fields.Char("First File Name")
    first_image_path = fields.Char(string="First Image Url")
    first_image_full_url = fields.Char(string="First Image Full Url")

    second_image = fields.Binary(string='Second Image')
    second_image_file_name = fields.Char("Second File Name")
    second_image_path = fields.Char(string="Second Image Url")
    second_image_full_url = fields.Char(string="Second Image Full Url")

    third_image = fields.Binary(string='Third Image')
    third_image_file_name = fields.Char("Third File Name")
    third_image_path = fields.Char(string="Third Image Url")
    third_image_full_url = fields.Char(string="Third Image Full Url")


    @api.model
    def create(self, vals):
        data = os.path.dirname(os.path.abspath(__file__))
        if "first_image_file_name" in vals and vals['first_image_file_name']!= False:
            if "first_image_file_name" in vals and "first_image" in vals and vals["first_image_file_name"] != False and vals["first_image"] != False:
                try:

                    time_stamp = str(time.time())
                    module_path = _abs_rout(self ,data)+"static/about_us_image"#loc
                    isExist = os.path.exists(module_path)
                    if isExist == False:
                        os.mkdir(module_path)
                    # module_path = "/home/vps112/odoo_16/torbetodoo/torbet_app/static/about_us_image" #servar
                    with open(os.path.join(module_path, time_stamp + vals["first_image_file_name"].replace(" ", "")), "wb+") as f:
                        f.write(base64.b64decode(vals["first_image"]))
                except Exception as e:
                        print('asdasdasd')

            vals["first_image_full_url"] = module_path + '/' + \
            time_stamp + vals["first_image_file_name"].replace(" ", "")
            vals["first_image_path"] = "/taleb/static/about_us_image/" + \
            time_stamp + vals["first_image_file_name"].replace(" ", "")
            # print("4444444444 ")

        if "second_image_file_name" in vals and vals['second_image_file_name']!= False:
            if "second_image_file_name" in vals and "second_image" in vals and vals["second_image_file_name"] != False and vals["second_image"] != False:
                try:

                    time_stamp = str(time.time())
                    module_path = _abs_rout(self ,data)+"static/about_us_image"#loc
                    isExist = os.path.exists(module_path)
                    if isExist == False:
                        os.mkdir(module_path)
                    with open(os.path.join(module_path, time_stamp + vals["second_image_file_name"].replace(" ", "")), "wb+") as f:
                        f.write(base64.b64decode(vals["second_image"]))
                except Exception as e:
                        print('asdasdasd')

            vals["second_image_full_url"] = module_path + '/' + \
            time_stamp + vals["second_image_file_name"].replace(" ", "")
            vals["second_image_path"] = "/taleb/static/about_us_image/" + \
            time_stamp + vals["second_image_file_name"].replace(" ", "")

        if "third_image_file_name" in vals and vals['third_image_file_name']!= False:
            if "third_image_file_name" in vals and "third_image" in vals and vals["third_image_file_name"] != False and vals["third_image"] != False:
                try:

                    time_stamp = str(time.time())
                    module_path = _abs_rout(self ,data)+"static/about_us_image"#loc
                    isExist = os.path.exists(module_path)
                    if isExist == False:
                        os.mkdir(module_path)
                    # module_path = "/home/vps112/odoo_16/torbetodoo/torbet_app/static/about_us_image" #servar
                    with open(os.path.join(module_path, time_stamp + vals["third_image_file_name"].replace(" ", "")), "wb+") as f:
                        f.write(base64.b64decode(vals["third_image"]))
                except Exception as e:
                        print('asdasdasd')

            vals["third_image_full_url"] = module_path + '/' + \
            time_stamp + vals["third_image_file_name"].replace(" ", "")
            vals["third_image_path"] = "/taleb/static/about_us_image/" + \
            time_stamp + vals["third_image_file_name"].replace(" ", "")
        values=super().create(vals)        
        return values
        
    def write(self, vals):
        data = os.path.dirname(os.path.abspath(__file__))
        mod =_abs_rout(self ,data)
        module_path=''
        time_stamp=''
     
        if "first_image_file_name" in vals and "first_image" in vals and vals["first_image_file_name"] != False and vals["first_image"] != False:
            try:
                old_image = self.first_image_full_url
                time_stamp = str(time.time())
                if vals["first_image_file_name"] == "" and vals['first_image'] == "" :
                    vals["first_image_full_url"] = ""
                    vals["first_image_path"] = ''
                    super().write(vals)
                    return True
                module_path = mod +"static/about_us_image"#loc
                isExist = os.path.exists(module_path)
                if isExist == False:
                    os.mkdir(module_path)
                with open(os.path.join(module_path, time_stamp + vals["first_image_file_name"].replace(" ", "")), "wb+") as f:
                    f.write(base64.b64decode(vals["first_image"]))

            except Exception as e:
                pass
            vals["first_image_full_url"] = module_path + '/' + \
            time_stamp + vals["first_image_file_name"].replace(" ", "")

            vals["first_image_path"] = "/taleb/static/about_us_image/" + \
            time_stamp + vals["first_image_file_name"].replace(" ", "")

          

        if "second_image_file_name" in vals and "second_image" in vals and vals["second_image_file_name"] != False and vals["second_image"] != False:
            try:
                old_image = self.second_image_full_url
                time_stamp = str(time.time())
                if vals["second_image_file_name"] == "" and vals['second_image'] == "" :
                    vals["second_image_full_url"] = ""
                    vals["second_image_path"] = ''
                    super().write(vals)
                    return True
                module_path = mod +"static/about_us_image"#loc
                isExist = os.path.exists(module_path)
                if isExist == False:
                    os.mkdir(module_path)
                with open(os.path.join(module_path, time_stamp + vals["second_image_file_name"].replace(" ", "")), "wb+") as f:
                    f.write(base64.b64decode(vals["second_image"]))

            except Exception as e:
                pass
            vals["second_image_full_url"] = module_path + '/' + \
            time_stamp + vals["second_image_file_name"].replace(" ", "")

            vals["second_image_path"] = "/taleb/static/about_us_image/" + \
            time_stamp + vals["second_image_file_name"].replace(" ", "")
        
        if "third_image_file_name" in vals and "third_image" in vals and vals["third_image_file_name"] != False and vals["third_image"] != False:
            try:
                old_image = self.third_image_full_url

                time_stamp = str(time.time())

                if vals["third_image_file_name"] == "" and vals['third_image'] == "" :
                    print('hello from')
                    vals["third_image_full_url"] = ""
                    vals["third_image_path"] = ''
                    super().write(vals)
                    return True

                module_path = mod +"static/about_us_image"#loc
                isExist = os.path.exists(module_path)
                if isExist == False:
                    os.mkdir(module_path)
                with open(os.path.join(module_path, time_stamp + vals["third_image_file_name"].replace(" ", "")), "wb+") as f:
                    f.write(base64.b64decode(vals["third_image"]))

            except Exception as e:
                pass
            vals["third_image_full_url"] = module_path + '/' + \
            time_stamp + vals["third_image_file_name"].replace(" ", "")

            vals["third_image_path"] = "/taleb/static/about_us_image/" + \
            time_stamp + vals["third_image_file_name"].replace(" ", "")

      
        # print(vals)
        super().write(vals)

        return True