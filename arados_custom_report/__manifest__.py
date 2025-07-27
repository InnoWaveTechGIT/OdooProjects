{
    'name': 'Custom Report',
    'version': '18.0.1.0.2',
    'category': 'Accounting',
    "license": "LGPL-3",
    "author": "Arados Software ",
    "website": "https://arados-so.com",
    'summary': 'This module will provide a comprehensive summary of accounting entries empowering accountants to make informed and strategic decision.',
    'depends': ['sale', 'accountant'],
    'data': [
        'views/expense_report_pivot.xml'
    ],
    'installable': True,
    'application': False,
}
