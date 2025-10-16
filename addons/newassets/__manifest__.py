# -*- coding: utf-8 -*-
{
    'name': 'New Asset',
    'version': '17.0.1.0.0',
    'summary': 'Record Model Information',
    'category': 'Tools',
    'author': 'odoo',
    'maintainer': 'odoo developer',
    'company': 'odoo Model',
    'website': '',
    'depends': ['base', 'base_import', 'deltatech_property', 'contacts', 'project'],
    'data': [
        'views/newassets.xml',
        'views/equipmentcategory.xml',
        'views/equipcattype.xml',
        'reports/asset_qr_code.xml',
        'views/equipmentclassification.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
    ],
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}

