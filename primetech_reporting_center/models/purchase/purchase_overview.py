# -*- coding: utf-8 -*-

from collections import defaultdict
from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import api, models


class PrimetechPurchaseOverview(models.AbstractModel):
    _name = "primetech.purchase.overview"
    _description = "Primetech Purchase Overview Dashboard"

    @api.model
    def get_dashboard_data(self):
        """
        Dashboard principal Achats
        """

        PurchaseOrder = self.env["purchase.order"]
        AccountMove = self.env["account.move"]
        StockPicking = self.env["stock.picking"]

        purchase_orders = PurchaseOrder.search([
            ("state", "in", ["purchase", "done"])
        ])

        purchase_count = len(purchase_orders)

        supplier_count = len(
            purchase_orders.mapped("partner_id")
        )

        total_ht = sum(
            purchase_orders.mapped("amount_untaxed")
        )

        total_ttc = sum(
            purchase_orders.mapped("amount_total")
        )

        average_order = (
            total_ttc / purchase_count
            if purchase_count
            else 0.0
        )

        pending_receipts = StockPicking.search_count([
            ("picking_type_code", "=", "incoming"),
            ("state", "not in", ["done", "cancel"]),
        ])

        vendor_bills_to_validate = AccountMove.search_count([
            ("move_type", "=", "in_invoice"),
            ("state", "=", "draft"),
        ])

        today = date.today()

        current_month_amount = 0.0
        previous_month_amount = 0.0

        monthly_evolution = []

        for i in range(11, -1, -1):

            month_date = today - relativedelta(months=i)

            month_orders = purchase_orders.filtered(
                lambda po:
                po.date_order
                and po.date_order.month == month_date.month
                and po.date_order.year == month_date.year
            )

            amount = sum(
                month_orders.mapped("amount_total")
            )

            monthly_evolution.append({
                "month": month_date.strftime("%b"),
                "amount": round(amount, 2),
            })

            if (
                month_date.month == today.month
                and month_date.year == today.year
            ):
                current_month_amount = amount

        previous_month = today - relativedelta(months=1)

        previous_orders = purchase_orders.filtered(
            lambda po:
            po.date_order
            and po.date_order.month == previous_month.month
            and po.date_order.year == previous_month.year
        )

        previous_month_amount = sum(
            previous_orders.mapped("amount_total")
        )

        if previous_month_amount:
            growth_percentage = (
                (
                    current_month_amount
                    - previous_month_amount
                )
                / previous_month_amount
            ) * 100
        else:
            growth_percentage = 100.0

        #
        # TOP FOURNISSEURS
        #

        supplier_data = []

        for supplier in purchase_orders.mapped("partner_id"):

            supplier_orders = purchase_orders.filtered(
                lambda po:
                po.partner_id.id == supplier.id
            )

            supplier_data.append({
                "name": supplier.name,
                "count": len(supplier_orders),
                "amount": round(
                    sum(
                        supplier_orders.mapped(
                            "amount_total"
                        )
                    ),
                    2,
                ),
            })

        top_suppliers = sorted(
            supplier_data,
            key=lambda x: x["amount"],
            reverse=True,
        )[:10]

        #
        # TOP PRODUITS
        #

        products = defaultdict(
            lambda: {
                "name": "",
                "qty": 0.0,
                "amount": 0.0,
            }
        )

        for po in purchase_orders:
            for line in po.order_line:

                product = line.product_id

                products[product.id]["name"] = (
                    product.display_name
                )

                products[product.id]["qty"] += (
                    line.product_qty
                )

                products[product.id]["amount"] += (
                    line.price_subtotal
                )

        top_products = sorted(
            products.values(),
            key=lambda x: x["amount"],
            reverse=True,
        )[:10]

        #
        # DEPENSES PAR CATEGORIE
        #

        categories = defaultdict(float)

        for po in purchase_orders:
            for line in po.order_line:

                category = (
                    line.product_id.categ_id.display_name
                    or "Sans catégorie"
                )

                categories[category] += (
                    line.price_subtotal
                )

        expense_by_category = [
            {
                "category": category,
                "amount": round(amount, 2),
            }
            for category, amount
            in categories.items()
        ]

        #
        # ACHATS EN RETARD
        #

        late_purchase_orders = []

        for po in PurchaseOrder.search([
            ("state", "=", "purchase")
        ]):

            late = False

            for line in po.order_line:

                if (
                    line.date_planned
                    and line.date_planned.date() < today
                ):
                    late = True
                    break

            if late:

                late_purchase_orders.append({
                    "name": po.name,
                    "supplier": po.partner_id.name,
                    "amount": po.amount_total,
                })

        late_purchase_orders = (
            late_purchase_orders[:10]
        )

        #
        # RECEPTIONS INCOMPLETES
        #

        incomplete_receipts = []

        receipts = StockPicking.search([
            ("picking_type_code", "=", "incoming"),
            ("state", "=", "assigned"),
        ], limit=10)

        for receipt in receipts:

            incomplete_receipts.append({
                "name": receipt.name,
                "partner": (
                    receipt.partner_id.name
                    if receipt.partner_id
                    else ""
                ),
            })

        #
        # FACTURES BLOQUEES
        #

        blocked_vendor_bills = []

        bills = AccountMove.search([
            ("move_type", "=", "in_invoice"),
            ("state", "=", "draft"),
        ], limit=10)

        for bill in bills:

            blocked_vendor_bills.append({
                "name": bill.name,
                "vendor": bill.partner_id.name,
                "amount": bill.amount_total,
            })

        #
        # DERNIERES COMMANDES
        #

        recent_purchase_orders = []

        recent_orders = PurchaseOrder.search(
            [],
            order="date_order desc",
            limit=10,
        )

        for po in recent_orders:

            recent_purchase_orders.append({
                "name": po.name,
                "supplier": po.partner_id.name,
                "date": (
                    po.date_order.strftime("%d/%m/%Y")
                    if po.date_order
                    else ""
                ),
                "amount": po.amount_total,
                "state": po.state,
            })

        return {
            "purchase_count": purchase_count,
            "supplier_count": supplier_count,
            "total_ht": round(total_ht, 2),
            "total_ttc": round(total_ttc, 2),
            "average_order": round(
                average_order,
                2,
            ),
            "pending_receipts": pending_receipts,
            "vendor_bills_to_validate":
                vendor_bills_to_validate,
            "growth_percentage": round(
                growth_percentage,
                2,
            ),
            "monthly_evolution":
                monthly_evolution,
            "top_suppliers":
                top_suppliers,
            "top_products":
                top_products,
            "expense_by_category":
                expense_by_category,
            "late_purchase_orders":
                late_purchase_orders,
            "incomplete_receipts":
                incomplete_receipts,
            "blocked_vendor_bills":
                blocked_vendor_bills,
            "recent_purchase_orders":
                recent_purchase_orders,
        }