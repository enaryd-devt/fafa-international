{
    "name": "PrimeTech Stock Replenishment",

    "version": "18.0.1.0.0",

    "category": "Inventory",

    "summary": """
        Gestion avancée des Bons de Réapprovisionnement
    """,

    "description": """
PrimeTech Stock Replenishment

Fonctionnalités :

- Détection automatique des produits en alerte
- Génération des bons de réapprovisionnement
- Regroupement par catégorie
- Modification des quantités à commander
- Validation du bon
- Génération automatique des demandes de prix
- Impression PDF professionnelle
- Historique des réapprovisionnements
- Workflow d'approbation
    """,

    "author": "PrimeTech Services",

    "website": "https://www.primetech.cm",

    "license": "LGPL-3",

    "depends": [
        "stock",
        "purchase",
        "mail",
    ],

    "data": [

        # SECURITY

        "security/stock_replenishment_security.xml",
        "security/ir.model.access.csv",

        # DATA

        "data/sequence.xml",

        # WIZARD

        "views/generate_replenishment_wizard_views.xml",

        # REPORTS

        "report/stock_replenishment_report.xml",
        "report/stock_replenishment_templates.xml",

        # VIEWS

        "views/stock_replenishment_action.xml",
        "views/stock_replenishment_views.xml",
        "views/stock_replenishment_menu.xml",

    ],

    "installable": True,

    "application": True,

    "auto_install": False,
}