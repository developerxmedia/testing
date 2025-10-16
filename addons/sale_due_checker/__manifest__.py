{
    'name': 'Invoice Due Checker',
    'version': '1.0',
    'summary': 'Check unpaid invoices before due date and notify via API',
    'description': 'A scheduled cron job to check for unpaid customer invoices with upcoming due dates and send their details to an external FastAPI endpoint via POST.',
    'author': 'Your Name',
    'category': 'Accounting',
    'depends': ['account'],
    'external_dependencies': {
        'python': ['requests', 'reportlab'],
    },
    'data': [
        'views/account_move_view.xml',
        'data/cron.xml',
    ],
    'installable': True,
    'application': False,
}