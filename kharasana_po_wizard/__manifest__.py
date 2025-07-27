{
    'name': 'Purchase Delivery Transfer',
    'version': '1.0',
    'summary': 'Create delivery transfers from purchase orders',
    'description': """
        Adds a button to purchase orders to create delivery transfers
        with selected products and quantities.
    """,
    'author': 'Ali Ammar',
    'website': 'https://yourwebsite.com',
    'category': 'Inventory/Purchase',
    'depends': ['purchase', 'stock' , 'project'],
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_order_views.xml',
        'views/delivery_transfer_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
