from odoo import models, api


class PosSession(models.Model):
    _inherit = "pos.session"

    # =========================================================
    # ENRICH POS PRODUCT DATA
    # =========================================================
    @api.model
    def _get_pos_ui_product_product(self, params):

        products = super()._get_pos_ui_product_product(params)

        if not products:
            return products

        # =====================================================
        # FETCH REAL PRODUCT DATA (IMPORTANT FIX)
        # =====================================================
        product_ids = [p["id"] for p in products]

        product_map = {
            p.id: p for p in self.env["product.product"].browse(product_ids).read([
                "qty_available",
                "virtual_available",
                "standard_price",
                "lst_price",
                "tracking",
            ])
        }

        StockLot = self.env["stock.lot"]
        StockQuant = self.env["stock.quant"]
        Warehouse = self.env["stock.warehouse"]

        warehouses = Warehouse.search([])

        # =====================================================
        # LOOP PRODUCTS
        # =====================================================
        for product in products:

            product_id = product["id"]
            data = product_map.get(product_id, {})

            # -------------------------
            # BASIC FIELDS FIX
            # -------------------------
            product["qty_available"] = data.get("qty_available") or 0
            product["virtual_available"] = data.get("virtual_available") or 0
            product["standard_price"] = data.get("standard_price") or 0
            product["lst_price"] = data.get("lst_price") or 0
            product["tracking"] = data.get("tracking") or False

       