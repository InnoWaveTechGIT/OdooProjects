{
    'name': "Mazaady Reports",

    'summary': "",

    'description': """ """,

    'author': "Mazaady",
    'website': "https://www.Mazaady.com",

    'category': '',
    'version': '0.1',

    'depends': ['base','loyalty', 'sale_subscription' ,'account', 'mazaady_doworks'],

    'data': [
        'security/ir.model.access.csv',
        'views/loyalty_view.xml',
        'views/contact.xml',
        'views/contracts.xml',
        'views/wallet_reports.xml',
        'views/account_activities.xml',
        'views/sales_statment_report.xml',

        'reports/wallet_report.xml',
        'reports/account_activities.xml',
        'reports/sale_statment.xml',
        'reports/deals_report.xml',
        
        'wizard/export_excel.xml',

    ],
    'demo': [
        'demo/demo.xml',
    ],
}

