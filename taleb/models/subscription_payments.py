from odoo import models,api, fields,_
import re
import os
import time
import base64 
from datetime import datetime ,date
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
import random

def generate_numbers(x, y):
    if y <= 0:
        raise ValueError("Invalid input: y must be greater than 0.")
        
     
    number_of_session_per_payment=x//y #3
    check_divide=x%y #2
    result=[]
    for i in range(int(y)):
        if i==0 and check_divide>0:
            result.append(check_divide)
        elif check_divide>0 and i==y-1 :
            result.append(number_of_session_per_payment+check_divide)
        else :
            result.append(number_of_session_per_payment)
            
    return result


def installment(self,all_course_session,number_of_payments,course_cost,id):
        payment_tracker=[]
        number_of_payments = int(number_of_payments)
        number_of_sessions = len(all_course_session)/number_of_payments
        remainder = 0
        session_cost = int(course_cost)/int(number_of_payments)
        rest=int(course_cost)%int(number_of_payments)
        time =date.today()
        for x in range(number_of_payments):
             sessions_per_payment = round(number_of_sessions+0.01 + remainder)
             remainder += number_of_sessions -  sessions_per_payment
             if x==0 and rest>0:
                record = {
                    'payments_tracker_id':id,
                    'payment_amount':session_cost+rest,
                    'payment_date':time +relativedelta(months=x),
                    'sessions_per_payment':sessions_per_payment

                }
             else :
                 record = {
                    'payments_tracker_id':id,
                    'payment_amount':session_cost,
                    'payment_date':time +relativedelta(months=x),
                    'sessions_per_payment':sessions_per_payment

                }
                 
             payment_tracker.append(record)

        

        return payment_tracker

