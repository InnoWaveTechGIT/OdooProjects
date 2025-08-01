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
   
    @http.route('/school/homework',  auth="api_key",csrf=False, website=True, methods=['POST'])
    def create_student_homwork(self,date,**kw):
        user_id=request.env.uid
        body = json.loads(request.httprequest.data)
        user = request.env['res.users'].sudo().browse(user_id)

        if user.user_type == 'Student':
            response = json.dumps({'data': [], 'message': 'Only teachers can create reports', 'code': 403})
            return Response(
                response, status=403,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        

        class_id = request.env['class.school.app'].sudo().search([('teacher_id' , '=' , user.id)])
        student_homework = request.env['homework.school.app'].sudo().search([('class_id' , '=' , class_id.id) , ('day' , '=' , date)])
        if student_homework:
            homework = request.env['home.work.lines'].sudo().create({
                'subject_id': body.get('subject_id'),
                'homework_id' : student_homework.id,
                'teacher_id' : user.id,
                'homework_description' : body.get('homework_description'), 
            })
        else:
            student_homework = request.env['homework.school.app'].sudo().create({
                'class_id' : class_id.id ,
                 'day' : date
                 })
            homework = request.env['home.work.lines'].sudo().create({
                'subject_id': body.get('subject_id'),
                'homework_id' : student_homework.id,
                'teacher_id' : user.id,
                'homework_description' : body.get('homework_description'), 
            })

        response = json.dumps({'data': [], 'message': 'Home work created', 'code': 200})
        return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
        )
    @http.route('/school/homework',  auth="api_key",csrf=False, website=True, methods=['DELETE'])
    def delete_student_homwork(self,id,**kw):
        user_id=request.env.uid
        user = request.env['res.users'].sudo().browse(user_id)

        if user.user_type == 'Student':
            response = json.dumps({'data': [], 'message': 'Only teachers can create reports', 'code': 403})
            return Response(
                response, status=403,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        
        if id:
            id = int(id)
        
            homework = request.env['home.work.lines'].sudo().search([('id' , '=' , id)])
            if homework:
                homework.unlink()
            else:
                response = json.dumps({'data': [], 'message': 'Home work not exist', 'code': 404})
                return Response(
                    response, status=404,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
                )

        response = json.dumps({'data': [], 'message': 'Home work Deleted', 'code': 200})
        return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
        )

    @http.route('/school/homework',  auth="api_key",csrf=False, website=True, methods=['GET'])
    def get_student_homwork(self,**kw):
        user_id=request.env.uid
        user = request.env['res.users'].sudo().browse(user_id)
        result = []
        if user.user_type == 'Student':
            class_id = request.env['class.school.app'].sudo().search([('student_ids' , 'in' , user.id)])
            student_homework = request.env['homework.school.app'].sudo().search([('class_id' , '=' , class_id.id) ])
            if student_homework:
                for home in student_homework:
                    result.append({
                        'id' : home.id,
                        'class_id' : home.class_id.id,
                        'day' : str(home.day),
                        'details' :[{
                            'id' :line.id,
                            'subject_id' : line.subject_id.name,
                            'teacher_id' :line.teacher_id.name,
                            'homework_description' : line.homework_description
                        } for line in home.homework_ids]
                    })
            else:
                response = json.dumps({'data': [], 'message': 'No Home work For this date', 'code': 200})
                return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
                )

        else:
            class_id = request.env['class.school.app'].sudo().search([('teacher_id' , '=' , user.id)])
            student_homework = request.env['homework.school.app'].sudo().search([('class_id' , '=' , class_id.id) ])
            if student_homework:
                for home in student_homework:
                    home.write({
                            'user_ids': [(4, user_id)]  # Use (4, ID) to add a new record to the Many2many field
                        })
                    result.append({
                        'id' : home.id,
                        'class_id' : home.class_id.id,
                        'day' :str(home.day),
                        'details' :[{
                            'id' :line.id,
                            'subject_id' : line.subject_id.name,
                            'teacher_id' :line.teacher_id.name,
                            'homework_description' : line.homework_description
                        }for line in home.homework_ids]
                    })
            else:
                response = json.dumps({'data': [], 'message': 'No Home work For this date', 'code': 200})
                return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
                )

        response = json.dumps({'data': result, 'message': 'Home work Details', 'code': 200})
        return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
        )