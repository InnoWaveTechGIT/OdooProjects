from odoo import models,api, fields,_
from odoo.exceptions import ValidationError
import re
import os
import time
import base64
import requests
import json
from odoo.exceptions import UserError
from . import send_notification

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
class PaymentType(models.Model):
    _name='payment.type'
    _description='Payment Type mode'
    
    name = fields.Char(string='Payment Type ',required = True)
    receiver_name=fields.Char(string='receiver_name')
    image = fields.Binary(string='Image')
    image_file_name = fields.Char("File Name")
    image_path = fields.Char(string="Image Url")
    image_full_url = fields.Char(string="Image Full Url")
    phone_number=fields.Char(string="phone_number")
    @api.model
    def create(self, vals):
        module_path= ''
        
        time_stamp = str(time.time())
        data = os.path.dirname(os.path.abspath(__file__))
        mod =_abs_rout(self ,data)
        
        print('Absolute directoryname: ',
      os.path.dirname(os.path.abspath(__file__)))
        data = os.path.dirname(os.path.abspath(__file__))
        if "image_file_name" in vals and vals['image_file_name']!= False:
            if "image_file_name" in vals and "image" in vals and vals["image_file_name"] != False and vals["image"] != False:
                print('image file name ')
                try:

                    time_stamp = str(time.time())
                    module_path = _abs_rout(self ,data)+"static/payments_images"#loc
          
                    isExist = os.path.exists(module_path)
                    if isExist == False:
                        os.mkdir(module_path)
                    
                    with open(os.path.join(module_path, time_stamp + vals["image_file_name"].replace(" ", "")), "wb+") as f:
                        f.write(base64.b64decode(vals["image"]))
                except Exception as e:
                        print('asdasdasd')

                vals["image_full_url"] = module_path + '/' + \
                time_stamp + vals["image_file_name"].replace(" ", "")
                vals["image_path"] = "/taleb/static/payments_images/" + \
                time_stamp + vals["image_file_name"].replace(" ", "")
                print(vals['image_file_name'])
                print("VALLLLSS")
        
      
       
        return super().create(vals)
    def write(self, vals):
        module_path= ''
        
        time_stamp = str(time.time())
        data = os.path.dirname(os.path.abspath(__file__))
        mod =_abs_rout(self ,data)
        

        if "image_file_name" in vals and "image" in vals and vals["image_file_name"] != False and vals["image"] != False:
            try:
               

                old_image = self.image_full_url
                if old_image:
                    print('old_image')
                    if os.path.exists(old_image):
                        os.unlink(old_image)


                    

                if vals["image_file_name"] == "" and vals['image'] == "" :
                    print('hello from')
                    vals["image_full_url"] = ""
                    vals["image_path"] = ''
                    super().write(vals)
                    return True

                # module_path = "/home/vps112/odoo_16/torbetodoo/torbet_app/static/personal_images"#server
                module_path = mod +"static/payments_images"#loc
                isExist = os.path.exists(module_path)
                
                if isExist == False:
                    os.mkdir(module_path)

                    
              
                with open(os.path.join(module_path, time_stamp + vals["image_file_name"].replace(" ", "")), "wb+") as f:
                    f.write(base64.b64decode(vals["image"]))
              

            except Exception as e:
                pass
            vals["image_full_url"] = module_path + '/' + \
            time_stamp + vals["image_file_name"].replace(" ", "")

            vals["image_path"] = "/taleb/static/payments_images/" + \
            time_stamp + vals["image_file_name"].replace(" ", "")

     

        # print(vals)
        return super().write(vals)
        # print('pvcdsvdr')

        # return True
class Points(models.Model):
    _name='points'
    _description='Points'
    _rec_name = 'price'

    _order = 'number_of_points'
    
    number_of_points=fields.Integer(string='number_of_points')
    price=fields.Integer(string='price')

    def name_get(self):
        result = []
        for rec in self:
            # name = record.points_id.name or ''
            result.append((rec.id, '%s - %s' % (rec.number_of_points,rec.price)))

        return result
    
    @api.constrains('number_of_points')
    def _check_point_constraint(self):
        point_data=self.env['configration_points'].search([('id' , '!=' ,False )])
        if len(point_data)>0:
           
            self.price = self.number_of_points * point_data.point_price
        else:
            raise ValidationError(_("يرجى اضافة سعر للنقاط من اعدادات النقاط"))
class PointsSubscriptions(models.Model):
    _name='points.subscription'
    _description='this model for testing purposes for add points to user '
    _rec_name = 'user_id'
    image = fields.Binary(string='Image')
    image_file_name = fields.Char("File Name")
    image_path = fields.Char(string="Image Url")
    image_full_url = fields.Char(string="Image Full Url")
    payment_type=fields.Many2one('payment.type',string='Payment Method',required = True)
    points_id=fields.Many2one('points',string='Points',required = True)
    number_of_points=fields.Integer(related='points_id.number_of_points')
    # number_of_points=fields.Integer(related='points_id.price')
    user_id=fields.Many2one('res.users',string='User',required = True)
    accepted = fields.Boolean(string="Accepted", readonly=True, invisible=True)
    created_date = fields.Datetime(string="Created Date", default=fields.Datetime.now)
    last_number_of_points=fields.Integer()
    total_number_of_points=fields.Integer()
    op_number = fields.Char(string='Operation Number', required=True)
    sender_name = fields.Char(string='Sender Name', required=True)
    
    
    def add_points_to_user(self):
        for record in self:
            if not record.accepted:
                op_numbers=self.env['points.subscription'].search([('accepted','=',True)])
                print("op numbers")
                print(op_numbers)
                for number in op_numbers :
                    if number.op_number==record.op_number :
                        record.accepted=False
                        raise ValidationError(_("رقم العملية موجود مسبقا "))
                        return False
                
                user_data = self.env['res.users'].search([('id' , '=' ,self.user_id.id)])
                print("user data >>>>>>>>>>")
                print(user_data.points)
                
            
                user_data.points=user_data.points+self.points_id.number_of_points
                # show success message
                record.accepted=True
                record.total_number_of_points=record.last_number_of_points+self.points_id.number_of_points
                total_number_of_points=self.total_number_of_points
                nop=self.number_of_points
                token =self.env['user.token'].search([('user_id','=',self.user_id['id'])])
                
                f_token = token.fire_base
                title1 ='تم أضافة%s نقطة الى رصيدك بنجاح' %(nop)
                payload = {
                    
                    'title' :title1,

                    "comment":"",
                    'points' :total_number_of_points,
                    'notification_type':'Payment'
                }
                
                    
                noti_data={
            'user_id':self.user_id['id'],
            'data':payload,
            'notification_type':'Payment'
        }
        
        self.env['notifications'].create(noti_data)
        
        send_notification.send_notification(self,f_token,payload)
        
        
       
        # send_notification.send_notification(self,f_token,payload)
        title = _("Successfully!")
        message = _("Points added to user Successfully!")
        return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
            'title': title,
            'message': message,
            'sticky': False,
        }
    }
        
    @api.model
    def create(self, vals):
        print('create')
        
        user_data=self.env['res.users'].search([('id' , '=' , vals['user_id'])])
        # Call super to create the record
        if 'last_number_of_points' not in vals:
            vals['last_number_of_points']=user_data.points
        # vals['total_number_of_points']=self.number_of_points+user_data.points
        vals['total_number_of_points']=user_data.points
        print('Absolute directoryname: ',
      os.path.dirname(os.path.abspath(__file__)))
        data = os.path.dirname(os.path.abspath(__file__))
        if "image_file_name" in vals and vals['image_file_name']!= False:
            if "image_file_name" in vals and "image" in vals and vals["image_file_name"] != False and vals["image"] != False:
                print('image file name ')
                try:

                    time_stamp = str(time.time())
                    module_path = _abs_rout(self ,data)+"static/subscriptions"#loc
          
                    isExist = os.path.exists(module_path)
                    if isExist == False:
                        os.mkdir(module_path)
                    
                    with open(os.path.join(module_path, time_stamp + vals["image_file_name"].replace(" ", "")), "wb+") as f:
                        f.write(base64.b64decode(vals["image"]))
                except Exception as e:
                        print('asdasdasd')

                vals["image_full_url"] = module_path + '/' + \
                time_stamp + vals["image_file_name"].replace(" ", "")
                vals["image_path"] = "/taleb/static/subscriptions/" + \
                time_stamp + vals["image_file_name"].replace(" ", "")
                # print("4444444444 ")
                print(vals['image_file_name'])
                print("VALLLLSS")
        
        
      
       
        
        return super().create(vals)
    def write(self, vals):
        module_path= ''
        print('vals')
        print(vals)
        time_stamp = str(time.time())
        data = os.path.dirname(os.path.abspath(__file__))
        mod =_abs_rout(self ,data)
        if('image' in vals):
            print(type(vals['image']))
            print((vals['image']))

       
        if('image' in vals):
            print('personal')
            print(type(vals['image']))

        if "image_file_name" in vals and "image" in vals and vals["image_file_name"] != False and vals["image"] != False:
            try:
                print('self.image_full_url')
                print(self.image_full_url)

                old_image = self.image_full_url
                if old_image:
                    print('old_image')
                    if os.path.exists(old_image):
                        os.unlink(old_image)


                    

                if vals["image_file_name"] == "" and vals['image'] == "" :
                    print('hello from')
                    vals["image_full_url"] = ""
                    vals["image_path"] = ''
                    super().write(vals)
                    return True

                # module_path = "/home/vps112/odoo_16/torbetodoo/torbet_app/static/personal_images"#server
                print('lllllllll')
                module_path = mod +"static/personal_images"#loc
                isExist = os.path.exists(module_path)
                
                if isExist == False:
                    os.mkdir(module_path)

                    
                
                with open(os.path.join(module_path, time_stamp + vals["image_file_name"].replace(" ", "")), "wb+") as f:
                    f.write(base64.b64decode(vals["personal_image"]))
              

            except Exception as e:
                print("There was an error saving the binary file: ", str(e))
            vals["image_full_url"] = module_path + '/' + \
            time_stamp + vals["image_file_name"].replace(" ", "")

            vals["image_path"] = "/taleb/static/subscriptions/" + \
            time_stamp + vals["image_file_name"].replace(" ", "")

             

        # print(vals)
        super().write(vals)
        # print('pvcdsvdr')
        

        return True
    

