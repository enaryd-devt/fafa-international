from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def action_print_stock_move_activity_report(self):
        return self.env.ref(
            "stock_move_line_activity_report.action_stock_move_line_activity_report"
        ).report_action(self)