{
    'name': 'CheckList  Documents',
    'version': '17.0.1.0.0',
    'category': 'Tools',
    'summary': 'Upload and manage tender documents via API',
    'depends': ['base'],
    'data': [
        'views/document_views.xml',
        'security/ir.model.access.csv',
#         'data/tender_sequence.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
