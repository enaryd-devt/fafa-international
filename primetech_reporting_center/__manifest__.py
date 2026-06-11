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
        "report_xlsx",
    ],

    "data": [

        "security/ir.model.access.csv",


        "views/dashboard/dashboard_action.xml",
        "views/dashboard/placeholder_action.xml",
        
        # =====================================================
        # ACCOUNTING
        # =====================================================

        # DASHBOARD
        "views/accounting/accounting_dashboard_action.xml",

        # WIZARDS
        "views/accounting/general_ledger_wizard_views.xml",
        "views/accounting/general_ledger_actions.xml",

        "views/accounting/trial_balance_wizard_views.xml",
        "views/accounting/trial_balance_action.xml",

        "views/accounting/accounting_journal_wizard_views.xml",
        "views/accounting/accounting_journal_actions.xml",

        "views/accounting/partner_balance_wizard_views.xml",
        "views/accounting/partner_balance_actions.xml",

        "views/accounting/balance_sheet_wizard_views.xml",
        "views/accounting/balance_sheet_actions.xml",

        "views/accounting/income_statement_wizard_views.xml",
        "views/accounting/income_statement_actions.xml",

        # PREVIEWS
        "views/accounting/report_preview_wizard_views.xml",

        # PDF
        "report/pdf/accounting/general_ledger_report_action.xml",
        "report/pdf/accounting/general_ledger_report.xml",

        "report/pdf/accounting/trial_balance_templates.xml",
        "report/pdf/accounting/trial_balance_report.xml",

        "report/pdf/accounting/accounting_journal_templates.xml",
        "report/pdf/accounting/accounting_journal_report.xml",

        "report/pdf/accounting/partner_balance_templates.xml",
        "report/pdf/accounting/partner_balance_report.xml",

        "report/pdf/accounting/balance_sheet_templates.xml",
        "report/pdf/accounting/balance_sheet_report.xml",

        "report/pdf/accounting/income_statement_templates.xml",
        "report/pdf/accounting/income_statement_report.xml",

        # XLSX
        "report/xlsx/accounting/general_ledger_xlsx.xml",
        "report/xlsx/accounting/trial_balance_xlsx.xml",
        "report/xlsx/accounting/accounting_journal_xlsx.xml",
        "report/xlsx/accounting/partner_balance_xlsx.xml",
        "report/xlsx/accounting/balance_sheet_xlsx.xml",
        "report/xlsx/accounting/income_statement_xlsx_report.xml",
        
        
        # =====================================================
        # SALES
        # =====================================================

        # DASHBOARD
        "views/sales/sales_overview_views.xml",

        # WIZARD
        "views/sales/sales_periodic_report_wizard_views.xml",
        "views/sales/sales_periodic_report_action.xml",
        "views/sales/report_sales_preview_wizard_views.xml",

        # PDF
        "report/pdf/sales/sales_periodic_templates.xml",
        "report/pdf/sales/sales_periodic_report.xml",

        # XLSX
        "report/xlsx/sales/sales_periodic_xlsx.xml",

                       

        # =====================================================
        # MENU
        # =====================================================

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

            "primetech_reporting_center/static/src/scss/*.scss",

        ]
    },
}