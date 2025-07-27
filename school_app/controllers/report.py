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

class Report(http.Controller):
    def get_report_data(self , reports , temperature):
        result=[]
        for report in reports:
            result.append({
                'report_id' : report.id,
                'student_name' : report.user_id.name,
                'date' : str(report.date),
                'breakfast' : report.fields_1,
                'lunch' : report.fields_2,
                'snack' : report.fields_3,
                'student_mood' : [{
                    'id' : mood.id,
                    'Period' : mood.Period,
                    'name' : mood.mood_id.name,
                    'image':mood.mood_id.image_url
                    }for mood in report.mood_ids],
                'student_drinks' : [{
                    'id' : drink.id,
                    'name' : drink.drink_id.name,
                    'image':drink.drink_id.image_url
                    }for drink in report.drink_ids],
                'student_health' : [{
                    'id' : health.id,
                    'name' : health.health_id.name,
                    'image' : health.health_id.image_url,
                    'number_of':health.number_of
                    }for health in report.health_ids],
                'student_behavior' : [{
                    'id' : behavior.id,
                    'name' : behavior.behavior_id.name,
                    'image' : behavior.behavior_id.image_url,
                    'status':behavior.status
                    }for behavior in report.behavior_ids],
                'temperature' : [{
                    'temperature' : behavior.temperature,
                    'date' : str(behavior.time),
                    'unit':behavior.unit
                    }for behavior in temperature],
                'teacher_notes' : report.description if report.description else ''
            })
        return result
    @http.route('/school/report',  auth="api_key",csrf=False, website=True, methods=['GET'])
    def get_student_report(self, date ,student_id=None ,**kw):
        user_id=request.env.uid
        result = []
        student_reports = request.env['student.report'].sudo().search([])
        temperature = request.env['school.temperature'].sudo().search([('date' , '=' , date)])
        user_id = request.env['res.users'].sudo().search([('id' , '=' , user_id)])
        if user_id.user_type == 'Student':
            student_report = request.env['student.report'].sudo().search([('user_id' , '=' , user_id.id) , ('date' , '=' , date)])
            if student_report:
                result = self.get_report_data(student_report ,temperature)
                response = json.dumps({'data': result[0] , 'message' : 'Report for this day' , 'code' : 200})
                return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
                )
            else:
                response = json.dumps({'data': [] , 'message' : 'No report for this day' , 'code' : 404})
                return Response(
                    response, status=404,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
                )
        if user_id.user_type == 'Teacher':
            student_report = request.env['student.report'].sudo().search([('user_id' , '=' , int(student_id)) , ('date' , '=' , date)])
            if student_report:
                result = self.get_report_data(student_report,temperature)
                response = json.dumps({'data': result[0] , 'message' : 'Report for this day' , 'code' : 200})
                return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
                )
            else:
                response = json.dumps({'data': [] , 'message' : 'No report for this day' , 'code' : 404})
                return Response(
                    response, status=404,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
                )

    @http.route('/school/report', auth="api_key", csrf=False, website=True, methods=['POST'])
    def create_student_report(self,student_id, **kw):
        user_id = request.env.uid
        body = json.loads(request.httprequest.data)
        user = request.env['res.users'].sudo().browse(user_id)

        if user.user_type == 'Student':
            response = json.dumps({'data': [], 'message': 'Only teachers can create reports', 'code': 403})
            return Response(
                response, status=403,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        
        
        date = body.get('date', False)
        breakfast = body.get('breakfast', False)
        lunch = body.get('lunch', False)
        snack = body.get('snack', False)
        mood_ids = body.get('mood_ids', [])
        drink_ids = body.get('drink_ids', [])
        health_ids = body.get('health_ids', [])
        behavior_ids = body.get('behavior_ids', [])
        teacher_notes = body.get('teacher_notes', '')
        student_report = request.env['student.report'].sudo().search([('user_id' , '=' , int(student_id)) , ('date' , '=' , date)])
        if student_report:
                response = json.dumps({'data': [] , 'message' : 'There is a report for this day you can update on ' , 'code' : 400})
                return Response(
                    response, status=400,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
                )
        report_data = {
            'user_id': int(student_id),
            'date': date,
            'fields_1': breakfast,
            'fields_2': lunch,
            'fields_3': snack,
            'description': teacher_notes,
        }

        report = request.env['student.report'].sudo().create(report_data)

        # Add mood_ids, drink_ids, health_ids, and behavior_ids to the report
        report.write({
            'mood_ids': [(0, 0, {'Period': mood['Period'], 'mood_id': mood['mood']}) for mood in mood_ids],
            'drink_ids': [(0, 0, {'drink_id': drink['drink']}) for drink in drink_ids],
            'health_ids': [(0, 0, {'health_id': health['action'], 'number_of': health['number_of']}) for health in health_ids],
            'behavior_ids': [(0, 0, {'behavior_id': behavior['behavior'], 'status': behavior['status']}) for behavior in behavior_ids],
        })

        response = json.dumps({'data': {'report_id': report.id}, 'message': 'Report created successfully', 'code': 200})
        return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
        )

    @http.route('/school/report/mood', auth="api_key", csrf=False, website=True, methods=['POST'])
    def create_update_student_mood(self,id=None , report_id=None, **kw):
        user_id = request.env.uid
        body = json.loads(request.httprequest.data)
        user = request.env['res.users'].sudo().browse(user_id)

        if user.user_type == 'Student':
            response = json.dumps({'data': [], 'message': 'Only teachers can create reports', 'code': 403})
            return Response(
                response, status=403,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        if id :
            mood = request.env['student.mood.report'].sudo().browse(int(id))
            mood.write({
                'Period': body['Period'], 
                'mood_id': body['mood']
            })
            response = json.dumps({'data': [], 'message': 'Data was Update', 'code': 200})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        else:
            mood = request.env['student.mood.report'].sudo().create({
                'student_id': int(report_id),
                'Period': body['Period'], 
                'mood_id': body['mood']
            })
        
            response = json.dumps({'data': [], 'message': 'Data was create', 'code': 200})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
    
    @http.route('/school/report/drinks', auth="api_key", csrf=False, website=True, methods=['POST'])
    def create_update_student_drinks(self,id=None , report_id=None, **kw):
        user_id = request.env.uid
        body = json.loads(request.httprequest.data)
        user = request.env['res.users'].sudo().browse(user_id)

        if user.user_type == 'Student':
            response = json.dumps({'data': [], 'message': 'Only teachers can create reports', 'code': 403})
            return Response(
                response, status=403,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        if id :
            drink = request.env['student.drink.report'].sudo().browse(int(id))
            drink.write({
                'drink_id': body['drink_id']
            })
            response = json.dumps({'data': [], 'message': 'Data was Update', 'code': 200})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        else:
            drink = request.env['student.drink.report'].sudo().create({
                'student_id': int(report_id),
                'drink_id': body['drink_id']
            })
        
            response = json.dumps({'data': [], 'message': 'Data was create', 'code': 200})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
    
    @http.route('/school/report/behavior', auth="api_key", csrf=False, website=True, methods=['POST'])
    def create_update_student_behavior(self,id=None , report_id=None, **kw):
        user_id = request.env.uid
        body = json.loads(request.httprequest.data)
        user = request.env['res.users'].sudo().browse(user_id)

        if user.user_type == 'Student':
            response = json.dumps({'data': [], 'message': 'Only teachers can create reports', 'code': 403})
            return Response(
                response, status=403,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        if id :
            behavior = request.env['student.behavior.report'].sudo().browse(int(id))
            behavior.write({
                'behavior_id': body['behavior_id'],
                'status' : body['status']
            })
            response = json.dumps({'data': [], 'message': 'Data was Update', 'code': 200})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        else:
            behavior = request.env['student.behavior.report'].sudo().create({
                'student_id': int(report_id),
                'behavior_id': body['behavior_id'],
                'status' : body['status']
            })
        
            response = json.dumps({'data': [], 'message': 'Data was create', 'code': 200})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )

    
    @http.route('/school/report/health', auth="api_key", csrf=False, website=True, methods=['POST'])
    def create_update_student_health(self,id=None , report_id=None, **kw):
        user_id = request.env.uid
        body = json.loads(request.httprequest.data)
        user = request.env['res.users'].sudo().browse(user_id)

        if user.user_type == 'Student':
            response = json.dumps({'data': [], 'message': 'Only teachers can create reports', 'code': 403})
            return Response(
                response, status=403,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        if id :
            health = request.env['student.health.report'].sudo().browse(int(id))
            health.write({
                'health_id': body['health_id'],
                'number_of' : body['number_of']
            })
            response = json.dumps({'data': [], 'message': 'Data was Update', 'code': 200})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        else:
            health = request.env['student.health.report'].sudo().create({
                'student_id': int(report_id),
                'health_id': body['health_id'],
                'number_of' : body['number_of']
            })
        
            response = json.dumps({'data': [], 'message': 'Data was create', 'code': 200})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
    @http.route('/school/report/nots', auth="api_key", csrf=False, website=True, methods=['POST'])
    def create_update_student_nots(self,id=None , report_id=None, **kw):
        user_id = request.env.uid
        body = json.loads(request.httprequest.data)
        user = request.env['res.users'].sudo().browse(user_id)

        if user.user_type == 'Student':
            response = json.dumps({'data': [], 'message': 'Only teachers can create reports', 'code': 403})
            return Response(
                response, status=403,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        
        else:
            health = request.env['student.report'].sudo().search([('id' ,'='  ,int(report_id))])
            health.write({
                'description' : body.get('description')
            })
         
        
            response = json.dumps({'data': [], 'message': 'Data was create', 'code': 200})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
    @http.route('/school/report/food', auth="api_key", csrf=False, website=True, methods=['POST'])
    def create_update_student_food(self, report_id=None, **kw):
        user_id = request.env.uid
        body = json.loads(request.httprequest.data)
        breakfast = bool(body.get('breakfast', False))
        lunch = bool(body.get('lunch', False))
        snack = bool(body.get('snack', False))
        user = request.env['res.users'].sudo().browse(user_id)
        if user.user_type == 'Student':
            response = json.dumps({'data': [], 'message': 'Only teachers can create reports', 'code': 403})
            return Response(
                response, status=403,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        
        if report_id:
            student_reports = request.env['student.report'].sudo().search([('id', '=', int(report_id))])
            values = {}
            
            values['fields_1'] = breakfast
    
            values['fields_2'] = lunch
        
            values['fields_3'] = snack

            if values:
                student_reports.write(values)
                response = json.dumps({'data': [], 'message': 'Data was updated', 'code': 200})
                return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
                )
            else:
                response = json.dumps({'data': [], 'message': 'No fields provided to update', 'code': 400})
                return Response(
                    response, status=400,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
                )
        else:
            response = json.dumps({'data': [], 'message': 'Enter report id', 'code': 400})
            return Response(
                response, status=400,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
            
