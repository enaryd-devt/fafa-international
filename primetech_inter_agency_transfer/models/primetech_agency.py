from odoo import fields, models


class PrimetechAgency(models.Model):
    _name = "primetech.agency"
    _description = "Agence PrimeTech"
    _order = "company_id, name"
    _check_company_auto = True

    name = fields.Char(string="Nom", required=True, index=True)
    code = fields.Char(string="Code", required=True, index=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company, index=True
    )
    warehouse_ids = fields.One2many("stock.warehouse", "primetech_agency_id", string="Entrepôts")
    location_ids = fields.One2many("stock.location", "primetech_agency_id", string="Emplacements")
    manager_ids = fields.Many2many(
        "res.users", "primetech_agency_manager_rel", "agency_id", "user_id", string="Gestionnaires"
    )
    warehouseman_ids = fields.Many2many(
        "res.users", "primetech_agency_warehouseman_rel", "agency_id", "user_id", string="Magasiniers"
    )
    address = fields.Text(string="Adresse")
    phone = fields.Char(string="Téléphone")
    email = fields.Char(string="E-mail")
    active = fields.Boolean(string="Actif", default=True)

    _sql_constraints = [
        ("primetech_agency_code_company_uniq", "unique(code, company_id)", "Le code de l'agence doit être unique par société."),
    ]
