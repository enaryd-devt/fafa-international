from odoo import api, fields, models


class StockReplenishmentLine(models.Model):
    _name = "pt.stock.replenishment.line"
    _description = "Ligne Réapprovisionnement"
    _order = "categ_id, product_id"

    replenishment_id = fields.Many2one(
        "pt.stock.replenishment",
        string="Bon",
        required=True,
        ondelete="cascade",
    )

    selected = fields.Boolean(
        string="Commander",
        default=True,
    )

    product_id = fields.Many2one(
        "product.product",
        string="Article",
        required=True,
    )

    categ_id = fields.Many2one(
        "product.category",
        string="Catégorie",
        related="product_id.categ_id",
        store=True,
        readonly=True,
    )

    supplier_id = fields.Many2one(
        "res.partner",
        string="Fournisseur",
        compute="_compute_supplier",
        store=True,
    )

    qty_available = fields.Float(
        string="Stock Actuel",
    )

    alert_quantity = fields.Float(
        string="Seuil d'Alerte",
    )

    optimal_quantity = fields.Float(
        string="Stock Optimal",
    )

    qty_to_order = fields.Float(
        string="Qté à Commander",
        required=True,
    )

    urgency = fields.Selection(
        [
            ("critical", "Critique"),
            ("high", "Elevée"),
            ("medium", "Moyenne"),
            ("low", "Faible"),
        ],
        string="Urgence",
        compute="_compute_urgency",
        store=True,
    )

    @api.depends("product_id")
    def _compute_supplier(self):

        for line in self:

            supplier = False

            if (
                line.product_id
                and
                line.product_id.seller_ids
            ):

                supplier = (
                    line.product_id
                    .seller_ids[0]
                    .partner_id
                )

            line.supplier_id = supplier

    @api.depends(
        "qty_available",
        "alert_quantity",
    )
    def _compute_urgency(self):

        for line in self:

            if not line.alert_quantity:

                line.urgency = "low"
                continue

            if line.qty_available <= 0:

                line.urgency = "critical"

            elif (
                line.qty_available
                <=
                (line.alert_quantity * 0.50)
            ):

                line.urgency = "high"

            elif (
                line.qty_available
                <=
                line.alert_quantity
            ):

                line.urgency = "medium"

            else:

                line.urgency = "low"