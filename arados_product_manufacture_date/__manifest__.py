# -*- coding: utf-8 -*-
{
    'name': "Product Manufacture Date",

    'description': """
       Track production dates on product
    """,

    'author': "Arados Software",
    'website': "https://www.arados-so.com",
    'license': 'LGPL-3',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '18.0.0.0.2',

    # any module necessary for this one to work correctly
    'depends': ['stock', 'product_expiry'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/product_template_views.xml',
        'views/stock_move_views.xml',
        'views/stock_lot_views.xml',
        'views/stock_quant_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

