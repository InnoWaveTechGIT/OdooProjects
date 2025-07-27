{
    "name": "Syrian E-invoice Integration",
    "version": "17.0.1.0.3",
    "description": """This Module integrates with the electronic invoice Portal yo automatically send your invoices to the Syrian Tax Authority  """,
    "license": "LGPL-3",
    "author": "Arados Software ",
    "website": "https://arados-so.com",
    "depends": ["base", 'account' ,'account_edi' ],
    "data": [
        # 'security/ir.model.access.csv',
        'data/schedule_action.xml',
        'data/demo_data.xml',
        'reports/e_invoice_report.xml',
        'view/setting.xml',
        'view/journals.xml',
        'view/account_move.xml',
        'view/product_category.xml',
        # 'view/product_template.xml',

    ],
    'installable': True,
    'application': False,
    'auto_install': False,



}
