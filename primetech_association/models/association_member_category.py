# -*- coding: utf-8 -*-

##############################################################################
#
#    PrimeTech Association Management
#    Copyright (C) 2026 PrimeTech Services
#
#    Author: PrimeTech Services
#    License LGPL-3
#
##############################################################################

from odoo import fields, models


class AssociationMemberCategory(models.Model):
    _name = "association.member.category"
    _description = "Association Member Category"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "sequence, name"

    # ==========================================================
    # TECHNICAL
    # ==========================================================

    active = fields.Boolean(
        string="Active",
        default=True,
        tracking=True,
    )

    sequence = fields.Integer(
        string="Sequence",
        default=10,
    )

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
    )

    color = fields.Integer(
        string="Color",
    )

    # ==========================================================
    # INFORMATION
    # ==========================================================

    name = fields.Char(
        string="Category",
        required=True,
        tracking=True,
        translate=True,
    )

    code = fields.Char(
        string="Code",
        tracking=True,
    )

    description = fields.Text(
        string="Description",
    )

    # ==========================================================
    # SETTINGS
    # ==========================================================

    is_default = fields.Boolean(
        string="Default Category",
        default=False,
    )

    # ==========================================================
    # RELATIONS
    # ==========================================================

    member_ids = fields.One2many(
        "association.member",
        "category_id",
        string="Members",
    )

    member_count = fields.Integer(
        string="Members",
        compute="_compute_member_count",
    )

    # ==========================================================
    # NOTES
    # ==========================================================

    note = fields.Html(
        string="Notes",
    )

    # ==========================================================
    # COMPUTE
    # ==========================================================

    def _compute_member_count(self):
        """
        Placeholder.
        The real implementation will be completed in V1.
        """
        for record in self:
            record.member_count = len(record.member_ids)