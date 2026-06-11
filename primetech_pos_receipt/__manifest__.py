{
    "name": "PrimeTech POS Receipt",
    "version": "18.0.1.0.0",
    "category": "Point of Sale",
    "author": "PrimeTech",
    "depends": ["point_of_sale"],
    "assets": {
        "point_of_sale._assets_pos": [
            "primetech_pos_receipt/static/src/js/receipt_patch.js",
            "primetech_pos_receipt/static/src/xml/receipt_templates.xml",
            "primetech_pos_receipt/static/src/scss/receipt.scss",
        ],
    },
    "installable": True,
}