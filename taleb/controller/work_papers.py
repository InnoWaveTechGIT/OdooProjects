from odoo import http
from odoo.http import request, Response
import json
import jwt
import base64


class WorkPapers(http.Controller):
    @http.route('/work_papers/<int:course_id>', auth='public' , methods=['GET'], csrf=False)
    def get_work_papers_taleb(self,course_id):
        course_id = int(course_id)
        result= []
        header = request.httprequest.headers
        # token = header['Authorization'].replace('Bearer ', '')
        # try:
        #     dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
        # except Exception as e:
        #     response = json.dumps({ 'jsonrpc': '2.0', 'message': 'Unauthorized!'})
        #     return Response(
        #     response, status=401,
        #     headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        #     )
        
        # user_id = int(dec_token['id'])
        check_str=lambda x:x if x else ''
        try:
            # subscription= True
            # subscription = request.env['subscription'].sudo().search([('course_id' , '=' ,course_id) , ('user_id' , '=' , user_id)])
            # if subscription :
            work_papers_taleb = http.request.env['work.papers.taleb'].sudo().search([('course_id', '=', course_id)])
            if work_papers_taleb:
                for rec in work_papers_taleb:
                    result.append({
                        'id' : rec.id,
                        'title' : rec.title,
                        'course_id' : rec.course_id.id,
                        'course_name' : rec.course_id.name,
                        'section_id' : rec.section_id.id,
                        'section_name' : rec.section_id.name,
                        'work_paper_ids_question' : [{'id':line.id,
                                        'title':check_str(line.title),
                                        'question':check_str(line.question_path),
                                            }for line in rec.work_paper_ids ],
                        'work_paper_ids_answer' : [{'id':line.id,
                                        'title':check_str(line.title),
                                        'answer':check_str(line.answer_path),
                                            }for line in rec.work_paper_ids ]
                    })

                response=json.dumps({"data":result, 'message':'Work papers' , 'code' : 200})
                return Response( response,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
            else:
                response=json.dumps({"data":[], 'message':'Work Papers doesn\t exist' , 'code' : 200})
                return Response( response,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
           
        except Exception as e:
            response = json.dumps({'data': [], 'message': str(e)})
            return Response(
                response, status=500,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
    @http.route('/work_papers/<int:course_id>/<int:work_id>', auth='public' , methods=['GET'], csrf=False)
    def get_work_papers_taleb1(self,course_id,work_id):
        course_id = int(course_id)
        work_id = int(work_id)
        result= []
        header = request.httprequest.headers
        token = header['Authorization'].replace('Bearer ', '')
        try:
            dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
        except Exception as e:
            response = json.dumps({ 'jsonrpc': '2.0', 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        
        user_id = int(dec_token['id'])
        try:
            # subscription = True
            subscription = request.env['subscription'].sudo().search([('course_id' , '=' ,course_id) , ('user_id' , '=' , user_id)])
            if subscription :
                work_papers_taleb = http.request.env['work.papers.line.taleb'].sudo().search([('id', '=', work_id)])
                work_papers_comments_taleb = http.request.env['work.papers.enquery.taleb'].sudo().search([('work_id', '=', work_id)])
                
                for rec in work_papers_taleb:
                    result.append({
                        'work_paper_ids_question' : {'id':rec.id,
                                        'title':rec.title,
                                        'question':rec.question_path,
                                            },
                        'work_paper_ids_answer' : {'id':rec.id,
                                        'title':rec.title,
                                        'answer':rec.answer_path,
                                            },
                        "Pending_Questions":[{
                            'id' : comment.id,
                            'comment' : comment.comment ,
                            'user' : comment.user_id.name ,
                            'section_id':comment.section_id.id,
                            'section_name':comment.section_id.name,
                            'course_id':comment.course_id.name,
                            'course_id':comment.course_id.name,
                            'user_id' : comment.user_id.id ,
                            'user_image' : comment.user_id.image_path,
                            'images' : [{
                                'id' : image.id,
                                'image' : image.image_url
                            }for image in comment.image_ids],
                            'replays' :
                            [{
                                'id' : replay.id,
                                'comment' : replay.comment ,
                                'user' : replay.user_id.name ,
                                'user_id' : replay.user_id.id ,
                                'images' : 
                                     [replay.image_url1 ,
                                     replay.image_url2 ,
                                     replay.image_url3 ,
                                     replay.image_url4 ,
                                    replay.image_url5 ]
                                
                                
                            }for replay in comment.comment_ids]
                            }for comment in work_papers_comments_taleb if comment.pending and comment.user_id.id == user_id],
                        'comments' : [{
                            'id' : comment.id,
                            'comment' : comment.comment ,
                            'user' : comment.user_id.name ,
                            'section_id':comment.section_id.id,
                            'section_name':comment.section_id.name,
                            'course_id':comment.course_id.name,
                            'course_id':comment.course_id.name,
                            'user_id' : comment.user_id.id ,
                            'user_image' : comment.user_id.image_path,
                            'images' : [{
                                'id' : image.id,
                                'image' : image.image_url
                            }for image in comment.image_ids],
                            'replays' :
                            [{
                                'id' : replay.id,
                                'comment' : replay.comment ,
                                'user' : replay.user_id.name ,
                                'user_id' : replay.user_id.id ,
                                'images' : 
                                     [replay.image_url1 ,
                                     replay.image_url2 ,
                                     replay.image_url3 ,
                                     replay.image_url4 ,
                                    replay.image_url5 ]
                                
                                
                            }for replay in comment.comment_ids]
                            }for comment in work_papers_comments_taleb if not comment.pending]
                        
                                        
                    })

                response=json.dumps({"data":result, 'message':'Work Papers' , 'code' : 200})
                return Response( response,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
            else:

                response=json.dumps({"data":[], 'message':'يرجى شراء الكورس' , 'code' : 403})
                return Response( response,status=403,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
        except Exception as e:
            response = json.dumps({'data': [], 'message': str(e)})
            return Response(
                response, status=500,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )

    @http.route('/work_papers/comment', auth="public", csrf=False, website=True, methods=['POST'])
    def add_student_comment_workpaper(self, **kw):
        authe = request.httprequest.headers
        body = {}
        session_id = 0
        try:
            body = json.loads(request.httprequest.data)
        except Exception as e:
            pass
        
        comment1 = ''
        comment = ''
        try:
            token = authe['Authorization'].replace('Bearer ', '')
            dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
            print('dec_token >>> ' , dec_token)
        except Exception as e:
            response = json.dumps({'jsonrpc': '2.0', 'message': 'Unauthorized!'})
            return Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', '100')]
            )
        
        user_id = int(dec_token['id'])
        images = request.httprequest.files.getlist('images[]')
        comment_images = []
        section_id = 0
        if kw:
            if 'work_id' in kw:
                work_id = kw['work_id']
            if 'section_id' in kw:
                section_id = int(kw['section_id'])
        
        if 'comment' in kw:
            comment = kw['comment']
        else:
            response = json.dumps({"message": "يرجى ادخال السؤال"})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('accept', 'application/json'), ('Content-Length', '100')]
            )
        work_id = request.env['work.papers.line.taleb'].search([('id' , '=' ,int(work_id))])
        session_course_id = request.env['section'].sudo().search([('id', '=', work_id.work_id.section_id.id)])
        

        course_id = session_course_id.course_id.id
        subscription_ids = request.env['subscription'].sudo().search([('course_id', '=', course_id), ('user_id', '=', user_id)])
        
        # if session_course_id.is_public == False:
        #     if len(subscription_ids) == 0:
        #         response = json.dumps({"messsage": "الطالب غير مشترك بالكورس"})
        #         return Response(
        #             response, status=200,
        #             headers=[('Content-Type', 'application/json'), ('accept', 'application/json'), ('Content-Length', '100')]
        #         )
        
        new_comment = request.env['work.papers.enquery.taleb'].sudo().create({
            'user_id': user_id, 'comment': comment, 'work_id': work_id.id, 'section_id': session_course_id.id
        })
        
        size = 0.0
        if images:
            for image in images:
                blob = image.read()
                size += len(blob)
        
                if size > 5300000:
                    response = json.dumps({'data': [], 'message': 'حجم الصور كبير'})
                    return Response(
                        response, status=400,
                        headers=[('Content-Type', 'application/json'), ('Content-Length', '100')]
                    )
                
                comment_image = base64.encodebytes(blob)
                comment_images.append({
                    'image': comment_image,
                    'comment_id': new_comment.id
                })
        
        if comment_images:
            for i in comment_images:
                new_comment_images = request.env['comment.images.workpaper'].sudo().create(i)
        
        if new_comment:
            response = json.dumps({"data": {'id': new_comment.id}, "message": "تم إضافة السؤال بنجاح"})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('accept', 'application/json'), ('Content-Length', '100')]
            )


    @http.route('/work_papers/comment/<int:comment_id>', auth="public", csrf=False, website=True, methods=['PUT'])
    def edit_student_comment_workpaper(self, comment_id, **kw):
        authe = request.httprequest.headers
        body = {}
        session_id = 0
        work_id = 0
        try:
            body = json.loads(request.httprequest.data)
        except Exception as e:
            pass
        
        comment1 = ''
        comment = ''
        try:
            token = authe['Authorization'].replace('Bearer ', '')
            dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
        except Exception as e:
            response = json.dumps({'jsonrpc': '2.0', 'message': 'Unauthorized!'})
            return Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', '100')]
            )
        try:
            user_id = dec_token['id']
            
            images = request.httprequest.files.getlist('images[]')
            comment_images = []
            section_id = 0
            if kw:
                if 'work_id' in kw:
                    work_id = int(kw['work_id'])
                if 'comment' in kw:
                    comment1 = kw['comment']
                
            
            if 'comment' in kw:
                comment = kw['comment']
            else:
                response = json.dumps({"message": "يرجى ادخال السؤال"})
                return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'), ('accept', 'application/json'), ('Content-Length', '100')]
                )
            
            work_id = request.env['work.papers.line.taleb'].search([('id' , '=' ,int(work_id))])
            session_course_id = request.env['section'].sudo().search([('id', '=', work_id.work_id.section_id.id)])

            course_id = session_course_id.course_id.id
            subscription_ids = request.env['subscription'].sudo().search([('course_id', '=', course_id), ('user_id', '=', user_id)])

            
            comment_record = request.env['work.papers.enquery.taleb'].sudo().browse(comment_id)
            
            if not comment_record:
                response = json.dumps({"message": "Record not found"})
                return Response(
                    response, status=404,
                    headers=[('Content-Type', 'application/json'), ('accept', 'application/json'), ('Content-Length', '100')]
                )
            
            # Update the comment record with the new values
            comment_record.write({
                'comment': comment1,
                'work_id': work_id,
                'section_id': session_course_id.id,
                'course_id' : course_id
            }) 
            
            size = 0.0
            if images:
                for image in images:
                    blob = image.read()
                    size += len(blob)
            
                    if size > 5300000:
                        response = json.dumps({'data': [], 'message': 'حجم الصور كبير'})
                        return Response(
                            response, status=400,
                            headers=[('Content-Type', 'application/json'), ('Content-Length', '100')]
                        )
                    
                    comment_image = base64.encodebytes(blob)
                    comment_images.append({
                        'image': comment_image,
                        'comment_id': comment_record.id
                    })
            old_images = request.env['comment.images.workpaper'].sudo().search([('comment_id' , '=' , int(comment_record.id))])
            old_images.unlink()
            if comment_images:
                
                for i in comment_images:
                    
                    new_comment_images = request.env['comment.images.workpaper'].sudo().create(i)
            
            response = json.dumps({"message": "تم تعديل السؤال بنجاح"})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('accept', 'application/json'), ('Content-Length', '100')]
            )
        except Exception as e:
            response = json.dumps({'data': {}, 'message': str(e)})
            return Response(
                response, status=500,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )

    @http.route('/work_papers/comment/<int:comment_id>', auth="public", csrf=False, website=True, methods=['DELETE'])
    def delete_student_comment_workpaper(self, comment_id):
        authe = request.httprequest.headers
        
        try:
            token = authe['Authorization'].replace('Bearer ', '')
            dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
        except Exception as e:
            response = json.dumps({'jsonrpc': '2.0', 'message': 'Unauthorized!'})
            return Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', '100')]
            )
        
        user_id = dec_token['id']
        
        comment_record = request.env['work.papers.enquery.taleb'].sudo().browse(comment_id)
        
        if not comment_record:
            response = json.dumps({"message": "Record not found"})
            return Response(
                response, status=404,
                headers=[('Content-Type', 'application/json'), ('accept', 'application/json'), ('Content-Length', '100')]
            )
        
        # Delete the comment record
        comment_record.unlink()
        
        response = json.dumps({"message": "تم حذف السؤال بنجاح"})
        return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'), ('accept', 'application/json'), ('Content-Length', '100')]
        )
    
    @http.route('/workpaper/reply', auth='public', methods=['POST'], csrf=False)
    def create_reply(self, **post):
        headers = request.httprequest.headers
        
        user_id = 0
        print('qq')
        try:
            token = headers['Authorization'].replace('Bearer ', '')
            print('q1')
            dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
            print('q2')
            if dec_token: 
                print('q3')
                user_id = int(dec_token['id'])
                print('qq')
        except Exception as e:
            response = json.dumps({'data': {}, 'message': 'User not found', 'code': 404})
            return Response(
                response, status=404,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        print('user_id', user_id)
        check_int = lambda x: int(x) if x else 0
        check_float = lambda x: float(x) if x else 0.0
        check_str = lambda x: str(x) if x else ''
        try:        
            image_list = request.httprequest.files.getlist('images[]') # Assuming 'images' is a list of image files
            images = []
            for image in image_list:
                print('sdsd')
                # Convert each image to base64 encoding
                image_data = base64.encodebytes(image.read())
                images.append(image_data)
            print(image_list)
            reply_data = {
                'user_id': user_id,
                'comment': check_str(post.get('text')),
                'replay_id': check_int(post.get('comment_id')),
                'image_1': images[0] if len(images) >= 1 else '',
                'image_2': images[1] if len(images) >= 2 else '',
                'image_3': images[2] if len(images) >= 3 else '',
                'image_4': images[3] if len(images) >= 4 else '',
                'image_5': images[4] if len(images) >= 5 else '',
                
            }
            print('reply_data', reply_data) 
            request.env['work.papers.enquery.line.taleb'].sudo().create(reply_data)
            
            response = json.dumps({'message': 'Record created successfully', 'code': 200, 'data': []})

            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        except Exception as e:
            response = json.dumps({'data': {}, 'message': str(e)})
            return Response(
                response, status=500,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        
    @http.route('/workpaper/reply/<int:reply_id>', auth="public", csrf=False, methods=['PUT'])
    def edit_reply(self, reply_id, **post):
        headers = request.httprequest.headers
       
        user_id = 0
        try:
            token = headers['Authorization'].replace('Bearer ', '')
            dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
            if dec_token: 
                user_id = int(dec_token['id'])
        except Exception as e:
            response = json.dumps({'data': {}, 'message': 'User not found', 'code': 404})
            return Response(
                response, status=404,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        # print('user_id', user_id)
        # user_id = 2
        check_int = lambda x: int(x) if x else 0
        check_float = lambda x: float(x) if x else 0.0
        check_str = lambda x: str(x) if x else ''
        try:        
            reply = request.env['work.papers.enquery.line.taleb'].sudo().search([('id', '=', reply_id), ('user_id', '=', user_id)])
            if reply:
                image_list = request.httprequest.files.getlist('images[]') # Assuming 'images' is a list of image files
                images = []
                for image in image_list:
                    # Convert each image to base64 encoding
                    image_data = base64.encodebytes(image.read())
                    images.append(image_data)

                reply_data = {
                    'comment': check_str(post.get('text')),
                    'image_1': images[0] if len(images) >= 1 else '',
                    'image_2': images[1] if len(images) >= 2 else '',
                    'image_3': images[2] if len(images) >= 3 else '',
                    'image_4': images[3] if len(images) >= 4 else '',
                    'image_5': images[4] if len(images) >= 5 else '',
                    
                }
                reply.sudo().write(reply_data)
                response = json.dumps({
                    'data': [],
                    'message': 'reply has updated successfully',
                    'code': 200
                })
                return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
                )
            else:
                response = json.dumps({'data': {}, 'message': 'reply not found', 'code': 404})
                return Response(
                    response, status=404,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
                )
            
        except Exception as e:
            response = json.dumps({'data': {}, 'message': str(e), 'code': 500})
            return Response(
                response, status=500,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )

    @http.route('/workpaper/reply/<int:reply_id>', auth="public", csrf=False, methods=['DELETE'])
    def delete_reply(self, reply_id):
        headers = request.httprequest.headers
        
        user_id = 0
        try:
            token = headers['Authorization'].replace('Bearer ', '')
            dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
            if dec_token: 
                user_id = int(dec_token['id'])
        except Exception as e:
            response = json.dumps({'data': {}, 'message': 'User not found', 'code': 404})
            return Response(
                response, status=404,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        try:
            if reply_id:
                record = request.env['work.papers.enquery.line.taleb'].sudo().search([
                    ('id', '=', int(reply_id)),
                    ('user_id', '=', user_id)
                ], limit=1)
                if record:
                    print('=============1')
                    record.sudo().unlink()
                    print('test')
                    response = json.dumps({'data': [], 'message': 'reply has been deleted successfully', 'code': 200})
                else:
                    response = json.dumps({'message': 'reply not found or access denied', 'code': 404})
            else:
                response = json.dumps({'message': 'Invalid reply ID', 'code': 400})
            
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        except Exception as e: 
            response = json.dumps({'data': [], 'message': str(e), 'code': 500})
            return Response(
                response, status=500,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )