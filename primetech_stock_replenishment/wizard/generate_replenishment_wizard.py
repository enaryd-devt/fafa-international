from odoo import fields, models


class GenerateReplenishmentWizard(models.TransientModel):
    _name = "pt.generate.replenishment.wizard"
    _description = "Génération Réapprovisionnement"

    category_ids = fields.Many2many(
        "product.category",
        string="Catégories"
    )

    only_with_supplier = fields.Boolean(
        string="Uniquement les articles ayant un fournisseur",
        default=True,
    )

    def action_generate(self):

        replenishment = self.env[
            "pt.stock.replenishment"
        ].create({})

        domain = [
            ("alert_quantity", ">", 0),
        ]

        if self.category_ids:

            domain.append(
                (
                    "categ_id",
                    "in",
                    self.category_ids.ids
                )
            )

        products = self.env[
            "product.product"
        ].search(
            domain,
            order="categ_id,name"
        )

        lines = []

        for product in products:

            if (
                product.qty_available
                >
                product.alert_quantity
            ):
                continue

            if (
                self.only_with_supplier
                and
                not product.seller_ids
            ):
                continue

            qty_to_order = max(
                (
                    product.optimal_quantity
                    -
                    product.qty_available
                ),
                0
            )

            lines.append((0, 0, {

                "product_id":
                    product.id,

                "qty_available":
                    product.qty_available,

                "alert_quantity":
                    product.alert_quantity,

                "optimal_quantity":
                    product.optimal_quantity,

                "qty_to_order":
                    qty_to_order,

            }))

        replenishment.write({

            "line_ids": lines

        })

        return {

            "type":
                "ir.actions.act_window",

            "res_model":
                "pt.stock.replenishment",

            "res_id":
                replenishment.id,

            "view_mode":
                "form",

            "target":
                "current",
        }