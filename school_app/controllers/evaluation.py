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

class HomeWork(http.Controller):
   
    @http.route('/school/evaluation',  auth="api_key",csrf=False, website=True, methods=['POST'])
    def create_student_evaluation(self,**kw):
        user_id=request.env.uid
        body = json.loads(request.httprequest.data)
        user = request.env['res.users'].sudo().browse(user_id)

        if user.user_type != 'Teacher':
            response = json.dumps({'data': [], 'message': 'Only teachers can create reports', 'code': 403})
            return Response(
                response, status=403,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        

        
        homework = request.env['student.evaluation.report'].sudo().create({
            'student_id': body.get('student_id'),
            'subject_id' : body.get('subject_id'),
            'teacher_id' : user.id,
            'rate' : body.get('rate'), 
            'note' : body.get('note'),
            'date' : body.get('date'),
        })
        

        response = json.dumps({'data': [], 'message': 'Home work created', 'code': 200})
        return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
        )
   

    @http.route('/school/evaluation',  auth="api_key",csrf=False, website=True, methods=['GET'])
    def get_student_evaluation(self,student_id=None,page=None,limit=None,**kw):
        user_id=request.env.uid
        user = request.env['res.users'].sudo().browse(user_id)
        if limit :
            limit = int (limit)
            
        else:
            limit = 10

        if page:
            page = int(page)
            
        else:
            page = 1 
        result = []
        
        if not student_id:
            response = json.dumps({'data': '' , 'message' : 'No Data Please enter student id' , 'code' : 400, 'all':0, 'totalpages':int(0)})
            return Response(
                response, status=400,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        else:
            student_id = int(student_id)
        student_homework = request.env['student.evaluation.report'].sudo().search([('student_id' , '=' , student_id) ], limit=limit, offset=(page - 1) * limit)
        album_obj_count = request.env['student.evaluation.report'].sudo().search_count([('student_id' , '=' , student_id) ])
        if len(student_homework) != 0:
            totalpages = math.ceil(album_obj_count / limit)
        else:
            if album_obj_count and int(limit)>album_obj_count:
                totalpages=1
            else:
                totalpages=0 
        if student_homework:
            for home in student_homework : 
                result.append({
                    'id' : home.id,
                    'student_id' : home.student_id.id,
                    'student_name' : home.student_id.name,
                    'day' : str(home.date),
                    'subject_id' : home.subject_id.id,
                    'teacher_id' : home.teacher_id.id,
                    'subject_name' : home.subject_id.name,
                    'teacher_name' : home.teacher_id.name,
                    'rate' : home.rate,
                    'note' : home.note,
                })
            response = json.dumps({'data': result, 'message': 'Done', 'code': 200, 'all':album_obj_count, 'totalpages':int(totalpages)})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        else:
            response = json.dumps({'data': [], 'message': 'No Home work For this date', 'code': 200, 'all':album_obj_count, 'totalpages':int(totalpages)})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
