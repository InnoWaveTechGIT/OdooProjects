from odoo import models,api, fields,_
import re
import os
import time
import base64 
from datetime import datetime ,date
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError



class Subscription(models.Model):
    _name = 'subscription'
    _description = "this module is for subscription"
    _rec_name='user_id'

    user_id = fields.Many2one('res.users' , string= 'User ID')
    course_id = fields.Many2one('courses' , string= 'Course ID',required = True)
    end_date = fields.Date('End Date' ,readonly = True)
    start_date = fields.Date('Start Date' , readonly = True)
    status = fields.Boolean('Status',compute='set_is_unvalid' ,readonly = True)
    discont = fields.Integer('Discount')
    points=fields.Integer(related='course_id.cost')
    created_date = fields.Datetime(string="Created Date", default=fields.Datetime.now)
    user_total_point=fields.Integer(related='user_id.points')
    active = fields.Boolean(default=True)
    
    purchased_sessions_ids =fields.One2many('purchased_sessions','purchased_sessions_id',string='Purchased Sessions',ondelete='cascade')
    purchased_section_ids =fields.One2many('purchased_sections','purchased_section_id',string='Purchased Sections',ondelete='cascade')
    @api.model
    def create(self, vals):
        
        vals['start_date'] = fields.Date.today()
        
        start_date_str = vals['start_date'].strftime('%Y-%m-%d')
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = start_date + timedelta(days=365)
        vals['end_date'] = end_date.strftime('%Y-%m-%d')
        return super().create(vals)



    def set_is_unvalid(self):
        date_now = date.today()
        for rec in self:
            if rec.end_date:
                if rec.end_date > date_now :
                    rec.update({
                        'status' :True
                    })
            else :
                rec.update({
                    'status' :False
                })
    # @api.model
    # def create(self, vals):
    #     if 'payment_type' in vals and vals['payment_type'] == 'كاش':
    #         if 'discont' in vals:
    #             course = self.env['courses'].search([('id' , '=' , vals['course_id'])])
    #             course.number_of_student+=1
    #             teacher=self.env['teacher'].search([('id' , '=' , course.teacher_id.id)])
    #             teacher.number_of_student+=1
    #             user_info=self.env['res.users'].search([('id' , '=' , vals['user_id'])])
    #             if course.cost>user_info.points:
    #                 raise ValidationError(_("الطالب لا يملك ما يكفي من النقاط للأشنراك بالدورة"))
                
    #             discount= course.cost*(vals['discont']/100)
    #             user_info.points=user_info.points-course.cost+discount
    #             time =date.today()
    #             vals['start_date'] = time
    #             if course.expiration_month:
                
    #                 vals['end_date']= vals['start_date'] + relativedelta(months=course.expiration_month)
    #             else:
    #                 vals['end_date']= vals['start_date'] + relativedelta(years=1)
    #             vals['status'] = True
                
    #             values=super().create(vals)  
    #         else:
    #             print('else ???????')
    #             course = self.env['courses'].search([('id' , '=' , vals['course_id'])])
    #             course.number_of_student+=1
    #             teacher=self.env['teacher'].search([('id' , '=' , course.teacher_id.id)])
    #             teacher.number_of_student+=1
    #             user_info=self.env['res.users'].search([('id' , '=' , vals['user_id'])])
    #             if course.cost>user_info.points:
    #                 raise ValidationError(_("الطالب لا يملك ما يكفي من النقاط للأشنراك بالدورة"))
    #             user_info.points=user_info.points-course.cost
    #             time =date.today()
    #             vals['start_date'] = time
    #             if course.expiration_month:
                
    #                 vals['end_date']= vals['start_date'] + relativedelta(months=course.expiration_month)
    #             else:
    #                 vals['end_date']= vals['start_date'] + relativedelta(years=1)
    #             vals['status'] = True
                
    #     elif 'payment_type' in vals and vals['payment_type'] == 'تقسيط':
    #         if 'number_of_payments' in vals and vals['number_of_payments'] =='2':
    #             values=super().create(vals)
    #             purchased_sessions = self.env['purchased_sessions'].search(['&',('course_id' , '=' , vals['course_id']),('user_id' , '=' , vals['user_id'])])
    #             if len(purchased_sessions) != 0:
    #                 self.env['purchased_sessions'].create({
    #                         'user_id': values.user_id.id,
    #                         'session_id': purchased_sessions.id,
    #                         'purchased_sessions_id': values.id
                            
    #                     }) 
    #             else:
    #                 all_course_session = self.env['course.video'].search([('course_id' , '=' , vals['course_id'])])

    #                 # Get half of the partners
    #                 if len(all_course_session) % 2 != 0 :
    
    #                     half_course_session = all_course_session[:(len(all_course_session)//2+1)]
    #                     for session_id in half_course_session:
    #                         self.env['purchased_sessions'].create({
    #                                 'user_id': vals['user_id'],
    #                                 'session_id': session_id.id,
    #                                 'purchased_sessions_id': values.id
                                    
    #                             }) 
    #                 else :
    #                     half_course_session = all_course_session[:(len(all_course_session)//2)]
    #                     for session_id in half_course_session:
    #                         self.env['purchased_sessions'].create({
    #                                 'user_id': vals['user_id'],
    #                                 'session_id': session_id.id,
    #                                 'purchased_sessions_id': values.id
                                    
    #                             }) 

    #     else:
    #         pass
        
    # #     sessions = self.env['course.video'].search([('course_id' , '=' , vals['course_id'])])
    # #     for session in sessions:
    # #         print("dsdsdsd")
    # #         print(session.title)
    # #         self.env['purchased_sessions'].create({
    # #     'user_id': values.user_id.id,
    # #     'session_id': session.id,
    # #     'purchased_sessions_id': values.id
        
    # # }) 
    #     return values



class PurchasedSections(models.Model):
    _name = 'purchased_sections'
    _description = "this module is for purchased_sections"


    purchased_section_id =  fields.Many2one('subscription' , string= 'subscription_id',ondelete='cascade')
    user_id = fields.Many2one('res.users' , string= 'User ID')
    section_id = fields.Many2one('section' , string= 'Section ID',required = True,ondelete='cascade')
    course_id = fields.Many2one('courses' , string= 'Course ID',ondelete='cascade')


    # @api.model
    # def create(self, vals):
       
    #     purchased_sessions = self.env['purchased_sessions'].search(['&',('session_id' , '=' , vals['session_id']),('user_id' , '=' , vals['user_id'])])
    #     if len(purchased_sessions) == 0:
    #         vals['course_id']=purchased_sessions.course_id['id']
    #         values =super().create(vals) 

    #     else:
    #         values =super().create(vals) 

    #     return True
class PurchasedSessions(models.Model):
    _name = 'purchased_sessions'
    _description = "this module is for purchased_sessions"


    purchased_sessions_id =  fields.Many2one('subscription' , string= 'subscription_id',ondelete='cascade')
    user_id = fields.Many2one('res.users' , string= 'User ID')
    session_id = fields.Many2one('course.video' , string= 'Session ID',required = True,ondelete='cascade')
    course_id = fields.Many2one('courses' , string= 'Course ID',ondelete='cascade')


    @api.model
    def create(self, vals):
       
        purchased_sessions = self.env['purchased_sessions'].search(['&',('session_id' , '=' , vals['session_id']),('user_id' , '=' , vals['user_id'])])
        if len(purchased_sessions) == 0:
            vals['course_id']=purchased_sessions.course_id['id']
            values =super().create(vals) 

        else:
            values =super().create(vals) 

        return True