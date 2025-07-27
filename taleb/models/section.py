from odoo import models,api, fields,_
import requests
from datetime import datetime ,date,timedelta
import json
from odoo.exceptions import ValidationError


class Sections(models.Model):
    _name = 'section'
    _description = "this module is for testing purpose only, it was created by Eng Ali Ammar"
    _order = 'order_num asc'


    name=fields.Char(string='Name')
    brief= fields.Char(string='Brief')
    course_id = fields.Many2one('courses' , string='')
    coursename = fields.Char(related='course_id.name' ,string='Section Name')
    duration = fields.Float(string='Duration' ,required = True)
    dacast_id =fields.Char(string= 'Dacast ID')
    cost = fields.Float(string='Cost' ,required = True)
    order_num = fields.Integer('Order')

    @api.onchange('name')
    def update_purchased_sections(self):
        purchased_sections = self.env['purchased_sections']
        for section in self:
            if section.course_id:
                subscription_ids = self.env['subscription'].search([('course_id', '=', section.course_id.id)])
                for subscription in subscription_ids:
                    # existing_purchase = purchased_sections.search([
                    #     ('user_id', '=', subscription.user_id.id),
                    #     ('section_id', '=', section.id),
                    #     ('course_id', '=', section.course_id.id)
                    # ])
                    # if not existing_purchase:
                        purchased_sections.create({
                            'user_id': subscription.user_id.id,
                            'section_id': section.id,
                            'course_id': section.course_id.id
                        })
    def cal_section_duration(self):
        duration = 0.0
        sections= self.env['section'].search([('id' , '!=' ,False)]) 
        for rec in sections:
            duration = 0.0
            section_duration = self.env['course.video'].search([('section_id' , '=' ,rec.id)])
            for obj in section_duration:
                duration += float(obj.duration)

            rec.duration =  duration
        duration = 0.0
        courses = self.env['courses'].search([('id' , '!=' ,False)])
        for course in courses:
            duration = 0.0
            sections= self.env['section'].search([('course_id' , '=' ,course.id)])
            for section in sections:
               duration += float(section.duration )
            course.duration = duration
#     @api.constrains('name')
#     def change_name(self):
#        for rec in self :
#             print('rec >>>>' , rec)
#             now = datetime.now()

#             # Subtract two minutes from the current time
#             two_minutes_ago = now - timedelta(minutes=2)
#             if rec.write_date > two_minutes_ago:
#                 vid_id = rec.dacast_id
#                 url = "https://developer.dacast.com/v2/folder/%s" % vid_id
#                 payload = {
#                     "name":rec.name,
#                     "parent_id":rec.course_id.dacast_id
#                 }
#                 headers = {
#                     "accept": "application/json",
#                     "X-Format": "default",
#                     "content-type": "application/json",
#                     "X-Api-Key": "1682575625dKkmM5tM9uCY1K5Qa3wuVBP43PjcN8xg"
#                 }

#                 response = requests.put(url, json=payload , headers=headers)
#                 print(response.text)
#     def create(self, vals):
#         range1 = range(len(vals))
#         if "name" in vals[0] and "course_id" in vals[0]:
#             course_name = self.env['courses'].search([('id', '=',vals[0]["course_id"])])
            
#             for i in range1:
            
#                 path = str(course_name.name) +'/' + str(vals[i]["name"])
               
#                 url = "https://developer.dacast.com/v2/folder"
#                 payload = {"full_path":path}
#                 headers = {
#                     "accept": "application/json",
#                     "X-Format": "default",
#                     "content-type": "application/json",
#                     "X-Api-Key": "1682575625dKkmM5tM9uCY1K5Qa3wuVBP43PjcN8xg"
#                 }

#                 response = requests.post(url, json=payload, headers=headers)
                
            
#                 data = json.loads(response.text)
             
#                 # vals[i]['dacast_id'] = data['id']
                
#             values=super().create(vals)     
#             for value in values:
#                 if value.course_id:
#                     subscription_ids = self.env['subscription'].search([('course_id', '=', value.course_id.id)])
#                     for subscription_id in subscription_ids:
#                         subscription_id.write({
#                             'purchased_section_ids': [(0, 0, {
#                                 'user_id': subscription_id.user_id.id, 
#                                 'section_id': value.id,
#                                 'course_id': value.course_id.id
#                                 }
#                             )]
#                         })
#             return values
        
#         else:
#             raise ValidationError(
#                 _('''الرجاء إدخال اسم الكورس الذي يتبع له هذا القسم أو إدخل اسم خاص بالقسم
# :)
                
#                 '''))



#     def write(self, vals):
#         # Additional logic or actions before writing the record
#         res = super(Sections, self).write(vals)
#         # Additional logic or actions after writing the record
#         if res:
#             for record in self:
#                 if record.course_id:
#                     subscription_ids = self.env['subscription'].search([('course_id', '=', record.course_id.id)])
                    
#                     for subscription_id in subscription_ids:
#                         # existing_purchase = self.env['purchased_sections'].search([
#                         #     ('user_id', '=', subscription_id.user_id.id),
#                         #     ('section_id', '=', record.id),
#                         #     ('course_id', '=', record.course_id.id)
#                         # ])
#                         # if existing_purchase:
#                         #     continue
#                         # else:
#                             subscription_id.write({
#                             'purchased_section_ids': [(0, 0, {
#                                 'user_id': subscription_id.user_id.id, 
#                                 'section_id': record.id,
#                                 }
#                             )]
#                         })

#         return True

