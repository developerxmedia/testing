{
    "name": "Invoices PDF",
    "summary": "Individual Sales PDF",
    "version": "17.0.1.0.0",
    "category": 'Sales',
    'author': "Scopex pvt.ltd,Logeshwari.P",
    "depends": ['base','mail','sale','stock','purchase','account',],
    "data": [
        # 'reports/invoice_pdf.xml',
        'reports/invoice_pdf_copy.xml',

        'reports/report.xml',
        'reports/header.xml',

    ],
    'images': ['static/description/icon.png'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}