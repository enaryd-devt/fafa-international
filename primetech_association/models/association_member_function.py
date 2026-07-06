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


class AssociationMemberFunction(models.Model):
    _name = "association.member.function"
    _description = "Association Member Function"
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
        string="Color Index",
    )

    # ==========================================================
    # INFORMATION
    # ==========================================================

    name = fields.Char(
        string="Function",
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
    # OPTIONS
    # ==========================================================

    executive_member = fields.Boolean(
        string="Executive Committee",
        help="Indicates whether this function belongs to the Executive Committee.",
    )

    election_required = fields.Boolean(
        string="Election Required",
        help="This position requires an election.",
    )

    max_holders = fields.Integer(
        string="Maximum Holders",
        default=1,
        help="Maximum number of members that can simultaneously occupy this function.",
    )

    # ==========================================================
    # RELATIONS
    # ==========================================================

    member_ids = fields.One2many(
        "association.member",
        "function_id",
        string="Members",
    )

    member_count = fields.Integer(
        string="Number of Members",
        compute="_compute_member_count",
    )

    # ==========================================================
    # NOTES
    # ==========================================================

    note = fields.Html(
        string="Internal Notes",
    )

    # ==========================================================
    # COMPUTE
    # ==========================================================

    def _compute_member_count(self):
        """
        Placeholder.
        The business logic will be enriched during V1.
        """
        for record in self:
            record.member_count = len(record.member_ids)