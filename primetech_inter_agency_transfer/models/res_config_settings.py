from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    primetech_insufficient_stock_policy = fields.Selection(
        [
            ("block", "Bloquer le transfert"),
            ("warning", "Autoriser avec avertissement"),
            ("manager_only", "Autoriser le responsable logistique uniquement"),
        ],
        string="Politique de stock insuffisant",
        config_parameter="primetech_inter_agency_transfer.insufficient_stock_policy",
        default="block",
    )
