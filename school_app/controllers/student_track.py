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

class Tracking(http.Controller):
   
    @http.route('/school/tracking',  auth="api_key",csrf=False, website=True, methods=['POST'])
    def change_student_tracking_status(self , student_id , status , date,**kw):
        student_id = int(student_id)
        user_id=request.env.uid
        user_id = request.env['res.users'].sudo().search([('id' , '=' , user_id)])
        if user_id.user_type != 'Supervisor' or user_id.user_type != 'Secretary' :
            response = json.dumps({'data': [] , 'message' : 'You don\'t have access' , 'code' : 403})
            return Response(
                response, status=403,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )

        else:
            student_track = request.env['student.track.report'].search([('student_id' ,'=' , student_id)])
            if student_track :
                request.env['student.track.report.line'].create({
                    'responseble_id' : user_id.id , 
                    'date' : date , 
                    'track_id' : student_track.id,
                    'state' : status
                })
            else:
                student_track = request.env['student.track.report'].create({
                    'student_id' : student_id
                    })
                request.env['student.track.report.line'].create({
                    'responseble_id' : user_id.id , 
                    'date' : date , 
                    'track_id' : student_track.id,
                    'state' : status
                })
            
            response = json.dumps({'data': [], 'message': 'Tracking created successfully', 'code': 200})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )