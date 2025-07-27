{
    "name": "Invoice discount",
    "summary": """ """,
    "version": "0.1",
    "license": "LGPL-3",
    "author": "Ali Ammar",
    "website": "",
    "depends": ["base", "account" , "sale"],
    "data": [        
        'security/ir.model.access.csv',
        'view/discount_invoice.xml',
        'view/expense_report_pivot.xml',


        # 'view/product.template.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
