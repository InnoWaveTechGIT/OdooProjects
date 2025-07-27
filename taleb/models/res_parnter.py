from odoo import models,api, fields,_
from odoo.exceptions import ValidationError
import re
import os
import time
import base64
from datetime import datetime

class UserInherit(models.Model):
   
    _name='res.partner'
    _inherit = ['res.partner','mail.thread', 'mail.activity.mixin']
    _description = "contact"



    @api.model
    def create(self, vals):
        values =super().create(vals)
        todos = {   
        'res_id': values.id,    
        'res_model_id': self.env['ir.model'].search([('model', '=', 'res.partner')]).id,
        'user_id': 2,
        'summary': 'New Contact created now ',
        'note': '',
        'activity_type_id': 4,
        'date_deadline': datetime.today(),
        }   

        data=self.env['mail.activity'].create(todos)
        
        return super().create(vals)