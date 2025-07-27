{
    'name': 'VPS Management',
    'version': '1.0',
    'category': 'Tools',
    'summary': 'Module for managing VPS server information',
    'description': """
        This module allows users to store and manage information about VPS servers, including IP, passwords, domain, and dates.
    """,
    'author': 'Ali Ammar',
    'depends': ['base' , 'mail'],
    'data': [
        'security/sec_group.xml',
        'security/ir.model.access.csv',
        'views/vps_views.xml',
    ],
    'installable': True,
    'application': True,
}
