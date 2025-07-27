{
    "name": "NUPCO VAT Invoice",
    "version": "18.0.0.0.1",
    "license": "LGPL-3",
    "author": "Arados Software ",
    "website": "https://arados-so.com",
    "depends": ["base", 'arados_nupco_tenders','l10n_sa_edi'],
    "data": [
        'view/account_move.xml',
        'report/vat_invoice.xml',
    ],

    'installable': True,
    'application': False,
    'auto_install': False,

}
