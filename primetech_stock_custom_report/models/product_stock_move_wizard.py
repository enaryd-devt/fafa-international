from odoo import models, fields, api
from odoo.exceptions import UserError


class ProductStockMoveWizard(models.TransientModel):
    _name = 'product.stock.move.wizard'
    _description = 'Wizard impression mouvements stock'

    product_tmpl_id = fields.Many2one('product.template', string='Article')

    product_ids = fields.Many2many('product.product', string='Articles')
    category_ids = fields.Many2many('product.category', string='Catégories')

    date_start = fields.Datetime(string='Date début', required=True)
    date_end = fields.Datetime(string='Date fin', required=True)

    move_type = fields.Selection([
        ('all', 'Tous'),
        ('in', 'Réception'),
        ('out', 'Livraison'),
        ('internal', 'Transfert interne')
    ], default='all')

    # =========================
    # ONCHANGE : blocage logique
    # =========================
    @api.onchange('category_ids')
    def _onchange_category_ids(self):
        if self.category_ids:
            self.product_ids = False

    @api.onchange('product_ids')
    def _onchange_product_ids(self):
        if self.product_ids:
            self.category_ids = False

    # =========================
    # CONTEXTE (depuis produit)
    # =========================
    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        active_model = self.env.context.get('active_model')
        active_id = self.env.context.get('active_id')

        if active_model == 'product.template' and active_id:
            res['product_tmpl_id'] = active_id

        return res

    # =========================
    # ACTION PRINT
    # =========================
    def action_print_report(self):
        self.ensure_one()

        if self.date_start > self.date_end:
            raise UserError("La date début doit être inférieure à la date fin.")

        domain = [
            ('date', '>=', self.date_start),
            ('date', '<=', self.date_end),
        ]

        # =========================
        # PRODUITS / CATÉGORIES
        # =========================
        product_ids = []

        if self.product_tmpl_id:
            product_ids = self.product_tmpl_id.product_variant_ids.ids

        elif self.product_ids:
            product_ids = self.product_ids.ids

        elif self.category_ids:
            product_ids = self.env['product.product'].search([
                ('categ_id', 'in', self.category_ids.ids)
            ]).ids

        if product_ids:
            domain.append(('product_id', 'in', product_ids))

        # =========================
        # TYPE MOUVEMENT
        # =========================
        if self.move_type == 'in':
            domain.append(('picking_id.picking_type_id.code', '=', 'incoming'))
        elif self.move_type == 'out':
            domain.append(('picking_id.picking_type_id.code', '=', 'outgoing'))
        elif self.move_type == 'internal':
            domain.append(('picking_id.picking_type_id.code', '=', 'internal'))

        moves = self.env['stock.move.line'].search(domain)

        if not moves:
            raise UserError("Aucun mouvement trouvé.")

        return self.env.ref(
            'primetech_stock_custom_report.action_stock_move_line_report'
        ).report_action(moves)