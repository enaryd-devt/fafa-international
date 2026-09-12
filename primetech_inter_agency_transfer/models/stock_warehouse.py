from odoo import api, fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    primetech_agency_id = fields.Many2one("primetech.agency", string="Agence PrimeTech", index=True)

    @api.depends("code", "name")
    def _compute_display_name(self):
        for warehouse in self:
            warehouse.display_name = "[%s] %s" % (warehouse.code, warehouse.name) if warehouse.code else warehouse.name
