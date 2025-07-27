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
        
    #17  /5 => 3  
    number_of_session_per_payment=x//y #3
    check_divide=x%y #2
    result=[]
    for i in range(int(y)):
        
        if check_divide>0 and i==y-1 :
            result.append(number_of_session_per_payment+check_divide)
        else :
            result.append(number_of_session_per_payment)
            
    return result
def installment_package(self, courses_sessions, number_of_payments, cost, id):
    payment_tracker=[]
    number_of_payments = int(number_of_payments)
    time = date.today()
    payment_amount = cost / number_of_payments
    ppt_courses = []
    remainder = 0
    courses_generated_list=[]

    for x in range(number_of_payments):
        record = {
            'payments_tracker_id': id,
            'payment_amount': payment_amount,
            'payment_date': time + relativedelta(months=x),
        }
        payment_tracker.append(record)
    for course in courses_sessions:
        all_course_session=course['all']
        res=generate_numbers(all_course_session,number_of_payments)
        courses_generated_list.append(res)
        res=[]
    for i in range(len(payment_tracker)):
        for j,course in enumerate(courses_sessions):
            sum1=0
            res=courses_generated_list[j]
            sum1=sum(res[:i])
            record1 = {
                
                'sessions_per_payment': res[i],
                'c_id': course['id'],
                'sum':sum1
            }
            ppt_courses.append(record1)

    return [payment_tracker, ppt_courses]
    
