from odoo import models


class StockReplenishmentReport(models.AbstractModel):
    _name = "report.primetech_stock_replenishment.stock_replenishment_report"

    def _get_report_values(self, docids, data=None):

        docs = self.env[
            "pt.stock.replenishment"
        ].browse(docids)

        return {
            "doc_ids": docids,
            "doc_model": "pt.stock.replenishment",
            "docs": docs,
        }