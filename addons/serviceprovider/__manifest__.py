# -*- coding: utf-8 -*-
{
    'name': 'Service Provider',
    'version': '17.0.1.0.0',
    'summary': 'Record Model Information',
    'category': 'Tools',
    'author': 'odoo',
    'maintainer': 'odoo developer',
    'company': 'odoo Model',
    'website': ' ',
    'depends': [
        'base',
        'base_import',
        'mail',
        'hr',
        'asset'
    ],
    'data': [
        'views/serviceprovider.xml',
        'views/servicetype.xml',
        'views/serviceagreement.xml',
        'views/agreementtype.xml',
        'views/equimenttype.xml',
        'views/equimentcat.xml',
        'security/ir.model.access.csv'
    ],
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
