from odoo import fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    primetech_agency_id = fields.Many2one("primetech.agency", string="Agence PrimeTech", index=True)
    primetech_is_transit = fields.Boolean(string="Emplacement de transit PrimeTech")
