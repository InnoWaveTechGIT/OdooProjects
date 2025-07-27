from odoo import models,api, fields,_
from odoo.exceptions import ValidationError
from datetime import date
import os
import base64
import time
# from fpdf import FPDF
from PIL import Image
# import img2pdf




def _abs_rout(self,data):
    path1=''
   

    abs = os.path.dirname(os.path.abspath(__file__))
    abs_sp =abs.split("/")
    
    for i in abs_sp:
        if i !='models':
            path1 += i +'/'
    return path1

class SectionQuizeResult(models.Model):
    _name="section_quize_result"
    _description=" model describe the tests for section "
    _rec_name = 'section_id'

    pdf_file = fields.Binary(string="PDF File")
    user_id = fields.Many2one('res.users' , string='User')
    the_expected_degree =fields.Integer(string="The expected degree", readonly = True)
    section_id=fields.Many2one('section' , string ='section' ,required = True)
    file_path = fields.Char(string="File Url", readonly = True)
    file_full_url = fields.Char(string="File Full Url", readonly = True)
    file_name = fields.Char("File Name", readonly = True)
    image_ids = fields.One2many('section_image','section_image_id',ondelete='cascade')
    file_type = fields.Selection(
        [('pdf', 'PDF'), ('image', 'Image')], string="File Type",required = True) 


    # @api.constrains('pdf_file')
    # def _check_is_pdf(self):
    #     for rec in self:
    #         if rec.pdf_file:
        
    #             file_extension = rec.file_name
    #             image_type = file_extension.split(".") 
    #             if image_type[-1].lower() != '.pdf':
    #                 raise ValidationError("File must be a PDF file.")

    

    @api.model
    def create(self, vals):
        module_path = ''
        data=os.path.dirname(os.path.abspath(__file__))
        
        if "file_name" in vals and vals['file_name']!= False:
            
            
            if "file_name" in vals and "pdf_file" in vals and vals["file_name"] != False and vals["pdf_file"] != False:
                
                try:

                    time_stamp = str(time.time())
                    module_path = _abs_rout(self ,data)+"static/section_quize_resalt"#loc
                    isExist = os.path.exists(module_path)
                    if isExist == False:
                        os.mkdir(module_path)
                    
                    with open(os.path.join(module_path, time_stamp  + vals["file_name"].replace(" ", "")), "wb+") as f:
                        f.write(base64.b64decode(vals["pdf_file"]))
                except Exception as e:
                        print('error')

                vals["file_full_url"] = module_path + '/' + \
                time_stamp + vals["file_name"].replace(" ", "")
                vals["file_path"] = "/taleb/static/section_quize_resalt/" + \
                time_stamp + vals["file_name"].replace(" ", "")
        values=super().create(vals)
        # course_name = self.env['section_image'].search([('id', '=',vals["image_ids"])])
     
        for i in values["image_ids"]:
            i.sudo().unlink()
        # for i in course_name:
        #     i.sudo().unlink()
        # values.write({'image_ids': [(6, 0, 0)],'file_name':'f','file_type':'pdf'
        #          })
            
        return values
    def write(self, vals):
        data = os.path.dirname(os.path.abspath(__file__))
        mod =_abs_rout(self ,data)
        
        module_path=''
        time_stamp=''
        if('pdf_file' in vals):
            pass
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
                module_path = mod +"static/section_quize_resalt"#loc
                isExist = os.path.exists(module_path)
                    
                if isExist == False:
                    os.mkdir(module_path)
                with open(os.path.join(module_path, time_stamp + vals["file_name"].replace(" ", "")), "wb+") as f:
                        f.write(base64.b64decode(vals["pdf_file"]))    
                    

            except Exception as e:
                    print("There was an error saving the binary file: ", str(e))
            vals["file_full_url"] = module_path + '/' + \
                time_stamp + vals["file_name"].replace(" ", "")

            vals["file_path"] = "/taleb/static/section_quize_resalt/" + \
            time_stamp + vals["file_name"].replace(" ", "")

        super().write(vals)


        return True
    
    def unlink(self):
        for rec in self:
            print
            old_section = rec.file_full_url
            if old_section:
                
                if os.path.exists(old_section):
                        os.unlink(old_section)
        x=super(SectionQuizeResult,self).unlink()
        return x  




