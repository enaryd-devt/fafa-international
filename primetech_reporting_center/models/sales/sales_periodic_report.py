from collections import defaultdict

from odoo import api, models


class SalesPeriodicReport(models.AbstractModel):
    _name = "primetech.sales.periodic.report"
    _description = "Rapport Périodique des Ventes"

    @api.model
    def get_report_data(
        self,
        date_from,
        date_to,
        company_id=False,
        user_id=False,
        partner_id=False,
        state_filter="all",
    ):

        # =====================================================
        # DOMAINE
        # =====================================================

        domain = [
            ("date", ">=", date_from),
            ("date", "<=", date_to),
        ]

        if company_id:
            domain.append(("company_id", "=", company_id))

        if user_id:
            domain.append(("user_id", "=", user_id))

        if partner_id:
            domain.append(("partner_id", "=", partner_id))

        if state_filter != "all":
            domain.append(("state", "=", state_filter))

        # =====================================================
        # VENTES
        # =====================================================

        sales = self.env["sale.report"].search(
            domain,
            order="date, id",
        )

        # =====================================================
        # VARIABLES
        # =====================================================

        sales_lines = []

        total_ht = 0.0
        total_ttc = 0.0
        total_qty = 0.0

        seller_summary = defaultdict(
            lambda: {
                "qty": 0.0,
                "ht": 0.0,
                "ttc": 0.0,
            }
        )

        customer_summary = defaultdict(
            lambda: {
                "ht": 0.0,
                "ttc": 0.0,
            }
        )

        product_summary = defaultdict(
            lambda: {
                "qty": 0.0,
                "ht": 0.0,
            }
        )

        warehouse_summary = defaultdict(
            lambda: {
                "qty": 0.0,
                "ht": 0.0,
            }
        )

        # =====================================================
        # PARCOURS DES VENTES
        # =====================================================

        for sale in sales:

            seller = (
                sale.user_id.name
                if sale.user_id
                else "-"
            )

            customer = (
                sale.partner_id.display_name
                if sale.partner_id
                else "-"
            )

            warehouse = (
                sale.warehouse_id.display_name
                if sale.warehouse_id
                else "-"
            )

            product = (
                sale.product_id.display_name
                if sale.product_id
                else "-"
            )

            qty = sale.product_uom_qty or 0.0

            ht = sale.price_subtotal or 0.0

            ttc = sale.price_total or 0.0

            delivered = sale.qty_delivered or 0.0

            invoiced = sale.qty_invoiced or 0.0

            # ==========================================
            # TYPE DE VENTE
            # ==========================================

            sale_type = "Commande"

            document = ""

            if sale.order_reference:

                document = sale.order_reference.name

                if sale.order_reference._name == "pos.order":
                    sale_type = "Point de Vente"

            # ==========================================
            # TOTAUX
            # ==========================================

            total_qty += qty
            total_ht += ht
            total_ttc += ttc

            # ==========================================
            # DETAIL
            # ==========================================

            sales_lines.append({

                "document": document,

                "sale_type": sale_type,

                "date": sale.date,

                "warehouse": warehouse,

                "customer": customer,

                "seller": seller,

                "product": product,

                "qty": qty,

                "qty_delivered": delivered,

                "qty_invoiced": invoiced,

                "unit_price": sale.price_unit,

                "discount": sale.discount,

                "discount_amount": sale.discount_amount,

                "ht": ht,

                "ttc": ttc,

                "state": sale.state,

                "invoice_status": sale.invoice_status,

            })

            # ==========================================
            # COMMERCIAUX
            # ==========================================

            seller_summary[seller]["qty"] += qty
            seller_summary[seller]["ht"] += ht
            seller_summary[seller]["ttc"] += ttc

            # ==========================================
            # CLIENTS
            # ==========================================

            customer_summary[customer]["ht"] += ht
            customer_summary[customer]["ttc"] += ttc

            # ==========================================
            # PRODUITS
            # ==========================================

            product_summary[product]["qty"] += qty
            product_summary[product]["ht"] += ht

            # ==========================================
            # MAGASINS
            # ==========================================

            warehouse_summary[warehouse]["qty"] += qty
            warehouse_summary[warehouse]["ht"] += ht
                    # =====================================================
        # RESUME GENERAL
        # =====================================================

        summary = {

            "sale_count":
                len(sales),

            "customer_count":
                len(set(customer_summary.keys())),

            "seller_count":
                len(set(seller_summary.keys())),

            "warehouse_count":
                len(set(warehouse_summary.keys())),

            "turnover_ht":
                total_ht,

            "turnover_ttc":
                total_ttc,

            "qty_sold":
                total_qty,

            "average_ticket":
                (
                    total_ht / len(sales)
                    if sales
                    else 0.0
                ),

        }

        # =====================================================
        # TOP CLIENTS
        # =====================================================

        top_customers = sorted(

            [

                {
                    "customer": customer,
                    **values,
                }

                for customer, values
                in customer_summary.items()

            ],

            key=lambda x: x["ht"],

            reverse=True,

        )[:10]

        # =====================================================
        # TOP PRODUITS
        # =====================================================

        top_products = sorted(

            [

                {
                    "product": product,
                    **values,
                }

                for product, values
                in product_summary.items()

            ],

            key=lambda x: x["ht"],

            reverse=True,

        )[:10]

        # =====================================================
        # TOP COMMERCIAUX
        # =====================================================

        top_salespersons = sorted(

            [

                {
                    "seller": seller,
                    **values,
                }

                for seller, values
                in seller_summary.items()

            ],

            key=lambda x: x["ht"],

            reverse=True,

        )[:10]

        # =====================================================
        # TOP MAGASINS
        # =====================================================

        top_warehouses = sorted(

            [

                {
                    "warehouse": warehouse,
                    **values,
                }

                for warehouse, values
                in warehouse_summary.items()

            ],

            key=lambda x: x["ht"],

            reverse=True,

        )

        # =====================================================
        # DETAIL TRIE
        # =====================================================

        sales_lines = sorted(

            sales_lines,

            key=lambda x: (
                x["date"],
                x["document"],
            ),

        )

        # =====================================================
        # RETURN
        # =====================================================

        return {

            "summary":
                summary,

            "sales_lines":
                sales_lines,

            "seller_summary":

                sorted(

                    [

                        {

                            "seller": seller,

                            **values,

                        }

                        for seller, values
                        in seller_summary.items()

                    ],

                    key=lambda x: x["ht"],

                    reverse=True,

                ),

            "customer_summary":

                sorted(

                    [

                        {

                            "customer": customer,

                            **values,

                        }

                        for customer, values
                        in customer_summary.items()

                    ],

                    key=lambda x: x["ht"],

                    reverse=True,

                ),

            "product_summary":

                sorted(

                    [

                        {

                            "product": product,

                            **values,

                        }

                        for product, values
                        in product_summary.items()

                    ],

                    key=lambda x: x["ht"],

                    reverse=True,

                ),

            "warehouse_summary":

                top_warehouses,

            "top_customers":

                top_customers,

            "top_products":

                top_products,

            "top_salespersons":

                top_salespersons,

            "top_warehouses":

                top_warehouses,

        }