class SubscriptionPayments(models.Model):
    _name = 'subscription_payments'
    _description = "this module is for subscription_payments"
    _rec_name='user_id'

    
    user_id = fields.Many2one('res.users' , string= 'User ID')
    course_id = fields.Many2one('courses' , string= 'Course ID')
    section_ids = fields.Many2many('section' , string= 'Section IDs' , domain="[('course_id', '=',course_id )]")
    state = fields.Selection(
    [('draft', 'Draft'), ('posted', 'Posted')],default = 'draft')
    
    pyment_number = fields.Integer('Payment Number',default=0)
    discont = fields.Integer('Discount')
    points=fields.Integer(related='course_id.cost')
    created_date = fields.Datetime(string="Created Date", default=fields.Datetime.now)
    user_total_point=fields.Integer(related='user_id.points')
    payment_method = fields.Selection(
        [('كاش', 'كاش'), ('تقسيط', 'تقسيط')], string="Payment Method",required = True,default = 'كاش') 
    number_of_payments = fields.Selection(
        [('2', '2'), ('4', '4'), ('5', '5')], string="Number of Payment") 
    payment_type = fields.Selection(
        [('Direct', 'Direct'), ('Coupon', 'Coupon')], string="Payment Type",default = 'Direct') 
    coupon_id = fields.Many2one('promotion.code' , string = 'Coupon')
    promoter_id = fields.Many2one(related='coupon_id.user_id' , string = 'Promoter')
    commition= fields.Float('Commition' , readonly = True)
    payment_tracker_ids = fields.One2many('payments_tracker' , 'payments_tracker_id' ,string='Payment Tracker')
    

    @api.constrains('coupon_id')
    def get_name(self):
        for rec in self:
             rec.commition = rec.course_id.cost * rec.coupon_id.promoter_rate / 100
             

    @api.model
    def create(self, vals):
        time =date.today()
        start_date = time
        cost = 0.0
        print(vals)
        vals['payment_method'] = 'كاش'
        user_info=self.env['res.users'].search([('id' , '=' , vals['user_id'])])
        
        
        course = self.env['courses'].search([('id','=',vals['course_id'])])
        teacher=self.env['teacher'].search([('id' , '=' , course.teacher_id.id)])
        if self.course_id['expiration_month']:
            end_date= start_date + relativedelta(months=self.course_id['expiration_month'])
        else:
            end_date= start_date + relativedelta(years=1)

        if 'section_ids' in vals and vals['section_ids'] != [[6, False, []]] :
            sections = vals['section_ids'][0][2]
            
            if len(sections) > 1 :
                raise ValidationError(
                _('''يجب شراء قسم واحد فقط 
                
                '''))
            else:

                for section  in sections:
                    section_id = self.env['section'].search([('id','=',int(section))])
                    if user_info.points >= int(section_id.cost) :
                            user_info.points=user_info.points-section_id.cost
                    else:
                        raise ValidationError(
                        _('''لايوجد نقاط كافية 
                        
                        '''))
                    subscription = self.env['subscription'].search(['&' , ('user_id' , '=' ,vals['user_id'] ) ,('course_id' ,'=',vals['course_id'] )]) 
                    if len(subscription) == 0 :
                
                        
                        subscription_id = self.env['subscription'].create({
                                        'user_id': vals['user_id'],
                                        'course_id': vals['course_id'],
                                        'start_date': start_date,
                                        'end_date': end_date
                                        
                                    }) 
                        self.env['purchased_sections'].create({
                                                        'user_id': vals['user_id'],
                                                        'section_id': section_id.id,
                                                        'purchased_section_id': subscription_id.id
                                                        
                                                    }) 
                        sessions = self.env['course.video'].search([('section_id','=',int(section))])
                        for session in sessions:
                            self.env['purchased_sessions'].create({
                                                        'user_id': vals['user_id'],
                                                        'session_id': session.id,
                                                        'purchased_sessions_id': subscription_id.id
                                                        
                                                    }) 
                    else:                        
                        if user_info.points >= int(section_id.cost) :
                            user_info.points=user_info.points-section_id.cost
                        else:
                            raise ValidationError(
                            _('''لايوجد نقاط كافية 
                            
                            '''))
                        sessions = self.env['course.video'].search([('section_id','=',int(section))])
                        self.env['purchased_sections'].create({
                                                        'user_id': vals['user_id'],
                                                        'section_id': section_id.id,
                                                        'purchased_section_id': subscription.id
                                                        
                                                    })
                        for session in sessions:
                            self.env['purchased_sessions'].create({
                                                        'user_id': vals['user_id'],
                                                        'session_id': session.id,
                                                        'purchased_sessions_id': subscription.id
                                                        
                                                    }) 
                        
                
                
                values =super().create(vals)
                return values
                
        
        else :
            if 'payment_method' in vals and vals['payment_method'] =='كاش':
                if 'payment_type' in vals and vals['payment_type'] == 'Direct':
                    
                    subscription = self.env['subscription'].create({
                                    'user_id': vals['user_id'],
                                    'course_id': vals['course_id'],
                                    'start_date': start_date,
                                    'end_date': end_date
                                    
                                }) 
                    
                    all_course_session = self.env['course.video'].search([('course_id' , '=' , vals['course_id'])])
                    for session_id in all_course_session:
                                
                                self.env['purchased_sessions'].create({
                                            'user_id': vals['user_id'],
                                            'session_id': session_id.id,
                                            'purchased_sessions_id': subscription.id
                                            
                                        }) 
                    user_info.points=user_info.points-course.cost
                    all_course_section = self.env['section'].search([('course_id' , '=' , vals['course_id'])])
                    for section in all_course_section:
                        section_id = self.env['section'].search([('id','=',section.id)])
                        self.env['purchased_sections'].create({
                                                        'user_id': vals['user_id'],
                                                        'section_id': section_id.id,
                                                        'purchased_section_id': subscription.id
                                                        
                                                    })

                    for session_id in all_course_session:
                                
                                self.env['purchased_sessions'].create({
                                            'user_id': vals['user_id'],
                                            'session_id': session_id.id,
                                            'purchased_sessions_id': subscription.id
                                            
                                        }) 
                    values =super().create(vals)
                            
                elif  'payment_type' in vals and vals['payment_type'] == 'Coupon':
                    
                    
                    if 'discont' in vals:
                        discount= course.cost*(vals['discont'])
                        discount=discount/100
                        if user_info.points-course.cost+discount > 0 :
                            user_info.points=user_info.points-course.cost+discount
                        else:
                            raise ValidationError(
                            _('''لايوجد نقاط كافية 
                            
                            '''))
                        course.number_of_student+=1
                    
                        teacher.number_of_student+=1
                        
                        subscription = self.env['subscription'].create({
                                    'user_id': vals['user_id'],
                                    'course_id': vals['course_id'],
                                    'start_date': start_date,
                                    'end_date': end_date
                                    
                                }) 
                        all_course_section = self.env['section'].search([('course_id' , '=' , vals['course_id'])])
                        for section in all_course_section:
                            section_id = self.env['section'].search([('id','=',section.id)])
                            self.env['purchased_sections'].create({
                                                            'user_id': vals['user_id'],
                                                            'section_id': section_id.id,
                                                            'purchased_section_id': subscription.id
                                                            
                                                        })
                        all_course_session = self.env['course.video'].search([('course_id' , '=' , vals['course_id'])])
                        for session_id in all_course_session:
                                    
                                    self.env['purchased_sessions'].create({
                                                'user_id': vals['user_id'],
                                                'session_id': session_id.id,
                                                'purchased_sessions_id': subscription.id
                                                
                                            }) 
                        

                        values =super().create(vals)

            
                        
                    
            
                    
            elif 'payment_method' in vals and vals['payment_method'] =='تقسيط':
                
            
                if 'payment_type' in vals and vals['payment_type'] == 'Direct':
                    if vals['number_of_payments'] == '5':
                        
                        cost = course.cost5
                    elif vals['number_of_payments'] == '4':
                        
                        cost = course.cost4
                    else:
                        
                        cost = course.cost2
                    values =super().create(vals)
                    
                    all_course_session = self.env['course.video'].search([('course_id' , '=' , vals['course_id'])])
                    payment_tracker = installment(self,all_course_session,vals['number_of_payments'],cost,values.id)
                    counter=0
                    for record in payment_tracker:
                        self.env['payments_tracker'].create(record)
                        
                        if counter ==0:
                            subscription = self.env['subscription'].create({
                                        'user_id': vals['user_id'],
                                        'course_id': vals['course_id'] ,
                                        'start_date': start_date,
                                        'end_date':end_date
                                        
                                    }) 
                            counter=counter+1
                            
                elif 'payment_type' in vals and vals['payment_type']  =='Coupon':
                    if vals['number_of_payments']=='5':
                        cost=course.cost5
                    elif vals['number_of_payments']=='2':
                        cost=course.cost2
                    # get coupon discount 
                    if 'discont' in vals:
                        
                        
                        course.number_of_student+=1
                    
                        teacher.number_of_student+=1
                        discount= cost*(vals['discont'])
                        discount=discount/100
                        cost=cost-discount
                        values =super().create(vals)
                    
                        all_course_session = self.env['course.video'].search([('course_id' , '=' , vals['course_id'])])
                        payment_tracker = installment(self,all_course_session,vals['number_of_payments'],cost,values.id)
                        counter=0
                        for record in payment_tracker:
                            self.env['payments_tracker'].create(record)
                            
                            if counter ==0:
                                subscription = self.env['subscription'].create({
                                            'user_id': vals['user_id'],
                                            'course_id': vals['course_id'] ,
                                            'start_date': start_date,
                                            'end_date':end_date
                                            
                                        }) 
                                counter=counter+1
                    
            return values  
                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                           
                        
                        
           
                    
                    
           
                       
            


        return values



    def write(self,vals):
        if "pyment_number" in vals and vals['pyment_number'] !=False :
            
            if vals['pyment_number']>int(self.number_of_payments):
                print ("")
            else :
                pn=int(vals['pyment_number'])
                all_course_session = self.env['course.video'].search([('course_id' , '=' , self.course_id.id)])
                payment_tracker=self.env['payments_tracker'].search([('payments_tracker_id' , '=' , self.id)])
                
                user_info=self.env['res.users'].search([('id' , '=' , self.user_id.id)])
                user_info.points=user_info.points-payment_tracker[pn-1].payment_amount
                # sum from 0 to this index 
                # from sum to sum+current sessions per payment
                arr=[]
                for i in payment_tracker:
                    
                    arr.append(i.sessions_per_payment)
               
                index=int(vals['pyment_number'])-1
                sum1=sum(arr[:index])
                start=sum1
               
                
                
                end=start+payment_tracker[pn-1].sessions_per_payment
              
                
                subscription = self.env['subscription'].search([('user_id','=',self.user_id.id), ('course_id','=',self.course_id.id)])
                for i in range(start, end):
                    
                    self.env['purchased_sessions'].create({
                                            'user_id': self.user_id.id,
                                            'session_id':all_course_session[i].id ,
                                            'purchased_sessions_id': subscription[0].id
                                            
                                        })
        values =super().write(vals)
        return values
                                
            
            
class PaymentsTracker(models.Model):
    _name = 'payments_tracker'
    _description = "this module is for testing purpose only, it was created by Eng Ali Ammar"


    payments_tracker_id = fields.Many2one('subscription_payments')
    payment_date = fields.Date(string='Payment Date' ,default=fields.Date.context_today)
    payment_amount = fields.Float(string='Amount')
    sessions_per_payment = fields.Integer('Sessions per payment')

    