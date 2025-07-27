import xlrd
import xmlrpc.client


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
import re
import socket
from os import path
import random
import string
import xmlrpc.client
import math
import pandas as pd
import io
import base64
class Payments(http.Controller):
    url = 'http://localhost:8090'
    db = 'sharbel1'
    username ='admin'
    password = 'admin'
    def create_or_replace_categories(self ,category_names):
        parent_id = False
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})

        for category_name in category_names:
            category_id = models.execute_kw(self.db, uid, self.password, 'product.category', 'search',
                                            [[('name', '=', category_name), ('parent_id', '=', parent_id)]])
            if category_id:
                parent_id = category_id[0]
            else:
                category_data = {
                    'name': category_name,
                    'parent_id': parent_id,
                }
                parent_id = models.execute_kw(self.db, uid, self.password, 'product.category', 'create', [category_data])
        return parent_id
    @http.route('/script/all',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_all_data_for_product(self, **kw):
                

        

        # Excel file details
        excel_file_path = '/home/ali/Porceletta Single.xlsx'
        sheet_name = 'Export'  # Modify this according to your Excel file structure

        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})

        if uid:

            # Read Excel file using pandas
            try:
                data_frame = pd.read_excel(excel_file_path, sheet_name=sheet_name)
            except FileNotFoundError:
                print("Excel file not found.")
                exit()
            last_product_id = False
            attribute_column = 'Attibute '
            attribute_value_column = 'Attibute value'
            # Iterate over each row in the Excel file
            for index, row in data_frame.iterrows():
                if row['SKU']:
                    # Extract product data from the Excel row
                    product_data = {
                        'name': row['Label'] if pd.notnull(row['Label']) else '',
                        'default_code': row['SKU'] if pd.notnull(row['SKU']) else '',
                        'list_price': row['UPC'] if isinstance(row['UPC'], (int, float)) and not math.isnan(row['UPC']) else 0.0,
                        # Add more fields as per your Excel file structure
                    }

                    # Handle categories
                    categories = str(row['Categories'])  # Convert to string to handle float values
                    if categories:
                        categories = categories.split('/')
                        category_id = self.create_or_replace_categories(categories)
                        product_data['categ_id'] = category_id

                    # Handle image URL
                    if "Thumbnail" in row:
                        thumbnail_value = row["Thumbnail"]
                        if isinstance(thumbnail_value, str) and thumbnail_value.strip().lower() != "nan":
                            image_url = thumbnail_value
                            try:
                                image_response = requests.get(image_url)
                                if image_response.status_code == 200:
                                    image_data = io.BytesIO(image_response.content)
                                    product_data["image_1920"] = base64.b64encode(image_data.getvalue()).decode()
                                else:
                                    print(f"Failed to retrieve image from URL: {image_url}")
                            except requests.exceptions.MissingSchema:
                                print(f"Invalid image URL: {image_url}")
                        elif isinstance(thumbnail_value, (int, float)) and not math.isnan(thumbnail_value):
                            print(f"Invalid thumbnail value in the row: {thumbnail_value}")
                        else:
                            print("Invalid or missing Thumbnail value in the row.")
                        

                    # Create the product record in Odoo
                    if all(product_data.values()):
                        product_id = models.execute_kw(self.db, uid, self.password, 'product.template', 'create', [product_data])
                        print(f"Product created with ID: {product_id}")
                    else:
                        print("Skipping row due to missing or invalid values.")

                    # Update the last created product ID
                    last_product_id = product_id
                    if row[attribute_column] and row[attribute_value_column]:
                        attribute_name = row[attribute_column]
                        attribute_value = row[attribute_value_column]

                        attribute_id = models.execute_kw(self.db, uid, self.password, 'product.attribute', 'search',
                                                        [[('name', '=', attribute_name)]])
                        if attribute_id:
                            
                                if attribute_value:
                                    attribute_value_id = models.execute_kw(self.db, uid, self.password, 'product.attribute.value', 'search',
                                                                            [[('attribute_id', '=', attribute_id[0]),
                                                                            ('name', '=', attribute_value)]])
                                    if attribute_value_id:
                                        models.execute_kw(self.db, uid, self.password, 'product.template', 'write',
                                                        [[last_product_id], {
                                                            'attribute_line_ids': [(0, 0, {
                                                                'attribute_id': attribute_id[0],
                                                                'value_ids': [(6, 0, attribute_value_id)],
                                                            })]
                                                        }])
                                    else:
                                        attribute_value_data = {
                                            'name': attribute_value,
                                            'attribute_id': attribute_id[0],
                                        }
                                        attribute_value_id = models.execute_kw(self.db, uid, self.password, 'product.attribute.value',
                                                                                'create', [attribute_value_data])
                                        models.execute_kw(self.db, uid, self.password, 'product.template', 'write',
                                                        [[last_product_id], {
                                                            'attribute_line_ids': [(0, 0, {
                                                                'attribute_id': attribute_id[0],
                                                                'value_ids': [(6, 0, [attribute_value_id])],
                                                            })]
                                                        }])
                                else:
                                    print(f"Skipping attribute '{attribute_name}' for product '{product_data['name']}' due to missing value.")
                elif last_product_id:
                    # Handle attributes
                    
                    attribute_id = models.execute_kw(self.db, uid, self.password, 'product.attribute', 'search',
                                                    [[('name', '=', attribute_name)]])
                    if attribute_id:
                        attribute_value_id = models.execute_kw(self.db, uid, self.password, 'product.attribute.value', 'search',
                                                                [[('attribute_id', '=', attribute_id[0]),
                                                                ('name', '=', attribute_value)]])
                        if attribute_value_id:
                            models.execute_kw(self.db, uid, self.password, 'product.template', 'write', [[last_product_id], {
                                'attribute_line_ids': [(0, 0, {
                                    'attribute_id': attribute_id[0],
                                    'value_ids': [(6, 0, attribute_value_id)],
                                })]
                            }])
                        else:
                            attribute_value_data = {
                                'name': attribute_value,
                                'attribute_id': attribute_id[0],
                            }
                            attribute_value_id = models.execute_kw(self.db, uid, self.password, 'product.attribute.value',
                                                                    'create', [attribute_value_data])
                            models.execute_kw(self.db, uid, self.password, 'product.template', 'write', [[last_product_id], {
                                'attribute_line_ids': [(0, 0, {
                                    'attribute_id': attribute_id[0],
                                    'value_ids': [(6, 0, [attribute_value_id])],
                                })]
                            }])
                    else:
                        attribute_data = {
                            'name': attribute_name,
                            'value_ids': [(0, 0, {'name': attribute_value})],
                        }
                        attribute_id = models.execute_kw(self.db, uid, self.password, 'product.attribute', 'create', [attribute_data])
                        models.execute_kw(self.db, uid, self.password, 'product.template', 'write', [[last_product_id], {
                            'attribute_line_ids': [(0, 0, {
                                'attribute_id': attribute_id,
                                'value_ids': False,
                            })]
                        }])

            print("Import completed successfully.")


            print("Import completed successfully.")
        else:
            print("Failed to authenticate with Odoo.")


