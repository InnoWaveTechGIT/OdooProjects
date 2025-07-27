from odoo import http
import json
from odoo.http import request ,Response
from odoo.tools import config
import requests
from urllib.parse import urljoin, urlencode


class BannerController(http.Controller):


    url = 'https://www.alnasaem.com' 
    @http.route('/api/banner', auth='public', methods=['GET'], csrf=False, type='http')
    def get_banner_images(self, **params):
        banner_images = []

        # Retrieve the banner data from your Odoo model
        banners = request.env['banner.nasaem'].sudo().search([])

        # Extract the image URLs from the banner data
        for banner in banners:
            banner_images.append({
                'id': banner.id,
                'category_id': banner.id,
                'image':banner.image_url,
                'for_register' : banner.for_register ,
                
                # Add other fields as required
            })
            image_url = banner.image_url
            banner_images.append(image_url)

        # Return the image URLs as a JSON response
        response = json.dumps({'data': banner_images , 'is_success' :True})
        return Response(
            response, status=200, content_type='application/json'
        )


    @http.route('/api/home', auth='public', methods=['GET'], csrf=False, type='http')
    def get_home_data(self, **params):
        # Retrieve banner images from the "/api/banner" API
        language = request.httprequest.headers.get('Accept-Language', 'en_US').split(',')[0]
        banners = request.env['banner.nasaem'].sudo().with_context(lang=language).search([('banner_language', '=', language)])
        banner_images= []
        # Extract the image URLs from the banner data
        for banner in banners:
            banner_images.append({
                'id': banner.id,
                'category_id': banner.id,
                'image':banner.image_url,
                'for_register' : banner.for_register ,
                
                # Add other fields as required
            })

        category_model = request.env['product.public.category']
        brands = category_model.sudo().with_context(lang=language).search([('x_studio_is_brand', '=', False), ('visible_website', '=', True)])
        result = []
        # Process the brands as needed
        for brand in brands:
            sub_cat =  category_model.search_count([('parent_id', '=', brand.id)])
            result.append(
                        {
                            'id':brand.id,
                            'name':brand.name,
                            'image':self.url + '/web/image?' + 'model=product.public.category&id=' + str(brand.id) + '&field=image_1920',
                            'sub_categories' : True if sub_cat else False
                            })
        category_model = request.env['product.public.category']
        brands = category_model.sudo().with_context(lang=language).search([('x_studio_is_brand', '=', True)])
        result1 = []
        try:
            # Process the brands as needed
            for brand in brands:
                sub_cat =  category_model.search_count([('parent_id', '=', brand.id)])
                result1.append(
                            {
                                'id':brand.id,
                                'name':brand.name,
                                'image':self.url + '/web/image?' + 'model=product.public.category&id=' + str(brand.id) + '&field=image_1920',
                                'sub_categories' : True if sub_cat else False
                                })
        except Exception as e:
                response = json.dumps({'data':[],'message':str(e) , 'is_success' :False}) 
                return Response(
                    response, status=500,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])

        # Process and combine the data from all APIs as needed
        home_data = {
            'banners': banner_images,
            'categories': result,
            'brands': result1,
            'banner_1' : {
                'categ_id' : 3818,
                'image' : 'https://www.alnasaem.com/web/image/32336-55cd0884/11-2.jpg' if language == 'ar_001' else 'https://www.alnasaem.com/web/image/32327-69e9b5c2/11.jpg'  ,
                'title' :  "عروضات تصل إلى"  if language == 'ar_001' else 'OFFERS UP TO' ,
                'paragraph' : "اكتشف عروضنا الحصرية"  if language == 'ar_001' else 'Explore Our Exclusive Offers'
            },
            'banner_2' : {
                'categ_id' : 3610 ,
                'image' : 'https://www.alnasaem.com/web/image/32335-0fc3cbfb/22-2.jpg' if language == 'ar_001' else 'https://www.alnasaem.com/web/image/32354-22539208/22.jpg',
                'title' : "تصفية"  if language == 'ar_001' else 'CLEARANCE',
                'paragraph' : "عروضات خاصة على الصناديق التالفة"  if language == 'ar_001' else 'SPECIAL DISCOUNTS on defected boxes'
            }
            
        }

        response = json.dumps({'data': home_data, 'is_success': True})
        return Response(response, status=200, content_type='application/json')