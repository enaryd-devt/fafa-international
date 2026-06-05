from odoo import api, models, fields
from datetime import date, timedelta
from collections import defaultdict
from dateutil.relativedelta import relativedelta




class PrimetechDashboard(models.AbstractModel):
    _name = "primetech.dashboard"
    _description = "PrimeTech Dashboard Service"

    @api.model
    def get_dashboard_kpis(self, filters=None):

        filters = filters or {}

        today = date.today()

        current_month_start = today.replace(day=1)

        previous_month_start = (
            current_month_start
            - relativedelta(months=1)
        )
        sales = sum(

            self.env[
                "account.move"
            ].search([

                ("move_type", "=",
                "out_invoice"),

                ("state", "=",
                "posted"),

            ]).mapped(
                "amount_untaxed"
            )

        )

        purchases = sum(

            self.env[
                "purchase.order"
            ].search([

                ("state", "in", [
                    "purchase",
                    "done",
                ])

            ]).mapped(
                "amount_untaxed"
            )

        )

        gross_margin = (
            sales - purchases
        )
        cash_balance = sum(

            self.env[
                "account.account"
            ].search([

                ("account_type",
                "=",
                "asset_cash")

            ]).mapped(
                "current_balance"
            )

        )

        # ==========================
        # CHIFFRE D'AFFAIRES
        # ==========================

        current_revenue = sum(

            self.env["account.move"].search([

                ("move_type", "=", "out_invoice"),
                ("state", "=", "posted"),
                ("invoice_date", ">=", current_month_start),

            ]).mapped("amount_total")

        )

        previous_revenue = sum(

            self.env["account.move"].search([

                ("move_type", "=", "out_invoice"),
                ("state", "=", "posted"),

                ("invoice_date", ">=", previous_month_start),

                ("invoice_date", "<", current_month_start),

            ]).mapped("amount_total")

        )

        revenue_trend = (

            (
                (
                    current_revenue
                    - previous_revenue
                )
                / previous_revenue
            ) * 100

            if previous_revenue

            else 100

        )

        # ==========================
        # ACHATS
        # ==========================

        current_purchases = sum(

            self.env["purchase.order"].search([

                ("state", "in", ["purchase", "done"]),

                ("date_approve", ">=", current_month_start),

            ]).mapped("amount_total")

        )

        previous_purchases = sum(

            self.env["purchase.order"].search([

                ("state", "in", ["purchase", "done"]),

                ("date_approve", ">=", previous_month_start),

                ("date_approve", "<", current_month_start),

            ]).mapped("amount_total")

        )

        purchases_trend = (

            (
                (
                    current_purchases
                    - previous_purchases
                )
                / previous_purchases
            ) * 100

            if previous_purchases

            else 100

        )


        # ==========================
        # CREANCES CLIENTS
        # ==========================

        customer_receivables = sum(

            self.env["account.move"].search([

                ("move_type", "=", "out_invoice"),

                ("state", "=", "posted"),

                ("payment_state", "in", [
                    "not_paid",
                    "partial",
                ]),

            ]).mapped("amount_residual")

        )

        # ==========================
        # COMMANDES A LIVRER
        # ==========================

        deliveries_pending = self.env[
            "stock.picking"
        ].search_count([

            ("picking_type_code", "=", "outgoing"),

            ("state", "not in", [
                "done",
                "cancel",
            ]),

        ])



        return {
            "cash_balance":
                cash_balance,

            "gross_margin":
                 gross_margin,

            "revenue": current_revenue,

            "revenue_trend": round(
                revenue_trend,
                1
            ),

            "purchases": current_purchases,

            "purchases_trend": round(
                purchases_trend,
                1
            ),

           "receivables": customer_receivables,
            "receivables_trend": 0,

            "deliveries": deliveries_pending,
            "deliveries_trend": 0,
        }

    @api.model
    def get_top_unpaid_invoices(
        self,
        filters=None
    ):

        domain = [

            ("move_type", "=", "out_invoice"),

            ("state", "=", "posted"),

            ("payment_state", "in", [
                "not_paid",
                "partial",
            ]),

        ]

        domain += self._get_date_domain(
            filters,
            "invoice_date"
        )

        invoices = self.env[
            "account.move"
        ].search(domain)

        customers = {}

        for invoice in invoices:

            partner = invoice.partner_id

            if partner.id not in customers:

                customers[partner.id] = {

                    "id": partner.id,

                    "customer": partner.name,

                    "residual": 0,

                    "invoice_count": 0,

                }

            customers[partner.id]["residual"] += (
                invoice.amount_residual
            )

            customers[partner.id]["invoice_count"] += 1

        result = sorted(

            customers.values(),

            key=lambda x: x["residual"],

            reverse=True,

        )

        return result
    
    @api.model
    def get_top_reserved_products(self, filters=None):


        domain = [

            (
                "picking_id.picking_type_code",
                "=",
                "outgoing"
            ),

            (
                "picking_id.state",
                "not in",
                [
                    "done",
                    "cancel",
                ]
            ),

        ]

        moves = self.env[
            "stock.move"
        ].search(domain)

        products = {}

        for move in moves:

            product = move.product_id

            customer = (
                move.picking_id.partner_id.name
                or "-"
            )

            if product.id not in products:

                products[product.id] = {

                    "id": product.id,

                    "name": product.display_name,

                    "qty": 0,

                    "delivery_count": 0,

                    "customers": set(),

                    "picking_ids": set(),

                    "pickings": set(),

                }

            products[product.id]["qty"] += (
                move.product_uom_qty
            )

            products[product.id]["delivery_count"] += 1

            products[product.id][
                "customers"
            ].add(customer)

            products[product.id][
                "picking_ids"
            ].add(move.picking_id.id)

            products[product.id][
                "pickings"
            ].add(move.picking_id.name)

        for product in products.values():

            product["customer"] = ", ".join(

                list(
                    product["customers"]
                )[:3]

            )

            product["picking_ids"] = list(

                product["picking_ids"]

            )

            product["pickings"] = ", ".join(

                list(
                    product["pickings"]
                )[:3]

            )

            del product["customers"]

        result = sorted(

            products.values(),

            key=lambda x: x["qty"],

            reverse=True,

        )

        return result

    @api.model
    def get_revenue_chart(self, filters=None):

        from collections import defaultdict
        from datetime import date

        filters = filters or {}

        period = filters.get(
            "period",
            "year"
        )

        # ==========================
        # FACTURES CLIENTS
        # ==========================

        domain = [

            ("move_type", "=", "out_invoice"),

            ("state", "=", "posted"),

        ]

        domain += self._get_date_domain(

            filters,

            "invoice_date"

        )

        invoices = self.env[
            "account.move"
        ].search(domain)

        revenue_chart = defaultdict(float)

        receivable_chart = defaultdict(float)

        # ====================================
        # VUE ANNUELLE
        # ====================================

        if period == "year":

            labels = [

                "Jan",
                "Fév",
                "Mar",
                "Avr",
                "Mai",
                "Juin",
                "Juil",
                "Août",
                "Sep",
                "Oct",
                "Nov",
                "Déc",

            ]

            for invoice in invoices:

                if not invoice.invoice_date:
                    continue

                month_index = (

                    invoice.invoice_date.month

                    - 1

                )

                # CA HT

                revenue_chart[
                    month_index
                ] += (
                    invoice.amount_untaxed
                )

                # Créances

                if invoice.payment_state in [

                    "not_paid",

                    "partial",

                ]:

                    receivable_chart[
                        month_index
                    ] += (
                        invoice.amount_residual
                    )

            revenue_values = [

                revenue_chart[i]

                for i in range(12)

            ]

            receivable_values = [

                receivable_chart[i]

                for i in range(12)

            ]

        # ====================================
        # VUE MENSUELLE
        # ====================================

        else:

            today = date.today()

            labels = [

                str(day)

                for day in range(
                    1,
                    today.day + 1
                )

            ]

            revenue_values = [

                0
                for _ in labels

            ]

            receivable_values = [

                0
                for _ in labels

            ]

            for invoice in invoices:

                if not invoice.invoice_date:
                    continue

                if (

                    invoice.invoice_date.month
                    != today.month

                    or

                    invoice.invoice_date.year
                    != today.year

                ):

                    continue

                idx = (
                    invoice.invoice_date.day
                    - 1
                )

                revenue_values[idx] += (

                    invoice.amount_untaxed

                )

                if invoice.payment_state in [

                    "not_paid",

                    "partial",

                ]:

                    receivable_values[idx] += (

                        invoice.amount_residual

                    )

        return {

            "labels": labels,

            "revenue": revenue_values,

            "receivables": receivable_values,

            "total_revenue": sum(
                revenue_values
            ),

            "total_receivables": sum(
                receivable_values
            ),

        }


    @api.model
    def get_activity_chart(self):

        # ==========================
        # ==========================
        # CHIFFRE D'AFFAIRES
        # ==========================

        revenue = sum(

            self.env[
                "account.move"
            ].search([

                ("move_type", "=", "out_invoice"),

                ("state", "=", "posted"),

            ]).mapped(
                "amount_untaxed"
            )

        )

        # ==========================
        # ACHATS
        # ==========================

        purchases = sum(

            self.env[
                "purchase.order"
            ].search([

                ("state", "in", [
                    "purchase",
                    "done",
                ])

            ]).mapped(
                "amount_untaxed"
            )

        )

        # ==========================
        # CREANCES
        # ==========================

        receivables = sum(

            self.env[
                "account.move"
            ].search([

                ("move_type", "=", "out_invoice"),

                ("state", "=", "posted"),

                ("payment_state", "in", [
                    "not_paid",
                    "partial",
                ])

            ]).mapped(
                "amount_residual"
            )

        )

        # ==========================
        # STOCK RESERVE
        # ==========================

        reserved_stock = self.env[
            "stock.move"
        ].search_count([

            (
                "picking_id.picking_type_code",
                "=",
                "outgoing"
            ),

            (
                "state",
                "in",
                [
                    "assigned",
                    "partially_available",
                ]
            ),

        ])

        return {

            "labels": [

                "CA",

                "Achats",

                "Créances",

                "Réservations",

            ],

            "values": [

                revenue,

                purchases,

                receivables,

                reserved_stock,

            ],

        }


    def _get_date_domain(self, filters, field_name):

        filters = filters or {}

        period = filters.get(
            "period",
            "month"
        )

        today = date.today()

        if period == "today":

            return [
                (field_name, ">=", today),
                (field_name, "<=", today),
            ]

        if period == "week":

            start = today - timedelta(
                days=today.weekday()
            )

            return [
                (field_name, ">=", start),
            ]

        if period == "month":

            start = today.replace(day=1)

            return [
                (field_name, ">=", start),
            ]

        if period == "year":

            start = today.replace(
                month=1,
                day=1
            )

            return [
                (field_name, ">=", start),
            ]

        if period == "custom":

            date_from = filters.get(
                "date_from"
            )

            date_to = filters.get(
                "date_to"
            )

            domain = []

            if date_from:

                domain.append(
                    (
                        field_name,
                        ">=",
                        date_from
                    )
                )

            if date_to:

                domain.append(
                    (
                        field_name,
                        "<=",
                        date_to
                    )
                )

            return domain

        return []
    
    @api.model
    def get_alerts(self):

        alerts = []

        # =====================================
        # CREANCES CRITIQUES
        # =====================================

        invoices = self.env[
            "account.move"
        ].search([

            ("move_type", "=", "out_invoice"),

            ("state", "=", "posted"),

            ("payment_state", "in", [
                "not_paid",
                "partial",
            ]),

        ])

        partners = {}

        for invoice in invoices:

            partner = invoice.partner_id

            if partner.id not in partners:

                partners[partner.id] = {

                    "id": partner.id,

                    "name": partner.name,

                    "amount": 0,

                }

            partners[partner.id]["amount"] += (
                invoice.amount_residual
            )

        critical_clients = [

            p

            for p in partners.values()

            if p["amount"] >= 5000000

        ]

        if critical_clients:

            alerts.append({

                "type": "danger",

                "title": "Créances Critiques",

                "count": len(critical_clients),

                "amount": sum(
                    x["amount"]
                    for x in critical_clients
                ),

                "items": sorted(

                    critical_clients,

                    key=lambda x:
                    x["amount"],

                    reverse=True,

                )[:10],

            })

        # =====================================
        # FACTURES EN RETARD
        # =====================================

        overdue_items = []

        overdue_invoices = self.env[
            "account.move"
        ].search([

            ("move_type", "=", "out_invoice"),

            ("state", "=", "posted"),

            ("payment_state", "in", [
                "not_paid",
                "partial",
            ]),

            ("invoice_date_due", "<",
            fields.Date.today()),

        ])

        for invoice in overdue_invoices:

            delay = (
                fields.Date.today()
                - invoice.invoice_date_due
            ).days

            if delay > 60:
                level = "critical"
            elif delay > 30:
                level = "warning"
            else:
                level = "normal"

            overdue_items.append({

                "id": invoice.id,

                "name": invoice.name,

                "customer": invoice.partner_id.name,

                "amount": invoice.amount_residual,

                "delay": delay,

                "level": level,

            })

        if overdue_items:

            alerts.append({

                "type": "warning",

                "title": "Factures en Retard",

                "count": len(overdue_items),

                "items": overdue_items[:10],

            })

        # =====================================
        # LIVRAISONS BLOQUEES
        # =====================================

        blocked_items = []

        pickings = self.env[
            "stock.picking"
        ].search([

            ("picking_type_code",
            "=",
            "outgoing"),

            ("state",
            "not in",
            [
                "done",
                "cancel",
            ]),

        ])

        today = fields.Date.today()

        for picking in pickings:

            if picking.scheduled_date:

                delay = (

                    today
                    -
                    picking.scheduled_date.date()

                ).days

                if delay >= 7:

                    blocked_items.append({

                        "id": picking.id,

                        "name": picking.name,

                        "amount": delay,

                    })

        if blocked_items:

            alerts.append({

                "type": "warning",

                "title": "Livraisons Bloquées",

                "count": len(blocked_items),

                "items": blocked_items[:10],

            })

    # =====================================
    # STOCK FAIBLE
    # =====================================

        low_stock_items = []

        products = self.env["product.product"].search([
            ("active", "=", True),
            ("sale_ok", "=", True),
        ])

        for product in products:

            qty = int(product.qty_available)

            # Stock faible si inférieur à 10
            if qty < 10:

                # Niveau d'alerte
                if qty <= 0:
                    level = "critical"
                elif qty < 5:
                    level = "warning"
                else:
                    level = "low"

                low_stock_items.append({

                    "id": product.id,

                    "name": product.display_name,

                    "qty": qty,

                    "sale_price": product.lst_price,

                    "level": level,

                    "model": "product.product",

                })

        # Trier du plus faible stock au plus élevé
        low_stock_items = sorted(
            low_stock_items,
            key=lambda item: item["qty"]
        )

        if low_stock_items:

            alerts.append({

                "type": "low_stock",

                "title": "⚠ Stock Faible",

                "count": len(low_stock_items),

                "items": low_stock_items,

            })
        return alerts
    
    @api.model
    def get_receivables_chart(self, filters=None):

        current_year = fields.Date.today().year

        result = {}

        for month in range(1, 13):

            invoices = self.env[
                "account.move"
            ].search([

                ("move_type", "=", "out_invoice"),

                ("state", "=", "posted"),

                ("payment_state", "in", [
                    "not_paid",
                    "partial",
                ]),

                ("invoice_date", ">=",
                date(current_year, month, 1)),

                ("invoice_date", "<=",
                date(
                    current_year,
                    month,
                    monthrange(
                        current_year,
                        month
                    )[1]
                )),

            ])

            result[month] = sum(
                invoices.mapped(
                    "amount_residual"
                )
            )
        return {
            

    "labels": [

        "Jan",
        "Fév",
        "Mar",
        "Avr",
        "Mai",
        "Juin",
        "Juil",
        "Août",
        "Sep",
        "Oct",
        "Nov",
        "Déc",

    ],

    "values": [

        result.get(i, 0)

        for i in range(1, 13)

    ]

}