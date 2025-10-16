{
    'name': 'Tender Managements',
    'version': '17.0.1.0.0',
    'category': 'Management',
    'summary': 'Tender Management with Document Evaluation',
    'description': '''
        Tender Management System
        ========================
        * Create and manage tenders
        * Upload documents
        * Evaluate documents via FastAPI
        * View evaluation results in table format
    ''',
    'depends': ['base', 'web', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/tender_views.xml',
        # 'views/tender_evaluation_views.xml',
        'views/menu_views.xml',
    ],
    'assets':{
        'web.assets_backend': [
            'tender_management/static/src/css/loading.css',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}