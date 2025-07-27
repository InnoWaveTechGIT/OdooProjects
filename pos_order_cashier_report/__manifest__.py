# Copyright 2018 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Pos Daily Sales Report",
    "summary": """ """,
    "version": "0.1",
    "license": "LGPL-3",
    "author": "",
    "website": "",
    "depends": ["base", 'website', 'crm', 'point_of_sale', "account_accountant"],
    "data": [
        'report/payment_report.xml',
        'view/report_saledetails.xml',

    ],
    'assets': {
        'point_of_sale.assets_prod': [
            'pos_order_cashier_report/static/src/overrides/**/*',
            'pos_order_cashier_report/static/src/app/**/*',
        ],
        'point_of_sale._assets_pos': [
            'pos_order_cashier_report/static/src/**/*',
            'pos_order_cashier_report/static/app/**/*',
            'pos_order_cashier_report/static/src/js/*',
            'pos_order_cashier_report/static/src/xml/invoice_popup.xml',
            'pos_order_cashier_report/static/src/xml/receipt.xml',
        ],
    },

}