class SectionQuizeImage(models.Model):
    _name="section_image"
    _description=" model describe the tests for section "



    section_image_id = fields.Many2one('section_quize_result')
    section_image = fields.Binary(string='Image')
    image_file_name = fields.Char("File Name")
    image_path = fields.Char(string="Image Url")
    image_full_url = fields.Char(string="Image Full Url")




    @api.model
    def create(self, vals):
        data = os.path.dirname(os.path.abspath(__file__))
        mod =_abs_rout(self ,data)
       
        module_path=''
        time_stamp=''
        if "image_file_name" in vals and vals['image_file_name']!= False:
            if "image_file_name" in vals and "section_image" in vals and vals["image_file_name"] != False and vals["section_image"] != False:
                try:

                    time_stamp = str(time.time())
                    module_path = mod+"static/section_images"#loc
                   
                    isExist = os.path.exists(module_path)
                    if isExist == False:
                        os.mkdir(module_path)
                    # module_path = "/home/vps112/odoo_16/torbetodoo/torbet_app/static/section_images" #servar
                    with open(os.path.join(module_path, time_stamp + vals["image_file_name"].replace(" ", "")), "wb+") as f:
                        f.write(base64.b64decode(vals["section_image"]))
                except Exception as e:
                        print('asdasdasd')

            vals["image_full_url"] = module_path + '/' + \
            time_stamp + vals["image_file_name"].replace(" ", "")
            vals["image_path"] = "/taleb/static/section_images/" + \
            time_stamp + vals["image_file_name"].replace(" ", "")
                # print("4444444444 ")
        values=super().create(vals)
        image_2_pdf =[]
      
        course_name = self.env['section_image'].search([('section_image_id', '=',vals["section_image_id"])])
       
        image_1 = Image.open(course_name[0]['image_full_url'])
        new_image = image_1.resize((1000, 1500))
        im_1 = new_image.convert('RGB')
        
        counter = 0 
        for i in course_name :
            
            image_2 = Image.open(i.image_full_url)
            new_image = image_2.resize((1000, 1200))
            im_2 = new_image.convert('RGB')
            if counter != 0:
                image_2_pdf.append(im_2)
            counter +=1

        x=im_1.save(r'/sd.pdf', save_all=True, append_images=image_2_pdf)
        section_file_pdf = self.env['section_quize_result'].search([('id', '=',values['section_image_id']['id'])])
        file = open('/home/ubuntu/taleb_odoo16/talebodoo/taleb/static/section_images/sd.pdf', "rb")
        out = file.read()

        file.close()

        gentextfile = base64.b64encode(out)
        file_name =time_stamp+'sd.pdf'
       
        section_file_pdf.write({'pdf_file': gentextfile, 'file_name': file_name})
        os.unlink('/home/ubuntu/taleb_odoo16/talebodoo/taleb/static/section_images/sd.pdf')
        return values


    
    def unlink(self):
        for rec in self:
            old_section = rec.image_full_url
            if old_section:
                
                if os.path.exists(old_section):
                        os.unlink(old_section)
        x=super(SectionQuizeImage,self).unlink()
        return x  
    def write(self, vals):
        module_path= ''
        time_stamp = str(time.time())
        data = os.path.dirname(os.path.abspath(__file__))
        mod =_abs_rout(self ,data)


        if "image_file_name" in vals and "section_image" in vals and vals["image_file_name"] != False and vals["section_image"] != False:
            try:
                old_image = self.image_full_url
                if old_image:
                    if os.path.exists(old_image):
                        os.unlink(old_image)


                    

                if vals["image_file_name"] == "" and vals['section_image'] == "" :
                    vals["image_full_url"] = ""
                    vals["image_path"] = ''
                    super().write(vals)
                    return True
                module_path = mod +"static/section_images"#loc
                isExist = os.path.exists(module_path)
                if isExist == False:
                    os.mkdir(module_path)
                with open(os.path.join(module_path, time_stamp + vals["image_file_name"].replace(" ", "")), "wb+") as f:
                    f.write(base64.b64decode(vals["section_image"]))
              

            except Exception as e:
                print("There was an error saving the binary file: ", str(e))
            vals["image_full_url"] = module_path + '/' + \
            time_stamp + vals["image_file_name"].replace(" ", "")

            vals["image_path"] = "/taleb/static/section_images/" + \
            time_stamp + vals["image_file_name"].replace(" ", "")



        super().write(vals)


        return True