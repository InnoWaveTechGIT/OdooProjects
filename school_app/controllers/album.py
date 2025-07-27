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

class Album(http.Controller):

    def get_images_data(self, albums):
        result = []
        for album in albums:
            result.append({
            'id': album.id,
            'name': album.name if album.name else '',
            'status': album.status if album.status else '' ,
            'image': album.image_url,
            'small_image_url' : album.small_image_url
            })

        return result


    def get_album_data(self, albums, sd=False):
        result = []
        for album in albums:
            images = [{
            'thumbnail_image': image.small_image_url,
            'image': image.image_url
            } for image in album.image_ids]

            # Limit images based on sd flag
            if sd:
                images = images[:4]  # Slice the list to keep only the first 4 elements

            result.append({
            'id': album.id,
            'name': album.name if album.name else '',
            'status': album.status,
            'images': images
            })

        return result
    @http.route('/school/album',  auth="api_key",csrf=False, website=True, methods=['GET'])
    def get_student_albums(self,**kw):
        user_id=request.env.uid
        result = []
        user_id = request.env['res.users'].sudo().search([('id' , '=' , user_id)])
        if user_id.user_type == 'Student':
            albums = request.env['album.school.app'].sudo().search(['|',('status' , '=' , 'Public') , ('student_ids' , 'in' ,user_id.id )])
            result = self.get_album_data(albums,True)
            for i in albums:
                i.write({
                                'user_ids': [(4, user_id)]  # Use (4, ID) to add a new record to the Many2many field
                            })
            response = json.dumps({'data': result , 'message' : 'All Data' , 'code' : 200})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        if user_id.user_type == 'Teacher':
            class_id = request.env['class.school.app'].sudo().search([('teacher_id' , '=' , user_id.id)])
            albums = request.env['album.school.app'].sudo().search(['|',('status' , '=' , 'Public') , ('class_id' , '=' ,class_id.id )])
           
            result = self.get_album_data(albums,True)
            response = json.dumps({'data': result , 'message' : 'All Data' , 'code' : 200})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        else:
            response = json.dumps({'data': [] , 'message' : 'No Data' , 'code' : 404})
            return Response(
                response, status=404,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
    
    @http.route('/school/album',  auth="api_key",csrf=False, website=True, methods=['POST'])
    def create_student_album(self,**kw):
        user_id=request.env.uid
        result = []
        user_id = request.env['res.users'].sudo().search([('id' , '=' , user_id)])
        images=request.httprequest.files.getlist('images[]')
        if user_id.user_type == 'Student':
            
            response = json.dumps({'data': [] , 'message' : 'You don\'t have access to create album' , 'code' : 403})
            return Response(
                response, status=403,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        if user_id.user_type == 'Teacher':
            class_id = request.env['class.school.app'].sudo().search([('teacher_id' , '=' , user_id.id)])
            album_data={
                'name' : kw.get('name'),
                'status' : 'Private',
                'class_id' : class_id.id
            }
            
            albums = request.env['album.school.app'].sudo().create(album_data)
            for image in images:
                album_images=[]
                blob = image.read()

                album_image= base64.encodebytes(blob)
                album_images.append({
                    'image' : album_image,
                    'image_id':albums.id
                })
        
                new_album_images = http.request.env['images.school.app'].sudo().create(album_images)

            response = json.dumps({'data': result , 'message' : 'All Data' , 'code' : 200})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        else:
            response = json.dumps({'data': [] , 'message' : 'No Data' , 'code' : 404})
            return Response(
                response, status=404,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
    
    @http.route('/school/album/<int:album_id>',  auth="api_key",csrf=False, website=True, methods=['GET'])
    def get_student_albums_by_id(self,album_id,**kw):
        user_id=request.env.uid
        result = []
        user_id = request.env['res.users'].sudo().search([('id' , '=' , user_id)])
        albums = request.env['album.school.app'].sudo().search([('id' , '=' , album_id) ])
        result = self.get_album_data(albums,False)
        response = json.dumps({'data': result , 'message' : 'All Data' , 'code' : 200})
        return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
        )
    @http.route('/school/album/<int:album_id>',  auth="api_key",csrf=False, website=True, methods=['DELETE'])
    def delete_student_albums_by_id(self,album_id,**kw):
        user_id=request.env.uid
        result = []
        user_id = request.env['res.users'].sudo().search([('id' , '=' , user_id)])
        albums = request.env['album.school.app'].sudo().search([('id' , '=' , album_id) ])
        albums.sudo().unlink()
        # result = self.get_album_data(albums,False)
        response = json.dumps({'data': [] , 'message' : 'Album was delete' , 'code' : 200})
        return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
        )

    @http.route('/school/gallary',  auth="api_key",csrf=False, website=True, methods=['POST'])
    def create_student_gallary(self,album_id=None,**kw):
        user_id=request.env.uid
        result = []
        user_id = request.env['res.users'].sudo().search([('id' , '=' , user_id)])
        images=request.httprequest.files.getlist('images[]')
        if user_id.user_type == 'Student':
            
            response = json.dumps({'data': [] , 'message' : 'You don\'t have access to create album' , 'code' : 403})
            return Response(
                response, status=403,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        if user_id.user_type == 'Teacher':
            class_id = request.env['class.school.app'].sudo().search([('teacher_id' , '=' , user_id.id)])
            
            for image in images:
                album_images=[]
                blob = image.read()

                album_image= base64.encodebytes(blob)
                if album_id :
                    album_images.append({
                        'image' : album_image,
                        'image_id':int(album_id)
                    })
                else:
                    album_images.append({
                        'image' : album_image,
                        'class_id' : class_id.id,
                        'status' : 'Private'
                                        })
        
                new_album_images = http.request.env['images.school.app'].sudo().create(album_images)

            response = json.dumps({'data': result , 'message' : 'All Data' , 'code' : 200})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        else:
            response = json.dumps({'data': [] , 'message' : 'No Data' , 'code' : 404})
            return Response(
                response, status=404,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
    @http.route('/school/gallary',  auth="api_key",csrf=False, website=True, methods=['GET'])
    def get_student_images(self,**kw):
        user_id=request.env.uid
        result = []
        user_id = request.env['res.users'].sudo().search([('id' , '=' , user_id)])
        if user_id.user_type == 'Student':
            albums = request.env['images.school.app'].sudo().search(['|',('status' , '=' , 'Public') , ('student_ids' , 'in' ,user_id.id )])
            result = self.get_images_data(albums)
            response = json.dumps({'data': result , 'message' : 'All Data' , 'code' : 200})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        if user_id.user_type == 'Teacher':
            class_id = request.env['class.school.app'].sudo().search([('teacher_id' , '=' , user_id.id)])
            albums = request.env['images.school.app'].sudo().search(['|',('status' , '=' , 'Public') , ('class_id' , '=' ,class_id.id )])
           
            result = self.get_images_data(albums)
            response = json.dumps({'data': result , 'message' : 'All Data' , 'code' : 200})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        else:
            response = json.dumps({'data': [] , 'message' : 'No Data' , 'code' : 404})
            return Response(
                response, status=404,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )

    @http.route('/school/gallary/<int:image_id>', auth="api_key", csrf=False, website=True, methods=['DELETE'])
    def delete_image(self,image_id , **kw):

        if not image_id:
            response = json.dumps({'data': [], 'message': 'Missing image_id parameter', 'code': 400})
            return Response(
                response, status=400,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )

        image = request.env['images.school.app'].sudo().browse(int(image_id))
        if not image:
            response = json.dumps({'data': [], 'message': 'Image not found', 'code': 404})
            return Response(
                response, status=404,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        user_id=request.env.uid
        result = []
        user_id = request.env['res.users'].sudo().search([('id' , '=' , user_id)])
        if user_id.user_type == 'Teacher':
            image.unlink()
            response = json.dumps({'data': [], 'message': 'Image deleted successfully', 'code': 200})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        else:
            response = json.dumps({'data': [] , 'message' : 'You don\'t have access to delete images' , 'code' : 403})
            return Response(
                response, status=403,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )