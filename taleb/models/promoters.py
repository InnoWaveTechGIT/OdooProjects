from odoo import models,api, fields,_
import re
import os
import time
import base64 
from odoo.exceptions import ValidationError

class PromotersTaleb(models.Model):
    _name = 'promoters'
    _description = "this module is for promoters"

    name = fields.Many2one('res.users',string='Name',domain="[('user_type', '=', 'promoter')]" ,ondelete='cascade' ,required = True)
    promoter = fields.Char(related='name.name',string='Promoter Name')
    promotion_code_ids =fields.One2many('promotion.code','user_id',string='Promotion Code')
    promotion_user_ids =fields.One2many('promotion.code.user','promotion_id',string='Promotion Code')
    package_code_ids=fields.One2many('package_promotion.code','user_id',string='Package Promotion Code')
   
    # @api.constrains("write_date")
    # def check_promotion_code(self):
    #     coupons = self.env['promotion.code'].search_count([('name' , '=' , self.name)])
        
    #     if coupons >1:
            # raise ValidationError(_("هناك سجل أخر لنفس  المروج"))
class PromotionCode(models.Model):
    _name='promotion.code'
    _description='promotion code'
    _rec_name = 'promotion_code'

    user_id=fields.Many2one('promoters' ,readonly=True , ondelete = 'cascade')
    promotion_code =fields.Char(string='Promotion Code')
    is_valid = fields.Boolean('Is Valid')
    discount_percentage =fields.Integer('Discount Percentage',required = True)
    course_ids = fields.Many2many('courses',string="Courses",required = True)
    expiration_date = fields.Datetime('Expiration Date')
    promoter_rate = fields.Float('Commition')


    def name_get(self):
        result = []
        for rec in self:
            # name = record.points_id.name or ''
            result.append((rec.id, '%s - %s' % (rec.user_id.name.name,rec.promotion_code)))

        return result
    
    @api.constrains("write_date")
    def check_promotion_code(self):
        coupons = self.env['promotion.code'].search_count([('promotion_code' , '=' , self.promotion_code)])
        coupon_rat = self.env['promotion.code'].search([('promotion_code' , '=' , self.promotion_code)])
        
        if coupons >1:
            raise ValidationError(_("هناك كوبون أخر بنفس الرمز يرجى تغيير الرمز"))
        if coupon_rat.promoter_rate >= 100 :
            raise ValidationError(_("قيمة ربح المروج يجب ان تكون اقل من 100"))

class PromotionCodeUser(models.Model):
    _name='promotion.code.user'
    _description='promotion code'

    user_id=fields.Many2one('res.users',string='Promotion Code User' )
    promotion_id =fields.Many2one('promoters' , string='Promotion Code',readonly=True)
class PackagePromotionCode(models.Model):
    _name='package_promotion.code'
    _description='promotion code'

    user_id=fields.Many2one('promoters' ,readonly=True)
    promotion_code =fields.Char(string='Promotion Code')
    is_valid = fields.Boolean('Is Valid')
    discount_percentage =fields.Integer('Discount Percentage',required = True)
    package_ids = fields.Many2many('packages',string="Packages",required = True)