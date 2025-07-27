{
    "name": "MRD Forcasting",
    "description": """This Module calculates forecasted minimum stock levels based on  sales averages and consider purchase quantities to optimize ordering decisions """,
    "version": "17.0.1.2.7",
    "license": "LGPL-3",
    "author": "Arados Software ",
    "website": "https://arados-so.com",
    "depends": ["base", 'stock','sale_management' , 'purchase' , 'product'],
    "data": [
        'security/ir.model.access.csv',
        # 'static/src/js/forcasting_button.js',
        # 'static/src/xml/month_calculation_popup.xml',
        'data/create_por.xml',
        'view/product_template.xml',
        'view/mrd_forcast.xml',
        'view/wizard.xml',



    ],
    "assets":{
        'web.assets_backend' :{
            'arados_mrd_forcasting/static/src/xml/month_calculation_popup.xml',
            'arados_mrd_forcasting/static/src/js/forcasting_button.js',

        }
    },
    'installable': True,
    'application': False,
    'auto_install': False,



}
