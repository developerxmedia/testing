{
    "name": "Pop up",
    "version": "17.0.3.9.0",
    "category": "Reporting",
    "summary": "Task Reports",
    "author": ""
    "initOS GmbH,"
    "redCOR AG,"
    "ForgeFlow,"
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-financial-reporting",
    "depends": ["base", "hr_attendance" ],
    "data": [
        'security/ir.model.access.csv',
        'security/access.xml',
        'data/ir_cron_datas.xml',
        'view/over_time.xml',
        'view/task_report.xml',
        # 'wizard/pop_up.xml',
    ],
    "qweb": [],
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "AGPL-3",
}