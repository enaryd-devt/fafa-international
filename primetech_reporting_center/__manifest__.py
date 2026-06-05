{
    "name": "PrimeTech Reporting Center",
    "version": "18.0.1.0.0",
    "category": "Reporting",
    "summary": "Centre de reporting et d'impression",
    "description": """
                    PrimeTech Reporting Center

                    Centre centralisé de reporting :
                    - Comptabilité
                    - Vente
                    - Achat
                    - Stock
                    - RH
                    - Impression
    """,
    "author": "PrimeTech",
    "website": "https://primetech.cm",
    "license": "LGPL-3",
    "application": True,
    "installable": True,

   "depends": [
        "base",
        "web",
        "account",
        "purchase",
        "stock",
        "hr",
    ],

    "data": [
        "views/dashboard/dashboard_action.xml",
        "views/dashboard/placeholder_action.xml",

        "views/menu/reporting_menu.xml",
        "views/menu/dashboard_menu.xml",
        "views/menu/accounting_menu.xml",
        "views/menu/sales_menu.xml",
        "views/menu/purchase_menu.xml",
        "views/menu/stock_menu.xml",
        "views/menu/hr_menu.xml",
        "views/menu/printing_menu.xml",
        "views/menu/configuration_menu.xml",
    ],

    "assets": {
        'web.assets_backend': [

            'primetech_reporting_center/static/lib/chartjs/chart.umd.js',

            'primetech_reporting_center/static/src/js/**/*.js',

            'primetech_reporting_center/static/src/xml/**/*.xml',

            'primetech_reporting_center/static/src/scss/*.scss',

        ]
    },
}