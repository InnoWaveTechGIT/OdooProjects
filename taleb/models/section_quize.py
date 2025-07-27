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

class SectionQuize(models.Model):
    _name="section_quize"
    _description=" model describe the tests for section "
    name = fields.Char()
    _rec_name = 'section_id'
    pdf_file = fields.Binary(string="PDF File")
    course_id = fields.Many2one('courses' , string='Course' ,required = True ,ondelete='cascade')
    section_id = fields.Many2one('section' , string ='section' ,required = True,domain="[('course_id', '=', course_id)]")
    test = fields.Char(string="File Url", readonly = True)
    file_path = fields.Char(string="File Url", readonly = True)
    file_full_url = fields.Char(string="File Full Url", readonly = True)
    file_name = fields.Char("File Name", readonly = True)
    @api.constrains('pdf_file')
    def _check_is_pdf(self):
        for rec in self:
            if rec.pdf_file:
                file_name, file_extension = os.path.splitext(rec.file_name)
                if file_extension.lower() != '.pdf':
                    raise ValidationError("File must be a PDF file.")
    
    
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
                    print('module_path')
                    print(module_path)
                    with open(os.path.join(module_path, time_stamp  + vals["file_name"].replace(" ", "")), "wb+") as f:
                        f.write(base64.b64decode(vals["pdf_file"]))
                except Exception as e:
                        print('error')

                vals["file_full_url"] = module_path + '/' + \
                time_stamp + vals["file_name"].replace(" ", "")
                vals["file_path"] = "/taleb/static/section_quize/" + \
                time_stamp + vals["file_name"].replace(" ", "")
        values=super().create(vals)
        return values
    def write(self, vals):
        print('Absolute directoryname: ',
        os.path.dirname(os.path.abspath(__file__)))
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
                    print('old_section')
                    if os.path.exists(old_section):
                        os.unlink(old_section)
                    time_stamp = str(time.time())

                if vals["file_name"] == "" and vals['pdf_file'] == "" :
                        print('hello from')
                        vals["file_full_url"] = ""
                        vals["file_path"] = ''
                        super().write(vals)
                        return True
                module_path = mod +"static/section_quize"#loc
                isExist = os.path.exists(module_path)
                    
                if isExist == False:
                    os.mkdir(module_path)
                print(module_path)
                with open(os.path.join(module_path, time_stamp + vals["file_name"].replace(" ", "")), "wb+") as f:
                        f.write(base64.b64decode(vals["pdf_file"]))    
                    

            except Exception as e:
                    print("There was an error saving the binary file: ", str(e))
            vals["file_full_url"] = module_path + '/' + \
                time_stamp + vals["file_name"].replace(" ", "")

            vals["file_path"] = "/taleb/static/section_quize/" + \
                time_stamp + vals["file_name"].replace(" ", "")

            super().write(vals)


            return True
        
    def unlink(self):
        for rec in self :
            old_section = rec.file_full_url
            if old_section:
                
                print('old_section')
                if os.path.exists(old_section):
                        os.unlink(old_section)
            x=super(SectionQuize,self).unlink()
            return x  
            