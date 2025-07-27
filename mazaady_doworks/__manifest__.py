{
    'name': "Mazaady DoWorks",

    'summary': "mazaady doworks integration purpose",

    'description': """ mazaady doworks integration purpose """,

    'author': "Mazaady",
    'website': "https://www.Mazaady.com",

    'category': 'Accounting',
    'version': '0.1',

    'depends': ['base','loyalty', 'sale_subscription', 'custom_sales', 'account'],

    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'data/sale_subscription_data.xml',
        # 'views/templates.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}

