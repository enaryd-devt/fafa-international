{
    "name": "POS quantity and price Display",
    "version": "18.1.0",
    "category": "Point of Sale",
    "summary": "Affiche le prix et la quantité disponible sur les cartes d'article du PDV",
    "author": "PrimeTech Services",
    "depends": ["point_of_sale", "stock"],
    'assets': {
        'point_of_sale._assets_pos': [
            "primetech_pos_show_qty_and_price/static/src/xml/pos_show_qty.xml",
            "primetech_pos_show_qty_and_price/static/src/xml/pos_bouton_item.xml",
            "primetech_pos_show_qty_and_price/static/src/xml/pos_show_price.xml",
            "primetech_pos_show_qty_and_price/static/src/js/pos_show_qty.js",            
            "primetech_pos_show_qty_and_price/static/src/js/pos_show_price.js",
            "primetech_pos_show_qty_and_price/static/src/css/pos_item.css",
            "primetech_pos_show_qty_and_price/static/src/js/price_list_button.js",
            "primetech_pos_show_qty_and_price/static/src/xml/price_list_button.xml",
            "primetech_pos_show_qty_and_price/static/src/css/price_list_button.css",


        ]
    },
    "installable": True,
    "auto_install": False,
}