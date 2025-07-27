
{
    "name": "E-commerce Nasaem",
    "summary": """ """,
    "author": "Ali Ammar",
    "website": "",
    "depends": ['base','sale', 'website_sale'],
    'assets': {
        'web.assets_frontend': [
            'https://unpkg.com/swiper/swiper-bundle.min.js',
        ]
    },
    "data": [
        'security/ir.model.access.csv',
        'views/user_token.xml',
        'views/banner.xml',
        'views/payment_template.xml',
        'views/promotion.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}