class SubscriptionPayments(models.Model):
    _name = 'package_subscription_payments'
    _description = "this module is for package_subscription_payments"
    _rec_name='user_id'

    
    user_id = fields.Many2one('res.users' , string= 'User ID')
    pyment_number = fields.Integer('Payment Number',default=0)
    
    discont = fields.Integer('Discount')
    points=fields.Float(related='Package.new_price')
    created_date = fields.Datetime(string="Created Date", default=fields.Datetime.now)
    user_total_point=fields.Integer(related='user_id.points')
    payment_method = fields.Selection(
        [('كاش', 'كاش'), ('تقسيط', 'تقسيط')], string="Payment Method",required = True,default = 'كاش') 
    number_of_payments = fields.Selection(
        [('2', '2'), ('5', '5')], string="Number of Payment") 
    payment_type = fields.Selection(
        [('Direct', 'Direct'), ('Coupon', 'Coupon')], string="Number of Payment",default = 'Direct') 

    Package = fields.Many2one('packages' ,string = 'Package')
    Package_payment_tracker_ids=fields.One2many('package_payments_tracker',"payments_tracker_id",string='Package Payment Tracker')
    @api.model
    def create(self, vals):
        time =date.today()
        start_date = time
        cost = 0.0
        package=self.env['packages'].search([('id','=',vals['Package'])])
        if self.Package['expiration_month']:
            end_date= start_date + relativedelta(months=self.Package['expiration_month'])
        else:
            end_date= start_date + relativedelta(years=1)
        courses_ids=package.package_courses
        user_date = self.env['res.users'].search([('id','=',vals['user_id'])])
        
        if  'payment_type' in vals and vals['payment_type'] == 'Direct':# no coupon
            if 'payment_method' in vals and vals['payment_method']=='كاش':
                values=super().create(vals)
                if user_date.points >= int(package.new_price) :
                    user_date.points=user_date.points-package.new_price
                else:
                    raise ValidationError(
                    _('''لايوجد نقاط كافية 
                    
                    '''))
                courses_ids=package.package_courses
                
                for course_id in courses_ids:
                
                    
                    teacher=self.env['teacher'].search([('id' , '=' , course_id.course_id.teacher_id.id)])
                    subscription = self.env['subscription'].create({
                                'user_id': vals['user_id'],
                                'course_id': course_id.course_id.id,
                                'start_date': start_date,
                                'end_date': end_date
                                
                            }) 
                    
                    sections = self.env['section'].search([('course_id' , '=' , course_id.course_id.id)])
                    for section  in sections:
                        section_id = self.env['section'].search([('id','=',int(section.id))])
                        
                        
                            
                        self.env['purchased_sections'].create({
                                                            'user_id': vals['user_id'],
                                                            'section_id': section_id.id,
                                                            'purchased_section_id': subscription.id
                                                            
                                                        }) 
                        
                    all_course_session = self.env['course.video'].search([('course_id' , '=' , course_id.course_id.id)])
                    course_id.course_id.number_of_student+=1
                
                    teacher.number_of_student+=1
                    for session_id in all_course_session:
                        
                            self.env['purchased_sessions'].create({
                                    'user_id': vals['user_id'],
                                    'session_id': session_id.id,
                                    'purchased_sessions_id': subscription.id})
            elif 'payment_method' in vals and vals['payment_method']=="تقسيط":                
                if vals['number_of_payments'] == '5':
                    cost = package.cost5
                else:
                    cost = package.cost2
                values=super().create(vals)
                courses_ids=package.package_courses
                courses_sessions=[]
                for course in courses_ids:
                    all_course_session = self.env['course.video'].search([('course_id' , '=' , course.course_id.id)])
                    rec={'all':int(len(all_course_session)),'id':course.course_id.id}
                    courses_sessions.append(rec)
                
                payment_tracker=installment_package(self, courses_sessions, vals['number_of_payments'],cost, values.id)
                ppt_courses=payment_tracker[1]
                payment_tracker=payment_tracker[0]
                ppt_ids=[]
                nop=len(courses_ids)
                
                for payment in payment_tracker:
                    p_id=self.env['package_payments_tracker'].create(payment)
                    ppt_ids.append(p_id.id)
                for index in range(len(ppt_ids)):
                    index=int(index)+1
                    first=(index* nop)-nop
                    last=(index*nop)-1
                    
                    for ppt in ppt_courses[first:last+1]:
                        ppt['ppt_id']=ppt_ids[index-1]
                        self.env['cpackage_payments_tracker'].create(ppt)
                
                for course in courses_ids:
                    counter=0
                    all_course_session = self.env['course.video'].search([('course_id' , '=' , course.course_id.id)])
                    if counter ==0:
                        subscription = self.env['subscription'].create({
                                    'user_id': vals['user_id'],
                                    'course_id': course.course_id.id,
                                    'start_date': start_date,
                                    'end_date':end_date
                                    
                                }) 
        elif   'payment_type' in vals and vals['payment_type'] == 'Coupon':
            if 'payment_method' in vals and vals['payment_method']=="كاش":
                values=super().create(vals)
                if 'discont' in vals:
                    discount=vals['discont']
                    discount= package.new_price*(vals['discont'])
                    discount=discount/100
                    if user_date.points-package.new_price+discount > 0 :
                            user_date.points=user_date.points-package.new_price+discount
                    else:
                        raise ValidationError(
                        _('''لايوجد نقاط كافية 
                        
                        '''))
                    courses_ids=package.package_courses
                    for course_id in courses_ids:
                    ### courses in package
                    
                        teacher=self.env['teacher'].search([('id' , '=' , course_id.course_id.teacher_id.id)])
                        subscription = self.env['subscription'].create({
                                    'user_id': vals['user_id'],
                                    'course_id': course_id.course_id.id,
                                    'start_date': start_date,
                                    'end_date': end_date
                                    
                                }) 
                    
                        
                        all_course_session = self.env['course.video'].search([('course_id' , '=' , course_id.course_id.id)])
                        course_id.course_id.number_of_student+=1
                    
                        teacher.number_of_student+=1

                        sections = self.env['section'].search([('course_id' , '=' , course_id.course_id.id)])
                        for section  in sections:
                            section_id = self.env['section'].search([('id','=',int(section.id))])
                            
                            
                                
                            self.env['purchased_sections'].create({
                                                                'user_id': vals['user_id'],
                                                                'section_id': section_id.id,
                                                                'purchased_section_id': subscription.id
                                                                
                                                            }) 
                        for session_id in all_course_session:
                            
                                self.env['purchased_sessions'].create({
                                        'user_id': vals['user_id'],
                                        'session_id': session_id.id,
                                        'purchased_sessions_id': subscription.id})
            elif 'payment_method' in vals and vals['payment_method']=="تقسيط": 
                
                values=super().create(vals)
                if 'discont' in vals:
                    if vals['number_of_payments']=='5':
                        cost=int(package.cost5)
                    elif vals['number_of_payments']=='2':
                        cost=int(package.cost2)
                    
                    #subtract coupon value from cost 
                    discount_amount=cost*int(vals['discont'])
                    discount_amount=discount_amount//100
                    cost=cost-discount_amount
                    courses_sessions=[]
                    for course in courses_ids:
                        all_course_session = self.env['course.video'].search([('course_id' , '=' , course.course_id.id)])
                        rec={'all':int(len(all_course_session)),'id':course.course_id.id}
                        courses_sessions.append(rec)
                    
                    payment_tracker=installment_package(self, courses_sessions, vals['number_of_payments'],cost, values.id)
                    ppt_courses=payment_tracker[1]
                    payment_tracker=payment_tracker[0]
                    ppt_ids=[]
                    nop=len(courses_ids)
                    
                    for payment in payment_tracker:
                        p_id=self.env['package_payments_tracker'].create(payment)
                        ppt_ids.append(p_id.id)
                    for index in range(len(ppt_ids)):
                        index=int(index)+1
                        first=(index* nop)-nop
                        last=(index*nop)-1
                        
                        for ppt in ppt_courses[first:last+1]:
                            ppt['ppt_id']=ppt_ids[index-1]
                            self.env['cpackage_payments_tracker'].create(ppt)
                        
                    for course in courses_ids:
                        counter=0
                        all_course_session = self.env['course.video'].search([('course_id' , '=' , course.course_id.id)])
                        if counter ==0:
                            subscription = self.env['subscription'].create({
                                        'user_id': vals['user_id'],
                                        'course_id': course.course_id.id,
                                        'start_date': start_date,
                                        'end_date':end_date
                                        
                                    })
                        #end 
        return values                
                        
                       

        
    def write(self,vals):
        if "pyment_number" in vals and vals['pyment_number'] !=False :
        
            pn=int(vals['pyment_number'])
            payment_tracker=self.env['package_payments_tracker'].search([('payments_tracker_id' , '=' , self.id)])
            payment_tracker=payment_tracker[pn-1]
            user_info=self.env['res.users'].search([('id' , '=' , self.user_id.id)])
            user_info.points=user_info.points-payment_tracker.payment_amount
            courses=self.env['cpackage_payments_tracker'].search([('ppt_id','=',payment_tracker.id)])
            for course_id in courses:
                subscription = self.env['subscription'].search([('user_id','=',self.user_id.id), ('course_id','=',course_id.c_id.id)])
                all_course_session = self.env['course.video'].search([('course_id' , '=' , course_id.c_id.id)])
                sessions=course_id.sessions_per_payment-1
                start=int(course_id.sum)
                last=start+int(course_id.sessions_per_payment)
                for i in range(start,last):
                    if i >len(all_course_session):
                        pass
                    else :
                        self.env['purchased_sessions'].create({
                                            'user_id': self.user_id.id,
                                            'session_id':all_course_session[i].id ,
                                            'purchased_sessions_id': subscription[0].id
                                            
                                        })
        values =super().write(vals)
        return values
                        
                
                
    
class PackagePaymentTracker(models.Model):
    _name='package_payments_tracker'
    _description = "this module is for testing purpose only, it was created by Eng Ali Ammar"
    payments_tracker_id = fields.Many2one('package_subscription_payments')
    payment_date = fields.Date(string='Payment Date' ,default=fields.Date.context_today)
    payment_amount = fields.Float(string='Amount')
    courses_sessions_per_payment=fields.One2many('cpackage_payments_tracker','ppt_id' , string = 'PaymentPackageTracker')
class PptCourses(models.Model):
    _name='cpackage_payments_tracker'
    _description = "this module is for testing purpose only, it was created by Eng Ali Ammar"
    c_id=fields.Many2one('courses',string='course',ondelete='cascade')
    sessions_per_payment = fields.Integer('Sessions per payment')
    ppt_id=fields.Many2one('package_payments_tracker',string='ppt_id',ondelete='cascade')
    sum=fields.Integer('number_of_purshased_sessions',default=0)
    
                       
                                    
                
        
        
        

