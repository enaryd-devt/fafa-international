from odoo import models, fields, api
from datetime import datetime
import json


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # =====================================================
    # STOCK ALERT QUANTITY
    # =====================================================

    alert_quantity = fields.Float(
        string="Alert Quantity",
        compute="_compute_alert_quantity",
        inverse="_inverse_alert_quantity",
        store=False
    )

    # NOTE: éviter de redéclarer qty_available (déjà Odoo)
    # On utilise directement le champ standard

    # =====================================================
    # COLOR FIELD (KANBAN)
    # =====================================================

    color_field = fields.Char(
        string="Color",
        compute='_compute_color_field',
        store=False
    )

    # =====================================================
    # LOT EXPIRATION ALERT (JSON FOR KANBAN)
    # =====================================================

    lot_alert_ids = fields.Text(
        string="Lot Alerts",
        compute="_compute_lot_alert_ids",
        store=False
    )

    # =====================================================
    # MARGIN
    # =====================================================

    margin_amount = fields.Float(
        string="Margin",
        compute="_compute_margin_amount",
        store=False
    )

    # =====================================================
    # COMPUTE METHODS
    # =====================================================

    @api.depends('list_price', 'standard_price')
    def _compute_margin_amount(self):
        for product in self:
            product.margin_amount = product.list_price - product.standard_price

    # -----------------------------------------------------

    @api.depends('qty_available', 'alert_quantity')
    def _compute_color_field(self):
        for product in self:
            product.color_field = (
                '#f08080' if product.qty_available <= product.alert_quantity else ''
            )

    # -----------------------------------------------------

    @api.depends('product_variant_ids.alert_quantity')
    def _compute_alert_quantity(self):
        for template in self:
            template.alert_quantity = (
                template.product_variant_ids[0].alert_quantity
                if template.product_variant_ids else 0.0
            )

    def _inverse_alert_quantity(self):
        for template in self:
            if template.product_variant_ids:
                template.product_variant_ids[0].alert_quantity = template.alert_quantity

    # -----------------------------------------------------
    # LOT EXPIRATION ALERT
    # -----------------------------------------------------

    @api.depends('product_variant_ids')
    def _compute_lot_alert_ids(self):

        today = fields.Date.context_today(self)
        warning_days = 7

        for template in self:

            alerts = []

            # sécurité tracking
            if template.tracking != 'lot':
                template.lot_alert_ids = json.dumps([])
                continue

            # correction relation lot -> product.product -> template
            lots = self.env['stock.lot'].search([
                ('product_id.product_tmpl_id', '=', template.id),
                ('expiration_date', '!=', False),
                ('product_qty', '>', 0),
            ])

            for lot in lots:

                expiration_date = lot.expiration_date

                # normalisation date
                if isinstance(expiration_date, datetime):
                    expiration_date = expiration_date.date()

                if not expiration_date:
                    continue

                days_left = (expiration_date - today).days

                if days_left < 0:
                    status = "expired"
                elif days_left <= warning_days:
                    status = "warning"
                else:
                    status = "ok"

                alerts.append({
                    'name': lot.name,
                    'expiration_date_display': expiration_date.strftime('%d/%m/%Y'),
                    'product_qty': round(lot.product_qty, 2),
                    'days_left': days_left,
                    'status': status,
                })

            template.lot_alert_ids = json.dumps(alerts)
            print("PRODUCT TEMPLATE LOADED")