{
    'name': 'Website Pricelist ',
    'summary': '',
    'description': "Allow user to Show products by price list",
    'author': 'Ali Ammar',
    'website': 'aliammarfin@gmail.com',

    'category': 'sale',
    'version': '0.1',

    # any module for this one to work correctly
    'depends': ['base', 'web','website'],

    'assets': {'web.assets_frontend': [
            # 'website_priclist/static/src/xml/dialogue.xml',
            'website_priclist/static/src/js/products.js',
        ],},

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/products_pricelist.xml',
        'views/assets.xml',
        # 'views/expense_report_pivot.xml',
        
    ],

    # loaded in demo mode only
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [],
    # 'post_init_hook': 'remove_contact_us_menu',
}
