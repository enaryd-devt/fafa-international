from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    primetech_transfer_id = fields.Many2one(
        "primetech.inter.agency.transfer", string="Transfert PrimeTech", index=True, copy=False
    )


class StockMove(models.Model):
    _inherit = "stock.move"

    primetech_transfer_line_id = fields.Many2one(
        "primetech.inter.agency.transfer.line", string="Ligne de transfert PrimeTech", index=True, copy=False
    )
