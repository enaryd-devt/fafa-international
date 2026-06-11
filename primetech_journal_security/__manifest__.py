{
    "name": "PrimeTech Journal Security",
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "summary": "Restriction de visibilité des journaux comptables",
    "author": "PrimeTech",
    "license": "LGPL-3",

    "depends": [
        "account",
    ],

    "data": [
        "security/journal_rule.xml",
        "security/security.xml",
        "views/account_journal_views.xml",
    ],

    "installable": True,
    "application": False,
}