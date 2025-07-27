from odoo import models,api, fields,_
from odoo.exceptions import ValidationError
import re
import os
import time
import base64
import requests
import json


class DenouncementTaleb(models.Model):
    _name = 'denouncement'
    _description = "this module is for denouncement"
    _rec_name='related_comment'
    _order ='write_date desc'

    
    related_comment = fields.Many2one('enquiries')
    denouncement_ids =fields.One2many('denouncement_details','denouncement_id')
    number_of_reports=fields.Integer(default=0,readonly=True)
    @api.constrains('related_comment')
    def check_unique_comment(self):
        for record in self:
            print('jh')
            record.validate_comment()
    def validate_comment(self):
        rec_number=self.env['denouncement'].search_count([('related_comment', '=',self.related_comment.id)])
        if rec_number>1:
            raise ValidationError(_("denouncement for this course already exist "))
    
    # delete_Realted_comment
    def delete_Realted_comment(self):
        
       
        comment = self.env['enquiries'].search([('id', '=', self.related_comment.id)])
        self.unlink()

        if comment:
            comment.unlink()

            title = _("Successfully!")
            message = _("Comment Deleted!")
            action = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': title,
                    'message': message,
                    'sticky': False,
                },
            }
        else:
            
            
            title = _("not found!")
            message = _("Comment not found!")
            action = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': title,
                'message': message,
                'sticky': False,
            },
        }

    # Redirect to tree view of the same model
        return {
        'type': 'ir.actions.act_window',
        'name': _('denouncement'),
        'res_model': 'denouncement',
        'view_mode': 'tree,form',
        'views': [(False, 'tree'), (False, 'form')],
        'context': self.env.context,
        'target': 'current',
        'action': action,
    }
        
    
class DenouncementTaleb(models.Model):
    _name = 'denouncement_details'
    _description = "this module is for testing purpose only, it was created by Eng Ali Ammar"
    # _rec_name='comment'
        
        
    user_id = fields.Many2one('res.users')
    comment = fields.Char('Comment')
    denouncement_id =fields.Many2one('denouncement')
    @api.model
    def create(self, vals):
        if "denouncement_id" in vals:
            denouncement_data = self.env['denouncement'].search([('id' , '=' , vals['denouncement_id'])])
            denouncement_data.number_of_reports += 1
        values=super().create(vals)        
        return values
