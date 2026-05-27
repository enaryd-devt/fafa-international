{
    'name': 'PrimeTech Invoice Print Template Selector',
    'version': '1.0',
    'depends': ['account'],
    'author': 'PrimeTech',
    'category': 'Accounting',
    'data': [
        'security/ir.model.access.csv',

        'views/print_wizard_views.xml',
        'views/account_move_views.xml',
       
        'reports/report_actions.xml',
        'reports/main_report.xml',
        'reports/template_1.xml',
        'reports/template_2.xml',
        'reports/template_3.xml',
        'reports/template_4.xml',
    ],
    'installable': True,
    'application': False,
}