# # Excel file path
# excel_file_path = '/path/to/excel/file.xlsx'

# # Connect to the Odoo server
# common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
# uid = common.authenticate(db, username, password, {})

# # Open a connection to the Odoo API
# models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

# # Open the Excel file
# workbook = xlrd.open_workbook(excel_file_path)
# sheet = workbook.sheet_by_index(0)  # Assuming the data is on the first sheet

# # Get column indexes for the required fields in the Excel file
# name_col_index = 0
# description_col_index = 1
# price_col_index = 2

# # Iterate over rows in the Excel file, starting from the second row (row index 1)
# for row_index in range(1, sheet.nrows):
#     name = sheet.cell_value(row_index, name_col_index)
#     description = sheet.cell_value(row_index, description_col_index)
#     price = sheet.cell_value(row_index, price_col_index)

#     # Create a new product template in Odoo using the data from the Excel file
#     product_template = models.execute_kw(db, uid, password, 'product.template', 'create', [{
#         'name': name,
#         'description': description,
#         'list_price': price,
#     }])

#     print(f"Product template created with ID: {product_template}")




# import xlrd
# from odoo import models, fields, api

# class ProductImport(models.TransientModel):
#     _name = 'product.import'

#     file = fields.Binary(string='Excel File')

#     @api.multi
#     def import_products(self):
#         excel_file = xlrd.open_workbook(file_contents=self.file)
#         sheet = excel_file.sheet_by_index(0)  # Assuming the data is on the first sheet

#         category_mapping = {}

#         for row_index in range(1, sheet.nrows):  # Start from the second row (index 1)
#             sku = sheet.cell_value(row_index, 0)
#             label = sheet.cell_value(row_index, 1)
#             thumbnail_url = sheet.cell_value(row_index, 2)
#             product_name = sheet.cell_value(row_index, 3)
#             tags = sheet.cell_value(row_index, 4)
#             category_name = sheet.cell_value(row_index, 5)
#             origin = sheet.cell_value(row_index, 6)
#             hs_code = sheet.cell_value(row_index, 7)
#             unit = sheet.cell_value(row_index, 8)
#             upc = sheet.cell_value(row_index, 9)
#             retail_price = sheet.cell_value(row_index, 10)

#             # Create or update category
#             category_id = category_mapping.get(category_name)
#             if not category_id:
#                 category = self.env['product.category'].search([('name', '=', category_name)], limit=1)
#                 if category:
#                     category_id = category.id
#                     category_mapping[category_name] = category_id
#                 else:
#                     category = self.env['product.category'].create({'name': category_name})
#                     category_id = category.id
#                     category_mapping[category_name] = category_id

#             attributes = []
#             attribute_values = []

#             # Extract attributes and attribute values
#             attribute_row_index = row_index
#             while attribute_row_index < sheet.nrows:
#                 attribute = sheet.cell_value(attribute_row_index, 11)
#                 attribute_value = sheet.cell_value(attribute_row_index, 12)

#                 if attribute and attribute_value:
#                     attributes.append(attribute)
#                     attribute_values.append(attribute_value)

#                 attribute_row_index += 1

#             # Create or update the product template in Odoo
#             product_template = self.env['product.template'].search([('default_code', '=', sku)], limit=1)
#             if product_template:
#                 product_template.write({
#                     'name': product_name,
#                     'list_price': retail_price,
#                     'categ_id': category_id,
#                     'attribute_line_ids': [(0, 0, {
#                         'attribute_id': self.env['product.attribute'].search([('name', '=', attribute_name)], limit=1).id,
#                         'value_ids': [(0, 0, {
#                             'name': attribute_value,
#                         })],
#                     }) for attribute_name, attribute_value in zip(attributes, attribute_values)],
#                 })
#             else:
#                 self.env['product.template'].create({
#                     'default_code': sku,
#                     'name': product_name,
#                     'list_price': retail_price,
#                     'categ_id': category_id,
#                     'attribute_line_ids': [(0, 0, {
#                         'attribute_id': self.env['product.attribute'].search([('name', '=', attribute_name)], limit=1).id,
#                         'value_ids': [(0, 0, {
#                             'name': attribute_value,
#                         })],
#                     }) for attribute_name, attribute_value in zip(attributes, attribute_values)],
#                 })