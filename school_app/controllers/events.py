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
import base64
from os import path
from pathlib import Path 
import pathlib
import collections

class Meals(http.Controller):
   
    @http.route('/school/events',  auth="api_key",csrf=False, website=True, methods=['POST'])
    def Add_event_for_class(self,**kw):
        user_id=request.env.uid
        result = []
        user_id = request.env['res.users'].sudo().search([('id' , '=' , user_id)])
        if user_id.user_type == 'Teacher':
            class_id = request.env['section.school.app'].sudo().search([('teacher_id' , '=' , user_id.id)] , limit=1) 
            events_data = {
                'event_type': 'Private',
                'name' : kw.get('name'),
                'description' : kw.get('description'),
                'start_time' : kw.get('start_time') ,
                'end_time' : kw.get('end_time'),
                'class_id' : class_id.id,
                'image' : base64.encodebytes(kw.get('image').read()) if kw.get('image') else False,
                
            }
            events = request.env['events.school.app'].sudo().create(events_data)
            response = json.dumps({'data': [] , 'message' : 'event has been created' , 'code' : 200})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        else:
            response = json.dumps({'data': [] , 'message' : 'You don\'t have access to create event' , 'code' : 403})
            return Response(
                response, status=403,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
    @http.route('/school/events/<int:event_id>',  auth="api_key",csrf=False, website=True, methods=['DELETE'])
    def delete_event_for_class(self,event_id,**kw):
        user_id=request.env.uid
        result = []
        user_id = request.env['res.users'].sudo().search([('id' , '=' , user_id)])
        if user_id.user_type == 'Teacher':
            class_id = request.env['section.school.app'].sudo().search([('teacher_id' , '=' , user_id.id)] , limit=1) 
            event_id = request.env['events.school.app'].sudo().search([('class_id' , '=' , class_id.id)] , limit=1) 
            if event_id:
                event_id.sudo().unlink()
            response = json.dumps({'data': [] , 'message' : 'event has been deleted' , 'code' : 200})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        else:
            response = json.dumps({'data': [] , 'message' : 'You don\'t have access to delete event' , 'code' : 403})
            return Response(
                response, status=403,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
    @http.route('/school/events/<int:event_id>',  auth="api_key",csrf=False, website=True, methods=['GET'])
    def get_event_for_class(self,event_id,**kw):
        user_id=request.env.uid
        result = []
        user_id = request.env['res.users'].sudo().search([('id' , '=' , user_id)])
        
        event_id = request.env['events.school.app'].sudo().search([('id' , '=' , event_id)] , limit=1) 
        if event_id:
            for event in event_id:

                result.append({
                    'id' : event.id,
                    'name': event.name, 
                    'description' :event.description,
                    'start_time' :str(event.start_time),
                    'end_time':str(event.end_time),
                    'image_url':event.image_url,
                })
        response = json.dumps({'data': result , 'message' : 'event data' , 'code' : 200})
        return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
        )
    
    @http.route('/school/events',  auth="api_key",csrf=False, website=True, methods=['GET'])
    def get_events_for_class(self,student_id=None,page=None,limit=None,**kw):
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
        user_id = request.env['res.users'].sudo().search([('id' , '=' , user_id)])
        if user_id.user_type == 'Teacher':
            class_id = request.env['section.school.app'].sudo().search([('teacher_id' , '=' , user_id.id)] , limit=1) 
            event_id = request.env['events.school.app'].sudo().search(['|' , ('class_id' , '=' , class_id.id) , ('event_type' , '=' , 'Public')], limit=limit, offset=(page - 1) * limit)
            album_obj_count = request.env['events.school.app'].sudo().search_count(['|' , ('class_id' , '=' , class_id.id) , ('event_type' , '=' , 'Public')])
            if len(event_id) != 0:
                totalpages = math.ceil(album_obj_count / limit)
            else:
                if album_obj_count and int(limit)>album_obj_count:
                    totalpages=1
                else:
                    totalpages=0 
            if event_id:
                
                for event in event_id:
                    event.write({
                            'user_ids': [(4, user_id.id)]  # Use (4, ID) to add a new record to the Many2many field
                        })
                    result.append({
                        'id' : event.id,
                        'name' : event.name, 
                        'description' :event.description,
                        'start_time' :str(event.start_time),
                        'end_time':str(event.end_time),
                        'image_url':event.image_url,
                    })
        else:
            if not student_id:
                response = json.dumps({'data': '' , 'message' : 'No Data Please enter student id' , 'code' : 400, 'all':0, 'totalpages':int(0)})
                return Response(
                    response, status=400,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
                )
            else:
                student_id = int(student_id)
            class_id = request.env['section.school.app'].sudo().search([('student_ids2' , '=' , student_id)] , limit=1) 
            event_id = request.env['events.school.app'].sudo().search(['|' , ('class_id' , '=' , class_id.id) , ('event_type' , '=' , 'Public')], limit=limit, offset=(page - 1) * limit)
            album_obj_count = request.env['events.school.app'].sudo().search_count(['|' , ('class_id' , '=' , class_id.id) , ('event_type' , '=' , 'Public')])
            if len(event_id) != 0:
                totalpages = math.ceil(album_obj_count / limit)
            else:
                if album_obj_count and int(limit)>album_obj_count:
                    totalpages=1
                else:
                    totalpages=0 
            if event_id:
                for event in event_id:
                    for event in event_id:
                        event.write({
                                'user_ids': [(4, user_id.id)]  # Use (4, ID) to add a new record to the Many2many field
                            })
                    result.append({
                        'id' : event.id,
                        'name' : event.name, 
                        'description' :event.description,
                        'start_time' :str(event.start_time),
                        'end_time':str(event.end_time),
                        'image_url':event.image_url,
                    })
        response = json.dumps({'data': result , 'message' : 'event data' , 'code' : 200, 'all':album_obj_count, 'totalpages':int(totalpages)})
        return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
        )
       