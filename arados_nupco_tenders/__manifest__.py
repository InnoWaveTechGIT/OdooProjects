{
    "name": "NUPCO Tenders",
    "version": "18.0.6.0.14",
    "license": "LGPL-3",
    "author": "Arados Software ",
    "website": "https://arados-so.com",
    "depends": ["base", 'stock', 'sale_management', 'product','account','documents','mrp','purchase', 'arados_product_custom_details','product_expiry'],
    "data": [
        'security/ir.model.access.csv',
        'data/demo_data.xml',
        'view/tender_view.xml',
        'view/tender_order_view.xml',
        'view/new_quote.xml',
        'view/stock_lot.xml',
        'view/stock_move_line.xml',
        'view/account_move.xml',
        'view/purchase.xml',
        'view/stock_picking.xml',
        'view/quted_values.xml',
        'view/tender_planner.xml',
        'view/tender_last_winning.xml',
        'view/tender_planner_comp.xml',

        'view/delivery_plan.xml',
        'view/delivery_plan_detail.xml',
        'view/tender_bme.xml',
        'view/tender_stock.xml',
        'wizard/win_tender.xml',
        'wizard/import_excel.xml',
        'wizard/new_quote.xml',
        'wizard/supplier.xml',
        'wizard/add_sale_order.xml',
        'wizard/order_import_excel.xml',

    ],
    "assets":{
        'web.assets_backend' :{
            'arados_nupco_tenders/static/src/xml/month_calculation_popup.xml',
            'arados_nupco_tenders/static/src/js/forcasting_button.js',

        }
    },
    'installable': True,
    'application': True,
    'auto_install': False,



}
