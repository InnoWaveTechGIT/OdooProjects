from odoo import models,api, fields,_,exceptions
import re
import os
import time
import base64

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

class AboutUsHaven(models.Model):
    _name = 'about.us.haven'
    _description = "this module is for about.us"
    _rec_name = 'title'

    title = fields.Char(string='Title')
    brief = fields.Html(string='brief ')
    face_book = fields.Char(string='Face Book')
    linked_in = fields.Char(string='Linked In')
    instagram = fields.Char(string='Instagram')



    @api.model
    def create(self, vals):
        # Check if a record already exists
        if self.search_count([]) >= 1:
            raise exceptions.ValidationError("Only one About Us record can be created!")
        return super(AboutUsHaven, self).create(vals)