class ConfigrationPoints(models.Model):
    _inherit = ['mail.thread','mail.activity.mixin']

    _name='configration_points'
    _description='this model for testing purposes for add points to user '
    
    point_price =fields.Integer('Point Price',required = True)





    @api.model
    def create(self, vals):
        price = 0 
        point_data=self.env['points'].search([('id' , '!=' ,False )])
        for rec in point_data:
            price = rec.number_of_points * vals['point_price']
            rec.update({

                "price" : price
            })
        

        valus = super().create(vals)

        return valus


    def write(self,vals):
        point_data=self.env['points'].search([('id' , '!=' ,False )])
        
        for rec in point_data:
            rec.price = rec.number_of_points * vals['point_price']
        write =super().write(vals)
        return write
    

    @api.constrains('write_date')
    def _check_numberconstraint(self):
        point_data = self.env['configration_points'].search_count([('id', '!=', False)])
        if point_data > 1:
            raise ValidationError(_("لا يمكنك انشاء اكثر من سعر للنقاط"))
class AddPointsUser(models.Model):
    _inherit = ['mail.thread','mail.activity.mixin']

    _name='points.user'
    _description='this model for testing purposes for add points to user '
    
    user_id=fields.Many2one('res.users',string='User',required = True)
    points=fields.Integer(string='points')
    total_points=fields.Integer(related='user_id.points')
    last_number_of_points=fields.Integer()
    created_date = fields.Datetime(string="Created Date", default=fields.Datetime.now)
    last_modified = fields.Datetime(string='Last Modified', compute='_compute_last_modified', store=False ,tracking=True )
    message=fields.Char(string='message' ,tracking=True)
    total_number_of_points=fields.Integer()
    # created_date = fields.Datetime(string="Created Date", default=fields.Datetime.now)
    @api.depends('write_date')
    def _compute_last_modified(self):
        for record in self:
            record.last_modified = record.write_date
            

        

    @api.model
    def create(self, vals):
        user_data=self.env['res.users'].search([('id' , '=' , vals['user_id'])])
        # Call super to create the record
        if 'last_number_of_points' not in vals:
            vals['last_number_of_points']=user_data.points
        vals['total_number_of_points']=vals['points']+user_data.points
        user_data.points=user_data.points+vals['points']
        if not vals['last_number_of_points']:
            vals['last_number_of_points']
        
        record = super().create(vals)
        
        
        
        
        token =self.env['user.token'].search([('user_id','=',vals['user_id'])])
        
        f_token = token.fire_base
        self.total_number_of_points= self.points+int(user_data.points)
        nop=vals['points']
        title1 ='تم أضافة%s نقطة الى رصيدك بنجاح' %(nop)
        payload = {
                    
                    'title' :title1,

                    "comment":"",
                    'points' :self.total_number_of_points

                }
        total_number_of_points=self.total_number_of_points
        
        return record


    def write(self,vals):
        
        
        
        if "user_id" in vals:
            
            return True
            
        
        else : 
            vals['message']=str('last add   '+str(vals['points'])+'  point')
            user_data=self.env['res.users'].search([('id' , '=' , self.user_id.id)])
            user_data.points=user_data.points+vals['points']
            write =super().write(vals)
            return write
   
