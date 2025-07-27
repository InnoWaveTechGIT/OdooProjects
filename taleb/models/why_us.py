from odoo import models,api, fields,_
import re
import os
import time
import base64

    

class WhyUsTaleb(models.Model):
    _name = 'why.us'
    _description = "this module is for why.us"
    _rec_name = 'title'
    title = fields.Char(string='Title')
    brief = fields.Html(string='brief ')
    video = fields.Binary(string='Video')
    video_file_name = fields.Char("File Name")
    video_path = fields.Char(string="Video Url")
    video_full_url = fields.Char(string="Video Full Url",readonly=True)



    @api.constrains('video_path')
    def _get_src(self):
         for rec in self:
              if rec.video_path != False:
                   frame = rec.video_path
                   frame = frame.split(' ')
                   for values in frame:
                       
                        if values.startswith('src'):
                             code_id = values.split('/embed/')
                             
                             rec.video_full_url= code_id[-1].replace('"','')

    # @api.model
    # def create(self, vals):
    #     print("id >>>" +str(self.id))
    #     print("id >>>" +str(self._origin.id))
    #     print(vals)
    #     print('Absolute directoryname: ',
    #   os.path.dirname(os.path.abspath(__file__)))
    #     print(os.chdir('../') )
    #     data = os.path.dirname(os.path.abspath(__file__))
    #     if "video_file_name" in vals and vals['video_file_name']!= False:
    #         if "video_file_name" in vals and "video" in vals and vals["video_file_name"] != False and vals["video"] != False:
    #             try:

    #                 time_stamp = str(time.time())
    #                 module_path = _abs_rout(self ,data)+"static/video"#loc
    #                 print(module_path)
    #                 isExist = os.path.exists(module_path)
    #                 print('module_path')
    #                 print(module_path)
    #                 print('isExist')
    #                 print(isExist)
    #                 if isExist == False:
    #                     os.mkdir(module_path)
    #                 # module_path = "/home/vps112/odoo_16/torbetodoo/torbet_app/static/video" #servar
    #                 with open(os.path.join(module_path, time_stamp + vals["video_file_name"].replace(" ", "")), "wb+") as f:
    #                     f.write(base64.b64decode(vals["video"]))
    #             except Exception as e:
    #                     print('asdasdasd')

    #             vals["video_full_url"] = module_path + '/' + \
    #             time_stamp + vals["video_file_name"].replace(" ", "")
    #             vals["video_path"] = "/taleb/static/video/" + \
    #             time_stamp + vals["video_file_name"].replace(" ", "")
    #             # print("4444444444 ")
    #     values=super().create(vals)        
    #     return values
        
    # def write(self, vals):
    #     print('Absolute directoryname: ',
    #   os.path.dirname(os.path.abspath(__file__)))
    #     data = os.path.dirname(os.path.abspath(__file__))
    #     mod =_abs_rout(self ,data)
    #     module_path=''
    #     time_stamp=''
    #     print(vals)
    #     print('dvdsvvvvvvvvvvvvvvvvv')
    #     if('image_1920' in vals):
    #         print(type(vals['image_1920']))
    #         print((vals['image_1920']))


    #     if('video' in vals):
    #         print('personal')
    #         print(type(vals['video']))
    #     if "video_file_name" in vals and "video" in vals and vals["video_file_name"] != False and vals["video"] != False:
    #         try:
    #             print('self.video_full_url')
    #             print(self.video_full_url)

    #             old_image = self.video_full_url
    #             if old_image:
    #                 print('old_image')
    #                 if os.path.exists(old_image):
    #                     os.unlink(old_image)


    #                 time_stamp = str(time.time())

    #             if vals["video_file_name"] == "" and vals['video'] == "" :
    #                 print('hello from')
    #                 vals["video_full_url"] = ""
    #                 vals["video_path"] = ''
    #                 super().write(vals)
    #                 return True

    #             # module_path = "/home/vps112/odoo_16/torbetodoo/torbet_app/static/video"#server
    #             print('lllllllll')
    #             module_path = mod +"static/video"#loc
    #             isExist = os.path.exists(module_path)
    #             print('module_path')
    #             print(module_path)
    #             print('isExist')
    #             print(isExist)
    #             if isExist == False:
    #                 os.mkdir(module_path)
    #             print(module_path)
    #             with open(os.path.join(module_path, time_stamp + vals["video_file_name"].replace(" ", "")), "wb+") as f:
    #                 f.write(base64.b64decode(vals["video"]))

    #         except Exception as e:
    #             print("There was an error saving the binary file: ", str(e))
    #         vals["video_full_url"] = module_path + '/' + \
    #         time_stamp + vals["video_file_name"].replace(" ", "")

    #         vals["video_path"] = "/taleb/static/video/" + \
    #         time_stamp + vals["video_file_name"].replace(" ", "")

    #         print('vals["video_full_url"ffffffffffffffffffffffffffffff]') 
    #         print(vals["video_path"]) 

    #     # print(vals)
    #     super().write(vals)
    #     # print('pvcdsvdr')

    #     return True