from odoo import models,api, fields,_
from odoo.exceptions import ValidationError
from datetime import date
import os
import base64
import time


def _abs_rout(self,data):
    path1=''
   

    abs = os.path.dirname(os.path.abspath(__file__))
    abs_sp =abs.split("/")
    
    for i in abs_sp:
        if i !='models':
            path1 += i +'/'
    return path1

class Refrences(models.Model):
    _name="refrences"
    _description=" model describe the refrences "
    refrence_name=fields.Char()
    content = fields.Text()
    pdf_file = fields.Binary(string="PDF File")
    file_path = fields.Char(string="File Url", readonly = True)
    file_full_url = fields.Char(string="File Full Url", readonly = True)
    file_name=fields.Char("File Name")
    session_id=fields.Many2one('course.video' , string = 'Session')
    selection = fields.Selection([
        ('pdf', 'Add PDF file'),
        ('content', 'Write in content field')
    ], string='Selection', default='pdf')

    
    @api.model
    def create(self, vals):
        module_path = ''
        session_id=self.env['course.video'].search([('id','=',vals['session_id'])])

        # course_name=section_id.course_id.name+'/'+section_id.name        
        path=session_id.Title+'/'
    
        data=os.path.dirname(os.path.abspath(__file__))
        if "file_name" in vals and vals['file_name']!= False:
            
            
            if "file_name" in vals and "pdf_file" in vals and vals["file_name"] != False and vals["pdf_file"] != False:
                
                try:

                    time_stamp = str(time.time())
                    module_path = _abs_rout(self ,data)+"static/refrences"#loc
                    isExist = os.path.exists(module_path)
                    if isExist == False:
                        os.mkdir(module_path)

                    with open(os.path.join(module_path, time_stamp  + vals["file_name"].replace(" ", "")), "wb+") as f:
                        f.write(base64.b64decode(vals["pdf_file"]))
                except Exception as e:
                        pass

                vals["file_full_url"] = module_path + '/' + \
                time_stamp + vals["file_name"].replace(" ", "")
                vals["file_path"] = "/taleb/static/refrences/" + \
                time_stamp + vals["file_name"].replace(" ", "")
        values=super().create(vals)
        return values
        
        
    def write(self, vals):
       
        data = os.path.dirname(os.path.abspath(__file__))
        mod =_abs_rout(self ,data)
        module_path=''
        time_stamp=''
        if('pdf_file' in vals):
            print('personal')
            print(type(vals['pdf_file']))
        if "file_name" in vals and "pdf_file" in vals and vals["file_name"] != False and vals["pdf_file"] != False:
            
            try:
                old_section = self.file_full_url
                if old_section:
                    if os.path.exists(old_section):
                        os.unlink(old_section)
                    time_stamp = str(time.time())

                if vals["file_name"] == "" and vals['pdf_file'] == "" :
                        print('hello from')
                        vals["file_full_url"] = ""
                        vals["file_path"] = ''
                        super().write(vals)
                        return True
                module_path = mod +"static/refrences"#loc
                isExist = os.path.exists(module_path)
                    
                if isExist == False:
                    os.mkdir(module_path)
                with open(os.path.join(module_path, time_stamp + vals["file_name"].replace(" ", "")), "wb+") as f:
                        f.write(base64.b64decode(vals["pdf_file"]))    
                    

            except Exception as e:
                    pass
            vals["file_full_url"] = module_path + '/' + \
                time_stamp + vals["file_name"].replace(" ", "")

            vals["file_path"] = "/taleb/static/refrences/" + \
                time_stamp + vals["file_name"].replace(" ", "")

            super().write(vals)


        return True
    
    def unlink(self):
        for rec in self :
            old_section = rec.file_full_url
            if old_section:
                
                if os.path.exists(old_section):
                        os.unlink(old_section)
            x=super(Refrences,self).unlink()
            return x  
            
        
       
            
           
            
            
    
        

            
            