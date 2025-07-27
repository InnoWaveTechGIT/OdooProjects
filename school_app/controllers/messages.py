from odoo import http
# from werkzeug.wrappers import Response
import logging
from datetime import datetime
import xmlrpc.client as xmlrpclib
import json
from odoo import models, fields, api
import math
import os
import requests
from odoo.http import request ,Response
# from odoo.http import JsonRequest
import jwt
import re
import werkzeug.wrappers
import socket
from os import path
from pathlib import Path 
import pathlib
import collections
import base64


class Data(http.Controller):

    def get_user_comment(self , user_comment , user_token) :
        if user_comment.id == user_token:
            return True
        else:
            return False
   
    @http.route('/school/messages',  auth="api_key",csrf=False, website=True, methods=['POST'])
    def add_student_data_details(self,student_id=None,**kw):
        user_id=request.env.uid
        result = []
        if student_id:

            student_conversation = request.env['school.conversation'].sudo().search([('user_id' , '=' , int(student_id))])
        else:
            student_conversation = request.env['school.conversation'].sudo().search([('user_id' , '=' , int(user_id))])
        user = request.env['res.users'].sudo().browse(user_id)
        images=request.httprequest.files.getlist('images[]')
        album_images=[]
        if student_conversation:
            message_data = {
                'user_id' : user.id,
                'body' : kw.get('body'),
                'conversation_id' : student_conversation.id
            }
            student_message = request.env['school.message'].sudo().create(message_data)
            for image in images:
                
                blob = image.read()

                album_image= base64.encodebytes(blob)
                
                album_images.append({
                    'image' : album_image,
                    'message_id':int(student_message.id)
                })
            if album_images:
                new_album_images = http.request.env['images.school.app'].sudo().create(album_images)
            response = json.dumps({'data': message_data , 'message' : 'your message sent' , 'code' : 200})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        else:
            student_conversation = request.env['school.conversation'].sudo().create({
                'user_id' : int(student_id)
            })
            message_data = {
                'user_id' : user.id,
                'body' : kw.get('body'),
                'conversation_id' : student_conversation.id
            }
            student_message = request.env['school.message'].sudo().create(message_data)
            for image in images:
                album_images=[]
                blob = image.read()

                album_image= base64.encodebytes(blob)
                
                album_images.append({
                    'image' : album_image,
                    'message_id':int(student_message.id)
                })
            if album_images:
                new_album_images = http.request.env['images.school.app'].sudo().create(album_images)
            response = json.dumps({'data': [] , 'message' : 'your message sent' , 'code' : 200})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
    @http.route('/school/messages',  auth="api_key",csrf=False, website=True, methods=['DELETE'])
    def delete_student_data_details(self,id,**kw):
        user_id=request.env.uid
        result = []
        student_conversation = request.env['school.message'].sudo().search([('id' , '=' , int(id))])
        user = request.env['res.users'].sudo().browse(user_id)
        if student_conversation and user.id == student_conversation.user_id.id:
            student_conversation.unlink()
            response = json.dumps({'data': [] , 'message' : 'your message deleted' , 'code' : 200})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        else:
            
            response = json.dumps({'data': [] , 'message' : 'you can\'t delete message not belong to you' , 'code' : 400})
            return Response(
                response, status=400,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
    
    @http.route('/school/messages',  auth="api_key",csrf=False, website=True, methods=['GET'])
    def get_student_message_details(self,student_id=None,page=None,limit=None,**kw):
        user_id=request.env.uid
        if limit :
            limit = int (limit)
            
        else:
            limit = 10

        if page:
            page = int(page)
            
        else:
            page = 1 
        result = []
        if student_id:

            student_conversation = request.env['school.conversation'].sudo().search([('user_id' , '=' , int(student_id))], limit=limit, offset=(page - 1) * limit)
            album_obj_count = request.env['school.conversation'].sudo().search_count([('user_id' , '=' , int(student_id))])
            
        else:
            student_conversation = request.env['school.conversation'].sudo().search([('user_id' , '=' , int(user_id))], limit=limit, offset=(page - 1) * limit)
            album_obj_count = request.env['school.conversation'].sudo().search_count([('user_id' , '=' , int(user_id))])
            print('student_conversation >> ' , student_conversation)

        if len(student_conversation) != 0:
            totalpages = math.ceil(album_obj_count / limit)
        else:
            if album_obj_count and int(limit)>album_obj_count:
                totalpages=1
            else:
                totalpages=0 

        user = request.env['res.users'].sudo().browse(user_id)
        if student_conversation:
            for message in student_conversation:
                print("message.message_ids >>> " , message.message_ids)
                for line in message.message_ids:
                    line.write({
                                'user_ids': [(4, user_id)]  # Use (4, ID) to add a new record to the Many2many field
                            })
                result.append({
                    'id':message.id,
                    'messages' : [{
                        'id' : line.id,
                        'user': line.user_id.name,
                        'body' : line.body,
                        'date' :str(line.date),
                        'is_me' : self.get_user_comment(line.user_id , user_id),
                        'images':[{
                            'id' :image.id,
                            'image' : image.image_url,
                            'small_image_url' : image.small_image_url
                        } for image in line.image_ids]
                        
                    } for line in message.message_ids]
                })
            response = json.dumps({'data': result , 'message' : 'your messages' , 'code' : 200, 'all':album_obj_count, 'totalpages':int(totalpages)})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        else:
            
            response = json.dumps({'data': [] , 'message' : 'there is no messages' , 'code' : 404})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )