# -*- coding: utf-8 -*-

from datetime import timedelta
from dateutil.relativedelta import relativedelta

from odoo import api
from odoo import fields
from odoo import models


class StockDashboard(
    models.AbstractModel
):
    _name = "pt.stock.dashboard"
    _description = (
        "Stock Dashboard Service"
    )

    @api.model
    def get_dashboard_data(
        self,
    ):

        Product = self.env[
            "product.product"
        ]

        Quant = self.env[
            "stock.quant"
        ]

        Move = self.env[
            "stock.move"
        ]

        Picking = self.env[
            "stock.picking"
        ]

        Category = self.env[
            "product.category"
        ]

        Location = self.env[
            "stock.location"
        ]

        Lot = self.env[
            "stock.lot"
        ]

        # =====================================
        # KPI PRINCIPAUX
        # =====================================

        all_products = Product.search([])

        products_count = len(all_products)

        all_quants = Quant.search([
            (
                "location_id.usage",
                "=",
                "internal"
            )
        ])

        stock_qty = round(

            sum(
                all_quants.mapped(
                    "quantity"
                )
            ),

            2

        )

        stock_value = round(

            sum(

                product.qty_available
                *
                product.standard_price

                for product in all_products

            ),

            2

        )

        out_of_stock = len(

            all_products.filtered(

                lambda p:
                p.qty_available <= 0

            )

        )

        locations_count = (
            Location.search_count([
                (
                    "usage",
                    "=",
                    "internal"
                )
            ])
        )

        lots_count = (
            Lot.search_count([])
        )

        pending_pickings = (
            Picking.search_count([
                (
                    "state",
                    "not in",
                    [
                        "done",
                        "cancel"
                    ]
                )
            ])
        )
        # =====================================
        # PRODUITS DORMANTS
        # =====================================

        limit_date = (

            fields.Date.today()

            - timedelta(
                days=90
            )

        )

        active_products = Move.search([

            (
                "date",
                ">=",
                limit_date,
            ),

            (
                "state",
                "=",
                "done",
            ),

        ]).mapped(
            "product_id"
        )

        dormant_products = len(

            all_products.filtered(

                lambda p:
                p.id not in active_products.ids

            )

        )

        # =====================================
        # MOUVEMENTS DU MOIS
        # =====================================

        today = (
            fields.Date.today()
        )

        first_day = today.replace(
            day=1
        )

        incoming_count = (
            Move.search_count([

                (
                    "state",
                    "=",
                    "done"
                ),

                (
                    "date",
                    ">=",
                    first_day
                ),

                (
                    "picking_type_id.code",
                    "=",
                    "incoming"
                )

            ])
        )

        outgoing_count = (
            Move.search_count([

                (
                    "state",
                    "=",
                    "done"
                ),

                (
                    "date",
                    ">=",
                    first_day
                ),

                (
                    "picking_type_id.code",
                    "=",
                    "outgoing"
                )

            ])
        )

        internal_count = (
            Move.search_count([

                (
                    "state",
                    "=",
                    "done"
                ),

                (
                    "date",
                    ">=",
                    first_day
                ),

                (
                    "picking_type_id.code",
                    "=",
                    "internal"
                )

            ])
        )

        # =====================================
        # TOP PRODUITS
        # =====================================

        top_products = []

        products = all_products

        products = sorted(

            products,

            key=lambda p:
            p.qty_available,

            reverse=True

        )[:10]

        for product in products:

            reserved_qty = round(

                abs(
                    product.qty_available
                    -
                    product.virtual_available
                ),

                2

            )

            top_products.append({

                "id":
                    product.id,

                "name":
                    product.display_name,

                "qty":
                    round(
                        product.qty_available,
                        2
                    ),

                "reserved":
                    round(
                        reserved_qty,
                        2
                    ),

                "value":
                    round(

                        product.qty_available
                        *
                        product.standard_price,

                        2

                    ),

            })
            # =====================================
            # REPARTITION PAR CATEGORIE
            # =====================================

            categories = []

            category_data = {}

            internal_quants = Quant.search([
                (
                    "location_id.usage",
                    "=",
                    "internal"
                )
            ])

            for quant in internal_quants:

                product = quant.product_id

                category = product.categ_id

                if not category:
                    continue

                if category.id not in category_data:

                    category_data[
                        category.id
                    ] = {

                        "id":
                            category.id,

                        "name":
                            category.display_name,

                        "qty":
                            0.0,

                        "value":
                            0.0,

                    }

                category_data[
                    category.id
                ]["qty"] += quant.quantity

                category_data[
                    category.id
                ]["value"] += (

                    quant.quantity
                    *
                    product.standard_price

                )

            categories = list(
                category_data.values()
            )

            categories = sorted(

                categories,

                key=lambda x:
                x["value"],

                reverse=True

            )[:10]

        # =====================================
        # EVOLUTION 12 MOIS
        # =====================================

        monthly_moves = []

        current_month = (
            fields.Date.today()
            .replace(day=1)
        )

        for i in range(
            11,
            -1,
            -1
        ):

            month_start = (
                current_month
                -
                relativedelta(
                    months=i
                )
            )

            month_end = (

                month_start

                +
                relativedelta(
                    months=1
                )

                -
                relativedelta(
                    days=1
                )

            )

            incoming = (
                Move.search_count([

                    (
                        "state",
                        "=",
                        "done"
                    ),

                    (
                        "date",
                        ">=",
                        month_start
                    ),

                    (
                        "date",
                        "<=",
                        month_end
                    ),

                    (
                        "picking_type_id.code",
                        "=",
                        "incoming"
                    ),

                ])
            )

            outgoing = (
                Move.search_count([

                    (
                        "state",
                        "=",
                        "done"
                    ),

                    (
                        "date",
                        ">=",
                        month_start
                    ),

                    (
                        "date",
                        "<=",
                        month_end
                    ),

                    (
                        "picking_type_id.code",
                        "=",
                        "outgoing"
                    ),

                ])
            )

            internal = (
                Move.search_count([

                    (
                        "state",
                        "=",
                        "done"
                    ),

                    (
                        "date",
                        ">=",
                        month_start
                    ),

                    (
                        "date",
                        "<=",
                        month_end
                    ),

                    (
                        "picking_type_id.code",
                        "=",
                        "internal"
                    ),

                ])
            )

            monthly_moves.append({

                "month":
                    month_start.strftime(
                        "%b %Y"
                    ),

                "incoming":
                    incoming,

                "outgoing":
                    outgoing,

                "internal":
                    internal,

            })

        # =====================================
        # STATISTIQUES
        # =====================================

        statistics = {

            "average_stock_value":

                round(

                    stock_value /
                    products_count,

                    2

                )

                if products_count > 0

                else 0,

        }

        # =====================================
        # RETOUR
        # =====================================

        return {

            "products_count":
                products_count,

            "stock_qty":
                stock_qty,

            "stock_value":
                stock_value,

            "out_of_stock":
                out_of_stock,

            "dormant_products":
                dormant_products,

            "locations_count":
                locations_count,

            "lots_count":
                lots_count,

            "pending_pickings":
                pending_pickings,

            "incoming_count":
                incoming_count,

            "outgoing_count":
                outgoing_count,

            "internal_count":
                internal_count,

            "top_products":
                top_products,

            "categories":
                categories,

            "monthly_moves":
                monthly_moves,

            "statistics":
                statistics,

        }