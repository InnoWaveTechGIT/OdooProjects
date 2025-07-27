{
    'name': "print_labels_invoice",
    'version': '0.1',
    'depends': ['base', 'account'],
    'data': [
        'views/views.xml',
        'views/templates.xml',
        'views/report_inv_label.xml',  # Ensure this is correctly listed
        'views/sale_order_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