# http://localhost:8069/taleb/static/payments_images/1681119009.2874658212.18Kb.png
# http://localhost:8069/taleb/static/payment_images/1681119009.2874658212.18Kb.png

class SubtractPointUser(models.Model):
    _inherit = ['mail.thread','mail.activity.mixin']

    _name='subtract.point'
    _description='this model for testing purposes for subtract points to user '
    
    user_id=fields.Many2one('res.users',string='User',required = True)
    points=fields.Integer(string='points')
    total_points=fields.Integer(related='user_id.points')
    last_number_of_points=fields.Integer()
    created_date = fields.Datetime(string="Created Date", default=fields.Datetime.now)
    last_modified = fields.Datetime(string='Last Modified', compute='_compute_last_modified', store=False ,tracking=True )
    message=fields.Char(string='message' ,tracking=True)
    total_number_of_points=fields.Integer()
    # created_date = fields.Datetime(string="Created Date", default=fields.Datetime.now)
    @api.depends('write_date')
    def _compute_last_modified(self):
        for record in self:
            record.last_modified = record.write_date
            

    

    @api.model
    def create(self, vals):
        user_data=self.env['res.users'].search([('id' , '=' , vals['user_id'])])
        # Call super to create the record
        if 'last_number_of_points' not in vals:
            vals['last_number_of_points']=user_data.points
        vals['total_number_of_points']=user_data.points-vals['points']
        user_data=self.env['res.users'].search([('id' , '=' , vals['user_id'])])
        user_data.points=user_data.points-vals['points']
        if not vals['last_number_of_points']:
            vals['last_number_of_points']
        record = super().create(vals)
        token =self.env['user.token'].search([('user_id','=',vals['user_id'])])
        f_token = token.fire_base
        self.total_number_of_points= self.points+int(user_data.points)
        nop=vals['points']
        title ='تم خصم%s نقطة الى رصيدك بنجاح' %(nop)
        payload = {
                    
                    'title' :title,

                    "comment":"",
                    'points' :self.total_number_of_points

                }
        total_number_of_points=self.total_number_of_points
        return record


    def write(self,vals):
        if "user_id" in vals:
            
            return True
            
        
        else : 
            vals['message']=str('last subtract point   '+str(vals['points'])+'  point')
            user_data=self.env['res.users'].search([('id' , '=' , self.user_id.id)])
            user_data.points=user_data.points-vals['points']
            write =super().write(vals)
            return write