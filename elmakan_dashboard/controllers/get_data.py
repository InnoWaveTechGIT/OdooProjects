from odoo import models, fields, api
import json                                  
from odoo import http                           
from odoo.http import request,Response          
import requests    

from email.message import EmailMessage
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
class Partners(http.Controller):
    
    @http.route('/data/categories/<int:category_id>', auth="public",csrf=False, cors='*',website=True, methods=['GET'])
    def get_category_by_id(self,category_id=None): 
        result=[]
        headers = request.httprequest.headers


        if 'Accept-Language' in headers and headers["Accept-Language"] == "ar":
            language = "ar"
        else:
            language = 'en'
        if category_id:
            categories = request.env['category.elmakan'].sudo().search([('id','=',category_id)])
            if categories:    
                try:
                
                    
                    check_image=lambda image:image if image else ''
                    for item in categories:
                        content_obj = request.env['category.content.elmakan'].sudo().search([('category_id' , '=' ,item.id)])
                        gallery_obj = request.env['category.gallery.elmakan'].sudo().search([('category_id' , '=' ,item.id)])
                        boxes_obj = request.env['category.boxes.elmakan'].sudo().search([('category_id' , '=' ,item.id)])
                        result.append({
                            'id':item.id,
                            'text':item.text,    
                            'title':item.title,             
                            'meta' : {'title_seo' :item.title_seo,
                            'description_seo' : item.description_seo,
                            'keywords_seo' : item.keywords_seo,
                            'image_alt' : item.image_alt,
                            } ,
                            'image_url':check_image(item.image_ids.image_url),
                            'content':[{'id':content.id,'text':content.text,'title':content.title,'image_url':content.image_url} for content in content_obj],
                            'gallery':[{'id':gallery.id,'text':gallery.text,'image_url':gallery.image_url} for gallery in gallery_obj],
                            'boxes':[{'id':boxes.id,'text':boxes.text,'title':boxes.title} for boxes in boxes_obj],
                            
                            
                        })
                
                
                
                    response = json.dumps({"data":result,'message' : 'All categories'}) 
                    return Response(
                        response, status=200,
                        headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])
                except Exception as e:
                    response = json.dumps({'data':[],'message':str(e)}) 
                    return Response(
                        response, status=500,
                        headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])
            else:
                if language=='en':
                    message=''
                else:
                    message=""
                response = json.dumps({"data":[],'message':message}) 
                return Response(
                    response, status=400,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]) 
        else:
            if language=='en':
                message=''
            else:
                message=""
            response = json.dumps({"data":[],'message':message}) 
            return Response(
                response, status=400,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])


    @http.route('/data/partners', auth="public",csrf=False,cors='*', website=True, methods=['GET'])
    def get_all_partners(self):
        result=[]
        headers = request.httprequest.headers 
        try:
            partner_obj=request.env['res.partner'].sudo().search([])
            if partner_obj:
                #get_title=lambda x:x.containt_ar if language=='ar' else x.containt_en
                #date=lambda x:str(x) if x!=False else "0000-00-00"
                check_image=lambda image:image if image else ''
                for item in partner_obj:
                    result.append({
                        'id':item.id,
                        'name':item.name                
                    })
            
            
            
            response = json.dumps({"data":result,'message' : 'All partners'}) 
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])
        except Exception as e:
            response = json.dumps({'data':[],'message':str(e)}) 
            return Response(
                response, status=500,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])


    @http.route('/data/contact', auth="public",csrf=False, cors='*',website=True, methods=['GET'])
    def get_all_contact(self):
        result=[]
        headers = request.httprequest.headers 
        try:
            contact_obj=request.env['contact.elmakan'].sudo().search([])
            if contact_obj:
                check_image=lambda image:image if image else ''
                for item in contact_obj:
                    result.append({
                        'id':item.id,
                        'title':item.title,
                        'text':item.text,
                        'link':item.link ,
                        'icon':item.image_url,
                        'meta' : {'title_seo' :item.title_seo,
                            'description_seo' : item.description_seo,
                            'keywords_seo' : item.keywords_seo,
                           } ,
                            
                    })
            
            
            
            response = json.dumps({"data":result,'message' : 'All contact'}) 
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])
        except Exception as e:
            response = json.dumps({'data':[],'message':str(e)}) 
            return Response(
                response, status=500,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])
        
    @http.route('/data/hero_section', auth="public",csrf=False,cors='*', website=True, methods=['GET'])
    def get_hero_section(self):
        result=[]
        headers = request.httprequest.headers 
        try:
            partner_obj=request.env['hero.section.elmakan'].sudo().search([('state','=',True)],limit=1)
            if partner_obj:
                #get_title=lambda x:x.containt_ar if language=='ar' else x.containt_en
                #date=lambda x:str(x) if x!=False else "0000-00-00"
                check_image=lambda image:image if image else ''
                for item in partner_obj:
                    result.append({
                        'id':item.id,
                        'title':item.title,
                        'meta' : {'title_seo' :item.title_seo,
                            'description_seo' : item.description_seo,
                            'keywords_seo' : item.keywords_seo,
                            } ,
                        'image_url':item.image_url   
                                     
                    })
            
            
            
            response = json.dumps({"data":result,'message' : 'Hero Section'}) 
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])
        except Exception as e:
            response = json.dumps({'data':[],'message':str(e)}) 
            return Response(
                response, status=500,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])

    
    @http.route('/Brand', auth="public",csrf=False, cors='*',website=True, methods=['GET'])
    def get_all_brands(self): 
        result=[]
        headers = request.httprequest.headers
        try:
            brand_obj=request.env['brand.elmakan'].sudo().search([('state','=',True)],order='isTopBrand desc')
            slider_obj=request.env['brand.slider.elmakan'].sudo().search([('state','=',True)])
            check_list=lambda x:x[0] if x else {} 
            check_str=lambda x:x if x else ""
            result=[
                {
                    'brandSlider': [
                        {
                            'title': check_str(slider.title),
                            'image': check_str(slider.image_url)
                        }
                        for slider in slider_obj],
                        
                    'brands': [
                        {
                            'title': check_str(brand.title),
                            'slug': check_str(brand.slug),
                            'image': check_str(brand.image_url),
                            'image_alt' : brand.image_alt,
                            'isTopBrand': brand.isTopBrand,
                            'meta' : {'title_seo' :brand.title_seo,
                            'description_seo' : brand.description_seo,
                            'keywords_seo' : brand.keywords_seo,
                            } ,
                        }
                        for brand in brand_obj]    
                }
            ]
           
            if result:
                result=result[0]
            else:
                result ={
                            "brandSlider": [
                               
                            ],
                            "brands": [
                                
                            ]
                        }   
            response = json.dumps({"brands":result,'message' : 'All Brands'}) 
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])    

        except Exception as e:
            response = json.dumps({'data':{},'message':str(e)}) 
            return Response(
                response, status=500,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])

    @http.route('/BrandBySlug/<string:slug>', auth="public",csrf=False,cors='*', website=True, methods=['GET'])
    def get_BrandBySlug(self,slug): 
        result=[]
        headers = request.httprequest.headers
        try:
            brand_obj=request.env['brand.elmakan'].sudo().search([('state','=',True)])
            # print('brand_obj',brand_obj)
            filtered_brand_objs = brand_obj.filtered(lambda rec: rec.slug == slug)
            # print('filtered_brand_objs',filtered_brand_objs)
            check_list=lambda x:x[0] if x else {} 
            check_str=lambda x:x if x else ""
            for item in filtered_brand_objs:
                result.append({
                    'image': check_str(item.image_url),
                    'title': check_str(item.title),
                    'isTopBrand': item.isTopBrand,
                    'meta' : {'title_seo' :item.title_seo,
                            'description_seo' : item.description_seo,
                            'keywords_seo' : item.keywords_seo,
                            } ,
                    'content': [
                            {
                            'title': check_str(content.title),
                            'image': check_str(content.image_url),
                            'image_alt' : content.image_alt ,
                            'text': check_str(content.text),
                            'logo':content.logo_url
                            }
                        for content in item.content_ids],
                    'description': [{
                            'title': check_str(des.title),
                            'description': check_str(des.description),
                            'text': check_str(des.text)
                        } for des in item.description_ids],  
                    "gallery": [
                            {
                            "image": gallery.image_url,
                            'image_alt' : gallery.image_alt,
                            "text": gallery.text
                            }
                        for gallery in item.gallery_ids]      
                })
            if result:
                result=result[0]
            else:
                result = {
                        "image": "",
                        "title": "",
                        "isTopBrand": False,
                        "content": [],
                        "description": [],
                        "gallery": []
                    }
                
            response = json.dumps({"brand":result,'message' : 'Brand Details'}) 
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])    

        except Exception as e:
            response = json.dumps({'data':{},'message':str(e)}) 
            return Response(
                response, status=500,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])


    @http.route('/Gatergories', auth="public",csrf=False,cors='*', website=True, methods=['GET'])
    def get_all_Gatergories(self): 
        result=[]
        headers = request.httprequest.headers
        try:
            category_obj=request.env['category.elmakan'].sudo().search([('state','=',True)])
            check_list=lambda x:x[0] if x else {} 
            check_str=lambda x:x if x else ""
            for item in category_obj:
                result.append({
                    'meta' : {'title_seo' :item.title_seo,
                            'description_seo' : item.description_seo,
                            'keywords_seo' : item.keywords_seo,
                            } ,
                    'image': check_str(item.image_url),
                    'image_alt' : item.image_alt,
                    'title': check_str(item.title),
                    'text': check_str(item.text),
                    'slug': check_str(item.slug)
                })
                
            response = json.dumps({"categories":result,'message' : 'All Categories'}) 
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])    

        except Exception as e:
            response = json.dumps({'data':{},'message':str(e)}) 
            return Response(
                response, status=500,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])                


    @http.route('/CategoriesBySlug/<string:slug>', auth="public",csrf=False,cors='*', website=True, methods=['GET'])
    def get_CategoriesBySlug(self,slug): 
        result=[]
        headers = request.httprequest.headers
        try:
            category_obj=request.env['category.elmakan'].sudo().search([('state','=',True)])
            filtered_category_obj = category_obj.filtered(lambda rec: rec.slug == slug)
            check_list=lambda x:x[0] if x else {} 
            check_str=lambda x:x if x else ""
            for item in filtered_category_obj:
                brands = request.env['brand.elmakan'].sudo().search([('categ_id','in',[item.id])])
                result.append({
                    
                    'title': check_str(item.title),
                    'image': check_str(item.image_url),
                    'image_alt' : item.image_alt,
                    'text': check_str(item.text),
                    'meta' : {'title_seo' :item.title_seo,
                            'description_seo' : item.description_seo,
                            'keywords_seo' : item.keywords_seo,
                            } ,
                    'content': [
                            {
                            'title': check_str(content.title),
                            'image': check_str(content.image_url),
                            'image_alt' : content.image_alt,
                            'text': check_str(content.text)
                            }
                        for content in item.content_ids], 
                    "gallery": [
                            {
                            "image": gallery.image_url,
                            'image_alt' : gallery.image_alt,
                            "text": gallery.text
                            }
                        for gallery in item.gallery_ids], 
                        "brands": [
                            {
                            "title": brand.title,
                            "slug": brand.slug ,
                            "image": brand.image_url ,
                            'image_alt' : brand.image_alt,
                            "isTopBrand": brand.isTopBrand ,
                            }
                        for brand in brands], 
                      
                    'boxes': {
                        "title":check_str(item.title_in_section_boxes),
                        "boxedData":[{ 'title': box.title, 'text': box.text } for box in item.boxes_ids] 
                    }
                           
                })
            if result:
                result=result[0]
            else:
                result = {
                            "title": "",
                            "image": "",
                            "text": "",
                            "content": [
                                
                            ],
                            "gallery": [
                                
                            ],
                            'boxes': {
                                "title":"",
                                "boxedData":[] 
                            }
                        }
                
            response = json.dumps({"category":result,'message' : 'Category Details'}) 
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])    

        except Exception as e:
            response = json.dumps({'data':{},'message':str(e)}) 
            return Response(
                response, status=500,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])


    @http.route('/About', auth="public",csrf=False,cors='*', website=True, methods=['GET'])
    def get_About(self): 
        result=[]
        headers = request.httprequest.headers
        try:
            about_obj=request.env['about.elmakan'].sudo().search([('state','=',True)],limit=1)
            check_list=lambda x:x[0] if x else {} 
            check_str=lambda x:x if x else ""
            for item in about_obj:
                result.append({
                    'text':check_str(item.text),
                    'video':check_str(item.video_url),
                    'meta' : {'title_seo' :item.title_seo,
                            'description_seo' : item.description_seo,
                            'keywords_seo' : item.keywords_seo,
                            } ,
                    "hero": [
                        {
                            'image':check_str(hero.image_url),
                            'image_alt' : hero.image_alt,
                            'title':check_str(hero.title),
                            'text': check_str(hero.text)
                        }
                        for hero in item.hero_ids],
                    'content': [
                            {
                            'image': check_str(content.image_url),
                            'image_alt' : content.image_alt,
                            'title': check_str(content.title),
                            'text': check_str(content.text)
                            }
                        for content in item.content_ids], 
                    "gallery": [
                            {
                            "image": gallery.image_url,
                            'image_alt' : gallery.image_alt,
                            "text": gallery.text,
                            "popup": {
                                'title': check_str(gallery.title_popup),
                                'address': check_str(gallery.address_popup),
                                'locationMapUrl': check_str(gallery.locationMapUrl_popup),

                                'phone': check_str(gallery.phone_popup),
                                'email': check_str(gallery.email_popup)
                                }
                            }
                        for gallery in item.gallery_ids],   
                        
                })
            if result:
                result=result[0]
            else:
                result={
                    "text": "",
                    "video": "",
                    'meta' : {'title_seo' :'',
                            'description_seo' : '',
                            'keywords_seo' : ''} ,
                    "hero": [
                        
                    ],
                    "content": [
                        
                    ],
                    "gallery": [
                       
                    ]
                }    
            response = json.dumps({"aboutUs":result,'message' : 'AboutUs Details'}) 
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])    

        except Exception as e:
            response = json.dumps({'data':{},'message':str(e)}) 
            return Response(
                response, status=500,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]) 


    @http.route('/Home', auth="public",csrf=False,cors='*', website=True, methods=['GET'])
    def get_Home(self): 
        result=[]
        headers = request.httprequest.headers
        try:
            home_obj=request.env['home.elmakan'].sudo().search([('state','=',True)],limit=1)
            check_list=lambda x:x[0] if x else {} 
            check_str=lambda x:x if x else ""
            for item in home_obj:
                result.append({
                    'meta' : {'title_seo' :item.title_seo,
                            'description_seo' : item.description_seo,
                            'keywords_seo' : item.keywords_seo,
                            } ,
                    "hero": check_list([{
                        "title": check_str(hero.title),
                        "image": check_str(hero.image_url),
                        'image_alt' : hero.image_alt,
                    } for hero in item.hero_id]),
                    "about": check_list([{
                        "text": check_str(about.text),
                        "video": check_str(about.video_url)
                    } for about in item.about_id]),
                    "features": [
                        {
                        "title": check_str(feature.title),
                        "link":check_str(feature.link),
                        "image": check_str(feature.image_url),
                        'image_alt' : feature.image_alt,
                        "slug": check_str(feature.slug)
                        }
                    for feature in [y for y in item.label_content_ids]+[x for x in item.features_ids]],
                    "content": [
                        {
                        "title": check_str(content.title),
                        "text": check_str(content.text),
                        "link": check_str(content.link)
                        }
                    for content in item.content_ids]
                    
                        
                })
            if result:
                result=result[0]
            else:
                result={
                    'meta' : {'title_seo' :'',
                            'description_seo' : '',
                            'keywords_seo' : '',
                            } ,
                    "hero": {
                        "title": "",
                        "image": "",
                        'image_alt' : ''
                    },
                    "about": {
                        "text": "",
                        "video" : ""
                    },
                    "features": [
                        
                    ],
                    "content": [
                        
                    ]
                }    
            response = json.dumps({"Home":result,'message' : 'Home Details'}) 
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])    

        except Exception as e:
            response = json.dumps({'data':{},'message':str(e)}) 
            return Response(
                response, status=500,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])                        




    @http.route('/Label', auth="public",csrf=False,cors='*', website=True, methods=['GET'])
    def get_Label(self): 
        result=[]
        headers = request.httprequest.headers
        try:
            label_obj=request.env['labelcontent.elmakan'].sudo().search([],limit=1)
            check_list=lambda x:x[0] if x else {} 
            check_str=lambda x:x if x else ""
            for item in label_obj:
                result.append({
                    'title':check_str(item.title),
                    'text':check_str(item.text),
                    'meta' : {'title_seo' :item.title_seo,
                            'description_seo' : item.description_seo,
                            'keywords_seo' : item.keywords_seo,
                            } ,
                    'content':[{
                        'title':check_str(content.title),
                        'image':check_str(content.image_url),
                        'image_alt' : content.image_alt,
                        'text':check_str(content.text)
                    } for content in item.content_ids],
                    'slider':[{
                        'title':check_str(slider.title),
                        'image':check_str(slider.image_url),
                        'image_alt' : slider.image_alt,
                        'text':check_str(slider.text)
                    } for slider in item.slider_ids],
                    'boxes':[{
                        'title':check_str(boxes.title),
                        'text':check_str(boxes.text)
                    } for boxes in item.box_ids],

                    
                        
                })
            if result:
                result=result[0]
            else:
                result={
                        "title": "",
                        "text": "",
                        'meta' : {'title_seo' :'',
                            'description_seo' : '',
                            'keywords_seo' : '',
                            } ,
                        "content": [],
                        "slider": [],
                        "boxes": []
                    }    
            response = json.dumps({"labelContent":result,'message' : 'Label Details'}) 
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])    

        except Exception as e:
            response = json.dumps({'data':{},'message':str(e)}) 
            return Response(
                response, status=500,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])  

    @http.route('/feature/<string:slug>', auth="public",csrf=False,cors='*', website=True, methods=['GET'])
    def get_feature_by_slug(self,slug): 
        result=[]
        data = []
        label=False
        headers = request.httprequest.headers
        try:
            check_list=lambda x:x[0] if x else {} 
            check_str=lambda x:x if x else ""
            check_label_slider=lambda x:x.slider_ids if label else []
            check_label_box = lambda x:x.box_ids if label else []
            feature_obj=request.env['feature.elmakan'].sudo().search([])
            filtered_feature_obj = feature_obj.filtered(lambda rec: rec.slug == slug)
            print('filtered_feature_obj >> ' , filtered_feature_obj)
            label_obj=request.env['labelcontent.elmakan'].sudo().search([])
            filtered_label_obj = label_obj.filtered(lambda rec: rec.slug == slug)
            if filtered_feature_obj:
                data=filtered_feature_obj
                label=False
            elif filtered_label_obj:
                data=filtered_label_obj
                label=True
            else:
                data=[]    
            for item in data:
                result.append({
                    'title':check_str(item.title),
                    'text':check_str(item.text),
                    'link':check_str(item.link),
                    'meta' : {'title_seo' :item.title_seo,
                            'description_seo' : item.description_seo,
                            'keywords_seo' : item.keywords_seo,
                            } ,
                    'content':[{
                        'text':check_str(content.text),
                        'title':check_str(content.title),
                        'link':check_str(content.link),
                        'image':check_str(content.image_url),
                        'image_alt' : content.image_alt
                       
                    } for content in item.content_ids],
                    "slider": [{
                        'title':check_str(slider.title),
                        'image':check_str(slider.image_url),
                        'image_alt' : slider.image_alt,
                        'text':check_str(slider.text)
                    } for slider in check_label_slider(item)],
                    "boxes": [{
                        'title':check_str(boxes.title),
                        'text':check_str(boxes.text)
                    } for boxes in check_label_box(item)]
                    
                    
                        
                })
            if result:
                result=result[0]
            else:
                result={
                        "title": "",
                        "text": "",
                        "link":"",
                        'meta' : {'title_seo' :'',
                            'description_seo' : '',
                            'keywords_seo' : '',
                           } ,
                        "content": [],
                        "slider": [],
                        "boxes": []
                    }   
            response = json.dumps({"data":result,'message' : f' {slug} Details'}) 
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])    

        except Exception as e:
            response = json.dumps({'data':{},'message':str(e)}) 
            return Response(
                response, status=500,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])


    @http.route('/client', auth="public",csrf=False,cors='*', website=True, methods=['GET'])
    def get_client(self): 
        result=[]
        headers = request.httprequest.headers
        try:
            client_obj=request.env['client.elmakan'].sudo().search([('state','=',True)],limit=1)
            check_list=lambda x:x[0] if x else {} 
            check_str=lambda x:x if x else ""
            for item in client_obj:
                result.append({
                    'title':check_str(item.title),
                    'text':check_str(item.text),
                    'meta' : {'title_seo' :item.title_seo,
                            'description_seo' : item.description_seo,
                            'keywords_seo' : item.keywords_seo,
                            } ,
                    'companies':[{
                        'key':check_str(companies.key),
                        'value':check_str(companies.value),
                        
                    } for companies in item.company_ids],
                    
                    
                        
                })
            if result:
                result=result[0]
            else:
                result={
                    "title": "",
                    "text": "",
                    'meta' : {'title_seo' :'',
                            'description_seo' : ''} ,
                    "companies": [
                        
                    ]
                }    
            response = json.dumps({"client":result,'message' : f' Client Details'}) 
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])    

        except Exception as e:
            response = json.dumps({'data':{},'message':str(e)}) 
            return Response(
                response, status=500,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])  


    @http.route('/form/contact_us', auth="public",csrf=False,cors='*', website=True, methods=['POST'])
    def post_form_contact_us(self,**kw): 
        result=[]
        headers = request.httprequest.headers
        email_obj = request.env['mail.elmakan'].sudo().search([],limit=1)
        if email_obj:
            if email_obj.company_email and email_obj.app_key:
                sender = email_obj.company_email
                password = email_obj.app_key
                username = email_obj.company_email
            else:
                response = json.dumps({"data":[],'message' : 'sender email or app key not set '}) 
                return Response(
                    response, status=400,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])        
        recipients = []
        subject = 'Submit Form'
        body_email = f"""
                        name : {kw.get('name','')}
                        email : {kw.get('email','')}
                        phone : {kw.get('phone','')}
                        company name : {kw.get('company_name','')}
                        message : {kw.get('message','')}
                    """
        try:
            recipients.append(email_obj.contact_us_email)
            # recipients=['info@almakaan.com']
            recipients.append(kw.get('email'))
            msg = MIMEMultipart()
            msg['From'] = sender
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject
            msg.attach(MIMEText(body_email, 'plain'))

            # Log in to Gmail's SMTP server
            smtp_server = 'smtp.gmail.com'
            smtp_port = 587

            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            status_code, response =server.login(username, password)

            # Send the email
            text = msg.as_string()
            server.sendmail(sender, recipients, text)

            # Close the connection to the SMTP server
            server.quit()
            if status_code==235:
                
                contact_obj=request.env['contact.us.elmakan'].sudo().search([('state','=',True)],limit=1)
                print('contact_obj',contact_obj)
                if contact_obj:
                    pass
                else:
                    response = json.dumps({"data":[],'message' : 'not have contact us record '}) 
                    return Response(
                        response, status=404,
                        headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])
                kw['contactus_id']=contact_obj.id      
                form_obj=request.env['form.content.us.elmakan'].sudo().create(kw)
                lead_obj = request.env['crm.lead'].sudo().create({
                    'name': kw.get('name'),
                    'email_from': kw.get('email'),
                    'phone': kw.get('phone'),
                    'partner_name': kw.get('company_name'),
                    'description': kw.get('message'),
                })
                response = json.dumps({"data":[],'message' : 'The form has been sent'}) 
                return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])    

        except Exception as e:
            response = json.dumps({'data':{},'message':'A technical error occurred, please try again'}) 
            return Response(
                response, status=500,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]) 



    @http.route('/form/feature', auth="public",csrf=False,cors='*', website=True, methods=['POST'])
    def post_form_feature(self,**kw): 
        result=[]
        headers = request.httprequest.headers


        email_obj = request.env['mail.elmakan'].sudo().search([],limit=1)
        if email_obj:
            if email_obj.company_email and email_obj.app_key:
                sender = email_obj.company_email
                password = email_obj.app_key
                username = email_obj.company_email

            else:
                response = json.dumps({"data":[],'message' : 'sender email or app key not set '}) 
                return Response(
                    response, status=400,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])        
        recipients = []
        subject = 'Submit Form'
        body_email = f"""
                        Thanks for reaching out! We'll be in touch within 24 hours.
                    """
        

        
        try:
            if 'feature' in kw:
                feature_obj=request.env['feature.mail.elmakan'].sudo().search([])
                feature_id=feature_obj.filtered(lambda rec:rec.feature_id.slug == kw.get('feature'))
                
                if feature_id:
                    pass
                else:
                    response = json.dumps({"data":[],'message' : f"the required feature {kw.get('feature')} not set in email setting"}) 
                    return Response(
                        response, status=400,
                        headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]) 
                recipients.append(kw.get('email'))
                if kw.get('feature'):
                    
                    recipients.append(feature_id.email)
                    
                else:
                    response = json.dumps({"data":[],'message' : 'slug feature is required'}) 
                    return Response(
                        response, status=400,
                        headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]) 
            else:
                response = json.dumps({"data":[],'message' : 'slug feature is required'}) 
                return Response(
                    response, status=400,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])                      

            msg = MIMEMultipart()
            msg['From'] = sender
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject
            msg.attach(MIMEText(body_email, 'plain'))

            # Log in to Gmail's SMTP server
            smtp_server = 'smtp.gmail.com'
            smtp_port = 587

            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            status_code, response =server.login(username, password)

            # Send the email
            text = msg.as_string()
            server.sendmail(sender, recipients, text)

            # Close the connection to the SMTP server
            server.quit()
            if status_code==235:
                # feature_obj=request.env['feature.elmakan'].sudo().search([('slug','=',kw.get('feature'))])
                # print('feature_obj',feature_obj)
                kw['feature_id']=feature_id.feature_id.id
                del kw['feature']
                save_form_obj=request.env['form.feature.elmakan'].sudo().create(kw)
                response = json.dumps({"data":[],'message' : 'The form has been sent'}) 
                return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]) 
            else:
                response = json.dumps({"data":[],'message' : 'The form was not sent. A technical error occurred'}) 
                return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])         

        except Exception as e:
            response = json.dumps({'data':{},'message':str(e)}) 
            return Response(
                response, status=500,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]) 


    @http.route('/contactus', auth="public",csrf=False,cors='*', website=True, methods=['GET'])
    def get_contactus_details(self): 
        result=[]
        headers = request.httprequest.headers
        try:
            client_obj=request.env['contact.us.elmakan'].sudo().search([('state','=',True)],limit=1)
            check_list=lambda x:x[0] if x else {} 
            check_str=lambda x:x if x else ""
            for item in client_obj:
                result.append({
                    'meta' : {'title_seo' :item.title_seo,
                            'description_seo' : item.description_seo,
                            'keywords_seo' : item.keywords_seo,
                            } ,
                    "location": [
                        {
                            "region":check_str(location.region),
                            "city": check_str(location.city),
                            "address": check_str(location.address),

                            "phone": check_str(location.phone),
                            "fax": check_str(location.fax),

                            "poBoxNumber":check_str(location.poBoxNumber),
                            "poBoxLocation": check_str(location.poBoxLocation),

                            "email": check_str(location.email)
                        }
                        for location in item.location_ids],

                    "ourAgents": [
                        {
                            "region": check_str(ourAgents.region),
                            "name": check_str(ourAgents.name),
                            "address": check_str(ourAgents.address),
                            "phone": check_str(ourAgents.phone),
                            "fax": check_str(ourAgents.fax),
                            "mobile": check_str(ourAgents.mobile),
                            "email": check_str(ourAgents.email)
                        }
                        for ourAgents in item.ourAgents_ids],

                        "contact_us" :{
                            'Phone' : item.Phone ,
                            'email' : item.email 
                        }
                    
                    
                        
                })
            if result:
                result=result[0]
            else:
                result={
                    'meta' : {'title_seo' :'',
                            'description_seo' : '',
                            'keywords_seo' : '',
                            } ,
                    "location": [
                        
                    ],
                    "ourAgents": [
                       
                    ]
                }    
            response = json.dumps({"contact":result,'message' : f' Contact US Details'}) 
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])    

        except Exception as e:
            response = json.dumps({'data':{},'message':str(e)}) 
            return Response(
                response, status=500,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])  


    @http.route('/blog', auth="public",csrf=False, website=True, methods=['GET'])
    def get_all_details_blog(self): 
        result=[]
        headers = request.httprequest.headers
        try:
            blog_obj=request.env['blog.almakan'].sudo().search([('state','=',True)])
            check_list=lambda x:x[0] if x else {} 
            check_str=lambda x:x if x else ""
            for item in blog_obj:
                result.append({
                    'image': check_str(item.image_url),
                    'image_alt' : item.image_alt,
                    'title': check_str(item.title),
                    'content':check_str(item.content),
                    'slug': check_str(item.slug),
                    'meta' : {'title_seo' :item.title_seo,
                            'description_seo' : item.description_seo,
                            'keywords_seo' : item.keywords_seo,
                            } ,
                    'tag': check_str(item.tag)
                })
             
            response = json.dumps({"blog":result,'message' : 'All Blogs'}) 
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])    

        except Exception as e:
            response = json.dumps({'data':{},'message':str(e)}) 
            return Response(
                response, status=500,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])

    @http.route('/blog/<string:slug>', auth="public",csrf=False, website=True, methods=['GET'])
    def get_blogBySlug_details(self,slug): 
        result=[]
        headers = request.httprequest.headers
        try:
            blog_obj=request.env['blog.almakan'].sudo().search([('state','=',True)])
            filtered_blog_obj = blog_obj.filtered(lambda rec: rec.slug == slug)
            check_list=lambda x:x[0] if x else {} 
            check_str=lambda x:x if x else ""
            for item in filtered_blog_obj:
                result.append({
                    'image': check_str(item.image_url),
                    'image_alt' : item.image_alt,
                    'title': check_str(item.title),
                    'content':check_str(item.content),
                    'meta' : {'title_seo' :item.title_seo,
                            'description_seo' : item.description_seo,
                            'keywords_seo' : item.keywords_seo,
                            } ,
                })
            if result:
                result=result[0]
            else:
                result={
                            "image": "",
                            "title": "",
                            'meta' : {'title_seo' :'',
                            'description_seo' : '',
                            'keywords_seo' : '',
                            'image_alt' : ''} ,
                            "content": ""
                        }   
            response = json.dumps({"blogDetails":result,'message' : 'Blog Details'}) 
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])    

        except Exception as e:
            response = json.dumps({'data':{},'message':str(e)}) 
            return Response(
                response, status=500,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])            