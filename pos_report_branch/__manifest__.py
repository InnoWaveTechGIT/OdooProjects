{
    'name': 'POS report branch',
    'summary': 'Human readable name Module Project',
    'version': '1.0',

    'description': """
Human readable name Module Project.
==============================================


    """,

    'author': 'TM_FULLNAME',
    'maintainer': 'TM_FULLNAME',
    'contributors': ['TM_FULLNAME <TM_FULLNAME@gmail.com>'],

    'website': 'http://www.gitlab.com/TM_FULLNAME',

    'license': 'AGPL-3',
    'category': 'Uncategorized',

    'depends': [
        'stock','point_of_sale','purchase',
    ],
    'external_dependencies': {
        'python': [
        ],
    },
    'data': [
        'security/ir.model.access.csv',
        'security/base_security.xml',
        'views/purchase_order.xml',
        'views/pos.xml',
        'views/res_users.xml',
    ],
    'demo': [
    ],
    'js': [
    ],
    'css': [
    ],
    'qweb': [
    ],
    'images': [
    ],
    'test': [
    ],

    'installable': True
}
