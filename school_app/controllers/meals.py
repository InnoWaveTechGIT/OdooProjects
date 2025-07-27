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

class Meals(http.Controller):
   
    @http.route('/school/meals',  auth="api_key",csrf=False, website=True, methods=['GET'])
    def get_student_meals_details(self,date,page=None,limit=None,**kw):
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
        meals = request.env['meals.school.app'].sudo().search([('date_time' , '=' , date)], limit=limit, offset=(page - 1) * limit)
        album_obj_count = request.env['meals.school.app'].sudo().search_count([('date_time' , '=' , date)])
        if len(meals) != 0:
            totalpages = math.ceil(album_obj_count / limit)
        else:
            if album_obj_count and int(limit)>album_obj_count:
                totalpages=1
            else:
                totalpages=0 
        if meals:
            for meal in meals:
                result.append({
                    'id' : meal.id,
                    # 'description' : meal.description,
                    'date_time' : str(meal.date_time),
                    'breakfast' : meal.breakfast,
                    'duration_1' : meal.duration_1,
                    'duration_12' : meal.duration_12,
                    'color_picker1' : meal.color_picker1,
                    'image_1' : meal.image_1_url,
                    'lunch' : meal.lunch,
                    'duration_2' : meal.duration_2,
                    'duration_22' : meal.duration_22,
                    'color_picker2' : meal.color_picker2,
                    'image_2' : meal.image_2_url,
                    'snack' : meal.snack,
                    'duration_3' : meal.duration_3,
                    'duration_32' : meal.duration_32,
                    'color_picker3' : meal.color_picker3,
                    'image_3' : meal.image_3_url,

                })
            response = json.dumps({'data': result , 'message' : 'All Data' , 'code' : 200, 'all':album_obj_count, 'totalpages':int(totalpages)})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        else:
            response = json.dumps({'data': [] , 'message' : 'No Data for this day' , 'code' : 404})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )