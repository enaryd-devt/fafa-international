from collections import defaultdict
from datetime import date

from odoo import api, models


class SalesOverview(models.AbstractModel):

    _name = "primetech.sales.overview"
    _description = "Sales Overview Dashboard"

    @api.model
    def get_dashboard_data(self):

        invoices = self.env[
            "account.move"
        ].search([
            ("move_type", "=", "out_invoice"),
            ("state", "=", "posted"),
        ])

        orders = self.env[
            "sale.order"
        ].search([
            ("state", "in", [
                "sale",
                "done",
            ]),
        ])

        # =====================================
        # KPI PRINCIPAUX
        # =====================================

        turnover_ht = sum(
            invoices.mapped(
                "amount_untaxed"
            )
        )

        turnover_ttc = sum(
            invoices.mapped(
                "amount_total"
            )
        )

        invoice_count = len(
            invoices
        )

        order_count = len(
            orders
        )

        customer_count = len(
            invoices.mapped(
                "partner_id"
            )
        )

        # =====================================
        # CA MOIS COURANT
        # =====================================

        today = date.today()

        current_month_invoices = invoices.filtered(
            lambda m:
                m.invoice_date
                and m.invoice_date.month == today.month
                and m.invoice_date.year == today.year
        )

        turnover_month = sum(
            current_month_invoices.mapped(
                "amount_untaxed"
            )
        )

        # =====================================
        # CA MOIS PRECEDENT
        # =====================================

        if today.month == 1:

            prev_month = 12
            prev_year = today.year - 1

        else:

            prev_month = today.month - 1
            prev_year = today.year

        previous_month_invoices = invoices.filtered(
            lambda m:
                m.invoice_date
                and m.invoice_date.month == prev_month
                and m.invoice_date.year == prev_year
        )

        turnover_previous_month = sum(
            previous_month_invoices.mapped(
                "amount_untaxed"
            )
        )

        # =====================================
        # CROISSANCE
        # =====================================

        growth_rate = 0.0

        if turnover_previous_month:

            growth_rate = (
                (
                    turnover_month
                    - turnover_previous_month
                )
                / turnover_previous_month
            ) * 100

        # =====================================
        # PANIER MOYEN
        # =====================================

        average_ticket = 0.0

        if invoice_count:

            average_ticket = (
                turnover_ht
                / invoice_count
            )

        # =====================================
        # FACTURES IMPAYEES
        # =====================================

        unpaid_invoices = self.env[
            "account.move"
        ].search([

            ("move_type", "=", "out_invoice"),

            ("state", "=", "posted"),

            ("payment_state", "in", [
                "not_paid",
                "partial",
            ]),

        ])

        unpaid_amount = sum(
            unpaid_invoices.mapped(
                "amount_residual"
            )
        )

        # =====================================
        # COMMANDES A FACTURER
        # =====================================

        to_invoice_orders = self.env[
            "sale.order"
        ].search([

            ("invoice_status", "=",
             "to invoice"),

        ])

        to_invoice_amount = sum(
            to_invoice_orders.mapped(
                "amount_total"
            )
        )

        # =====================================
        # TOP CLIENTS
        # =====================================

        customer_totals = defaultdict(
            float
        )

        for invoice in invoices:

            if not invoice.partner_id:
                continue

            customer_totals[
                invoice.partner_id.name
            ] += invoice.amount_untaxed

        top_customers = []

        for name, amount in sorted(

            customer_totals.items(),

            key=lambda x: x[1],

            reverse=True,

        )[:10]:

            top_customers.append({

                "name": name,

                "amount": amount,

            })
        # =====================================
        # TOP PRODUITS
        # =====================================

        product_totals = defaultdict(
            float
        )

        for line in invoices.mapped(
            "invoice_line_ids"
        ):

            if not line.product_id:
                continue

            product_totals[
                line.product_id.display_name
            ] += (
                line.price_subtotal
            )

        top_products = []

        for name, amount in sorted(

            product_totals.items(),

            key=lambda x: x[1],

            reverse=True,

        )[:10]:

            top_products.append({

                "name": name,

                "amount": amount,

            })

        # =====================================
        # TOP COMMERCIAUX
        # =====================================

        salesperson_totals = defaultdict(
            float
        )

        for invoice in invoices:

            salesperson = (
                invoice.invoice_user_id
            )

            if not salesperson:
                continue

            salesperson_totals[
                salesperson.name
            ] += (
                invoice.amount_untaxed
            )

        top_salespersons = []

        for name, amount in sorted(

            salesperson_totals.items(),

            key=lambda x: x[1],

            reverse=True,

        )[:10]:

            top_salespersons.append({

                "name": name,

                "amount": amount,

            })

        # =====================================
        # EVOLUTION MENSUELLE DU CA
        # =====================================

        monthly_sales = defaultdict(
            float
        )

        for invoice in invoices:

            if not invoice.invoice_date:
                continue

            month_key = (
                invoice.invoice_date.strftime(
                    "%Y-%m"
                )
            )

            monthly_sales[
                month_key
            ] += (
                invoice.amount_untaxed
            )

        evolution = []

        for month in sorted(
            monthly_sales.keys()
        ):

            evolution.append({

                "month": month,

                "amount":
                    monthly_sales[
                        month
                    ],

            })

        # =====================================
        # RETOUR DASHBOARD
        # =====================================

        return {

            "turnover_ht":
                turnover_ht,

            "turnover_ttc":
                turnover_ttc,

            "turnover_month":
                turnover_month,

            "turnover_previous_month":
                turnover_previous_month,

            "growth_rate":
                round(
                    growth_rate,
                    2,
                ),

            "average_ticket":
                average_ticket,

            "invoice_count":
                invoice_count,

            "order_count":
                order_count,

            "customer_count":
                customer_count,

            "unpaid_amount":
                unpaid_amount,

            "to_invoice_amount":
                to_invoice_amount,

            "top_customers":
                top_customers,

            "top_products":
                top_products,

            "top_salespersons":
                top_salespersons,

            "monthly_sales":
                evolution,

        }