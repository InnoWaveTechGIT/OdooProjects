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

class Data(http.Controller):
   
    @http.route('/school/data',  auth="api_key",csrf=False, website=True, methods=['GET'])
    def get_student_data_details(self,**kw):
        user_id=request.env.uid
        result = []
        healths = request.env['student.health'].sudo().search([])
        behaviors = request.env['student.behavior'].sudo().search([])
        drinks = request.env['student.drink'].sudo().search([])
        moods = request.env['student.mood'].sudo().search([])
        result.append({
            'health':[{
                'id' : health.id,
                'name' : health.name,
                'image' : health.image_url
            } for health in healths],
            'behavior':[{
                'id' : behavior.id,
                'name' : behavior.name,
                'image' : behavior.image_url
            } for behavior in behaviors],
            'drink':[{
                'id' : drink.id,
                'name' : drink.name,
                'image' : drink.image_url
            } for drink in drinks],
            'mood':[{
                'id' : mood.id,
                'name' : mood.name,
                'image' : mood.image_url
            } for mood in moods],

        })
        response = json.dumps({'data': result , 'message' : 'All Data' , 'code' : 200})
        return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
        )

    @http.route('/school/students',  auth="api_key",csrf=False, website=True, methods=['GET'])
    def get_student_data(self,**kw):
        user_id=request.env.uid
        result = []
        user_id = request.env['res.users'].sudo().search([('id' , '=' , user_id)])
        if user_id.user_type == 'Teacher':
            class_id = request.env['class.school.app'].sudo().search([('teacher_id' , '=' , user_id.id)] , limit=1) 
            for i in class_id.student_ids:
                result.append({
                    'id' : i.id,
                    'name' : i.name,
                    'image' : i.image_url
                })
            response = json.dumps({'data': result , 'message' : 'All Data' , 'code' : 200})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        else:
            response = json.dumps({'data': [] , 'message' : 'You don\'t have access' , 'code' : 403})
            return Response(
                response, status=403,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )

    @http.route('/school/numberofunread', auth="api_key", csrf=False, website=True, methods=['GET'])
    def get_numberofunread(self, **kw):
        user_id = http.request.env.uid
        result = []

        user = http.request.env['res.users'].sudo().search([('id', '=', user_id)])

        if user.user_type == 'Teacher':
            class_id = http.request.env['class.school.app'].sudo().search([('teacher_id', '=', user_id)])
            albums = http.request.env['album.school.app'].sudo().search_count([
                ('user_ids', 'not in', (user_id,)), '|', ('status', '=', 'Public'), ('student_ids', 'in', [user_id])
            ])
            event_id = http.request.env['events.school.app'].sudo().search_count([
                ('user_ids', 'not in', (user_id,)), '|', ('class_id', '=', class_id.id), ('event_type', '=', 'Public')
            ])
            student_homework = http.request.env['home.work.lines'].sudo().search_count([
                ('user_ids', 'not in', (user_id,)), ('homework_id.class_id', '=', class_id.id)
            ])
            result.append({
                'events': event_id,
                'homework': student_homework,
                'albums': albums,
                'notifications' : 0 , 
                'messages' : 0
            })

            response = json.dumps({'data': result, 'message': 'event data', 'code': 200})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )

        if user.user_type == 'Student':
            class_id = http.request.env['class.school.app'].sudo().search([('student_ids', 'in', user_id)])
            albums = http.request.env['album.school.app'].sudo().search_count([
                ('user_ids', 'not in', (user_id,)), '|', ('status', '=', 'Public'), ('student_ids', 'in', (user_id,))
            ])
            student_homework = http.request.env['home.work.lines'].sudo().search_count([
                ('user_ids', 'not in', (user_id,)), ('homework_id.class_id', '=', class_id.id)
            ])
            event_id = http.request.env['events.school.app'].sudo().search_count([
                ('user_ids', 'not in', (user_id,)), '|', ('class_id', '=', class_id.id), ('event_type', '=', 'Public')
            ])
            messages_id = http.request.env['school.message'].sudo().search_count([
                ('user_ids', 'not in', (user_id,)),  ('conversation_id.user_id', '=', user_id)
            ])
            result.append({
                'events': event_id,
                'homework': student_homework,
                'albums': albums,
                'notifications' : 0 , 
                'messages' : messages_id
            })

            response = json.dumps({'data': result[0], 'message': 'event data', 'code': 200})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )

        response = json.dumps({'data': [], 'message': 'You don\'t have access', 'code': 403})
        return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
        )