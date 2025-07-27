{
    'name': 'Purchase Report',
    'version': '17.0.1.0.2',
    'category': 'Website',
    "license": "LGPL-3",
    'summary': 'Manage Purchase Reports ',
    "author": "Arados Software ",
    "website": "https://arados-so.com",
    'depends': ['base' , 'purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/reports.xml',
        'views/purchase_return_report.xml',

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
