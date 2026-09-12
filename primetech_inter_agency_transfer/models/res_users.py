from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    primetech_agency_ids = fields.Many2many(
        "primetech.agency", "primetech_agency_user_rel", "user_id", "agency_id", string="Agences autorisées"
    )
