{
    "name": "Product Custom Details",
    "description": """""",
    "version": "18.0.0.0.0",
    "license": "LGPL-3",
    "author": "Arados Software ",
    "website": "https://arados-so.com",
    "depends": ["base",'product' , 'stock_delivery'],
    "data": [
        'security/ir.model.access.csv',
        # 'static/src/js/forcasting_button.js',
        # 'static/src/xml/month_calculation_popup.xml',
        'view/product_template.xml',




    ],


    'installable': True,
    'application': False,
    'auto_install': False,



}
