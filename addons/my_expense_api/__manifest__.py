{
    'name': 'Expense API',
    'version': '1.0',
    'summary': 'API to create HR Expenses via POST',
    'description': 'Provides an endpoint to create expense records using external POST requests.',
    'author': 'Your Name',
    'depends': ['base', 'hr_expense'],
    'data': [
        'views/hr_expense_views.xml',
        'views/hr_employee_inherit_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}