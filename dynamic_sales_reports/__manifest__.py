{
    'name': 'Dynamic Reports',
    'version': '1.0',
    'summary': 'Dynamic Reports Module',
    'depends': ['base', 'web','dynamic_reports', 'point_of_sale', 'product', 'hr'],
    'data': [
        'views/create_dynamic_wizard.xml',

    ],
    'installable': True,
    'auto_install': False,
}
