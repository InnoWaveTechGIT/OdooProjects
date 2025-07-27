{
    "name": "MS customize",
    "summary": """ """,
    "version": "17.0.0.1",
    "license": "LGPL-3",
    "author": "Ali Ammar",
    "website": "",
    "depends": ["base", 'mail' , "sale" ,"account", 'contacts' , 'stock'],
    "data": [        
        'security/ir.model.access.csv',
        'view/expense_report_pivot.xml',
        'view/stock_picking.xml',



        # 'view/product.template.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
