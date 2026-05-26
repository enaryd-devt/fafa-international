{
    'name': 'PrimeTech Reports custom',
    'version': '18.0.1.0.0',
    'summary': 'Custom layout report for Odoo 18',
    'author': 'PrimeTech',
    'depends': ['account', 'stock'],
    'data': [
        "views/custom_report_invoice.xml",
        "views/inventory_count_report.xml",
        "views/custom_receipt_payment.xml",
        "views/custom_saleorder.xml",
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}