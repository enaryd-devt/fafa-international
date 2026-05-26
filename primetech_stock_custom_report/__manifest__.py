{
    "name": "PrimeTech Stock Custom Report",
    "version": "18.0.1.0.0",
    "summary": "Professional PDF report for stock ",
    "category": "Warehouse",
    "author": "PrimeTech Services",
    "license": "LGPL-3",

    "depends": [
        "stock",
    ],
    "assets": {
        "web.report_assets_common": [
            "primetech_stock_custom_report/static/src/css/report_stock.css",
        ],
    },

    "data": [
        "security/ir.model.access.csv",
        "report/report_template.xml",
        "report/report_action.xml",
        "wizard/product_stock_move_wizard_view.xml",
        "views/menu_analysis.xml",
    

    ],

    "installable": True,
    "application": False,
}