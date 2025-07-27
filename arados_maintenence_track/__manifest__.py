{
    "name": "Product Maintenance Track",
    "version": "17.0.1.3.18",
    "license": "LGPL-3",
    "author": "Arados Software ",
    "website": "https://arados-so.com",
    "depends": ["base", 'stock', 'sale_management', 'product','maintenance' , 'repair','purchase' , 'hr_maintenance','mrp_maintenance' , 'sign','stock_delivery'],
    "data": [
        'security/ir.model.access.csv',
        'view/product_template.xml',
        'view/stock_move_line.xml',
        'view/stock_lot.xml',
        'view/stock_picking.xml',
        'view/maintenance_request.xml',
        'view/repair_order.xml',
        'view/maintenance_stage.xml',
        'report/repair_report.xml',
        'report/purchase_invoice_report.xml',
        # 'data/maintenance_request_scheduler_data.xml'

    ],
    'installable': True,
    'application': False,
    'auto_install': False,



}
