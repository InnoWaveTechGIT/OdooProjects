{
    'name': 'Haven Hub',
    'version': '1.0',
    'summary': '',
    'description': """
        Adds a button to purchase orders to create delivery transfers
        with selected products and quantities.
    """,
    'author': 'InnoWaveTech',
    'website': 'https://inno-wave-tech.com',
    'category': '',
    'depends': ['base' , ],
    'data': [
        'security/ir.model.access.csv',
        'views/about_us.xml',
        # 'views/delivery_transfer_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
