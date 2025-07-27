from odoo import models,api, fields,_
import re
import os
import time
import base64 
from odoo.exceptions import ValidationError

class PromotersTaleb(models.TransientModel):
    _name = 'coupons.report'
    _description = "this module is for Coupons reports"

    promoters_id=fields.Many2one('promoters' ,string='Promoter' ,required = True)
    date_from = fields.Datetime('From')
    date_to = fields.Datetime('To')

    def action_print_report(self):
        domain = []
        if self.read()[0]['promoters_id']:
            promoters_id = self.read()[0]['promoters_id'][0]
            domain += [('promoter_id' , '=' , promoters_id)]
        else:
            domain += [('coupon_id' , '=' , promoters_id)]
        if self.read()[0]['date_from']:
            date_from = self.read()[0]['date_from']
            domain += [('created_date' , '>=' , date_from)]
        if self.read()[0]['date_to']:
            date_to = self.read()[0]['date_to']
            domain += [('created_date' , '<=' , date_to)]
  
            
        coupons= self.env['subscription_payments'].search_read(domain)
        total = 0
        coupons_id = []
        for coupon in coupons:
            coupons_id.append(coupon['coupon_id'][0])
            total += coupon['commition']
        domain.pop(0)

        coupons_id = list(set(coupons_id))
        data_appear = []
        
        for coupon_id in coupons_id : 
            count = 0 
            total_std = 0
            domain += [('coupon_id' , '=' , coupon_id)]
            total_std= self.env['subscription_payments'].search_count(domain)
            coupon = self.env['subscription_payments'].search(domain)
            for s in coupon:
                count += s.commition
                coupon_name = s.coupon_id
            x={
                'coupon_id' : coupon_name.promotion_code , 
                'total_std' : total_std,
                'count_commission' : count
            }
            data_appear.append(x)
            domain.pop(-1)
        
        
        data={
            'form_data' : self.read()[0],
            'coupons' : data_appear,
            'total' : total
        }

        return self.env.ref('taleb.action_coupon_report_card').report_action(self,data=data)