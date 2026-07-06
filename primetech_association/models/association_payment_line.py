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

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AssociationPaymentLine(models.Model):
    _name = "association.payment.line"
    _description = "Ligne d'affectation de paiement"
    _order = "id"

    # ==========================================================
    # TECHNIQUE
    # ==========================================================

    active = fields.Boolean(
        string="Actif",
        default=True,
    )

    sequence = fields.Integer(
        string="Séquence",
        default=10,
    )

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Filiale",
        related="payment_id.company_id",
        store=True,
        readonly=True,
        index=True,
    )

    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Devise",
        related="payment_id.currency_id",
        store=True,
        readonly=True,
    )

    # ==========================================================
    # PAIEMENT
    # ==========================================================

    payment_id = fields.Many2one(
        comodel_name="association.payment",
        string="Paiement",
        required=True,
        ondelete="cascade",
        index=True,
    )

    payment_date = fields.Date(
        related="payment_id.payment_date",
        string="Date de paiement",
        store=True,
        readonly=True,
    )

    amount_received = fields.Monetary(
        string="Montant reçu",
        currency_field="currency_id",
        default=0.0,
        copy=False,
    )

    # ==========================================================
    # AFFECTATION
    # ==========================================================

    subscription_line_id = fields.Many2one(
        comodel_name="association.subscription.line",
        string="Ligne de cotisation",
        required=True,
        ondelete="restrict",
        index=True,
    )

    subscription_id = fields.Many2one(
        related="subscription_line_id.subscription_id",
        string="Cotisation",
        store=True,
        readonly=True,
    )

    member_id = fields.Many2one(
        related="subscription_line_id.member_id",
        string="Membre",
        store=True,
        readonly=True,
    )

    member_code = fields.Char(
        related="subscription_line_id.member_code",
        string="Code membre",
        store=True,
        readonly=True,
    )

    # ==========================================================
    # MONTANTS
    # ==========================================================

    amount_due = fields.Monetary(
        related="subscription_line_id.amount_due",
        string="Montant dû",
        currency_field="currency_id",
        readonly=True,
    )

    amount_already_paid = fields.Monetary(
        string="Déjà payé",
        currency_field="currency_id",
        compute="_compute_payment_amounts",
    )

    balance_before_payment = fields.Monetary(
        string="Reste avant paiement",
        currency_field="currency_id",
        compute="_compute_payment_amounts",
    )

    amount_paid = fields.Monetary(
        string="Montant affecté",
        currency_field="currency_id",
        required=True,
        default=0.0,
    )

    balance_after_payment = fields.Monetary(
        string="Reste après paiement",
        currency_field="currency_id",
        compute="_compute_payment_amounts",
    )

    # ==========================================================
    # PÉNALITÉ DE RETARD
    # ==========================================================

    is_late = fields.Boolean(
        string="Paiement en retard",
        compute="_compute_penalty_information",
    )

    late_days = fields.Integer(
        string="Jours de retard",
        compute="_compute_penalty_information",
    )

    penalty_amount = fields.Monetary(
        string="Pénalité de retard",
        currency_field="currency_id",
        default=0.0,
    )

    total_with_penalty = fields.Monetary(
        string="Total avec pénalité",
        currency_field="currency_id",
        compute="_compute_total_with_penalty",
    )

    # ==========================================================
    # ÉTAT DE L'AFFECTATION
    # ==========================================================

    allocation_state = fields.Selection(
        selection=[
            ("draft", "À valider"),
            ("partial", "Paiement partiel"),
            ("confirmed", "Affecté"),
            ("cancelled", "Annulé"),
        ],
        string="État de l'affectation",
        compute="_compute_allocation_state",
    )

    # ==========================================================
    # NOTES
    # ==========================================================

    note = fields.Html(
        string="Notes internes",
    )

    # ==========================================================
    # CALCUL DES MONTANTS
    # ==========================================================

    @api.depends(
        "subscription_line_id",
        "subscription_line_id.amount_due",
        "subscription_line_id.payment_line_ids.amount_paid",
        "subscription_line_id.payment_line_ids.payment_id.state",
        "subscription_line_id.payment_line_ids.payment_id.subscription_period_id",
        "amount_paid",
        "payment_id.state",
        "payment_id.subscription_period_id",
    )
    def _compute_payment_amounts(self):

        for record in self:

            amount_due = record.amount_due or 0.0

            if not record.subscription_line_id:

                record.amount_already_paid = 0.0
                record.balance_before_payment = amount_due
                record.balance_after_payment = amount_due

                continue

            current_period = (
                record.payment_id.subscription_period_id
            )

            # ======================================================
            # PAIEMENTS CONFIRMÉS DU MÊME CYCLE
            # ======================================================

            confirmed_lines = (
                record.subscription_line_id
                .payment_line_ids
                .filtered(
                    lambda line: (
                        line.payment_id
                        and
                        line.payment_id.state == "confirmed"
                        and
                        line.id != record.id
                        and
                        line.payment_id.subscription_period_id
                        == current_period
                    )
                )
            )

            amount_already_paid = sum(
                confirmed_lines.mapped(
                    "amount_paid"
                )
            )

            balance_before = max(
                amount_due - amount_already_paid,
                0.0,
            )

            current_amount = (
                record.amount_paid or 0.0
            )

            record.amount_already_paid = (
                amount_already_paid
            )

            record.balance_before_payment = (
                balance_before
            )

            record.balance_after_payment = max(
                balance_before - current_amount,
                0.0,
            )
    # ==========================================================
    # CALCUL DU RETARD
    # ==========================================================

    @api.depends(
        "payment_id.payment_date",
        "payment_id.state",
        "subscription_line_id",
        "subscription_line_id.subscription_id",
        "subscription_line_id.subscription_id.period_ids",
        "subscription_line_id.subscription_id.period_ids.state",
        "subscription_line_id.subscription_id.period_ids.due_date",
        "subscription_line_id.subscription_id.period_ids.sequence",
    )
    def _compute_penalty_information(self):

        for record in self:

            record.is_late = False
            record.penalty_amount = 0.0

            subscription_line = (
                record.subscription_line_id
            )

            if not subscription_line:
                continue

            subscription = (
                subscription_line.subscription_id
            )

            if not subscription:
                continue

            payment_date = (
                record.payment_id.payment_date
                or fields.Date.context_today(record)
            )

            # ==================================================
            # RECHERCHER LE CYCLE CONCERNÉ PAR LE PAIEMENT
            # ==================================================

            periods = subscription.period_ids.filtered(
                lambda period:
                    period.state
                    in (
                        "running",
                        "closed",
                    )
                    and period.period_start_date
                    and period.period_end_date
                    and period.period_start_date
                    <= payment_date
                    <= period.period_end_date
            )

            # ==================================================
            # SI AUCUN CYCLE PAR DATE :
            # PRENDRE LE CYCLE EN COURS
            # ==================================================

            if not periods:

                periods = (
                    subscription.period_ids.filtered(
                        lambda period:
                            period.state == "running"
                    )
                )

            if not periods:
                continue

            period = periods.sorted(
                key=lambda item: (
                    item.sequence,
                    item.id,
                ),
                reverse=True,
            )[0]

            due_date = period.due_date

            if not due_date:
                continue

            # ==================================================
            # CONTRÔLE DU RETARD
            # ==================================================

            record.is_late = bool(
                payment_date > due_date
            )

            if not record.is_late:
                continue

            # ==================================================
            # CALCUL DE LA PÉNALITÉ
            # ==================================================

            subscription = (
                subscription_line.subscription_id
            )

            penalty_amount = 0.0

            # --------------------------------------------------
            # PÉNALITÉ FIXE
            # --------------------------------------------------

            if (
                hasattr(subscription, "penalty_type")
                and subscription.penalty_type == "fixed"
            ):

                penalty_amount = (
                    subscription.penalty_amount or 0.0
                )

            # --------------------------------------------------
            # PÉNALITÉ EN POURCENTAGE
            # --------------------------------------------------

            elif (
                hasattr(subscription, "penalty_type")
                and subscription.penalty_type == "percentage"
            ):

                penalty_rate = (
                    subscription.penalty_rate or 0.0
                )

                penalty_amount = (
                    (record.amount_paid or 0.0)
                    * penalty_rate
                    / 100.0
                )

            record.penalty_amount = penalty_amount
    
    # ==========================================================
    # TOTAL AVEC PÉNALITÉ
    # ==========================================================

    @api.depends(
        "amount_paid",
        "penalty_amount",
    )
    def _compute_total_with_penalty(self):
        for record in self:
            record.total_with_penalty = (
                (record.amount_paid or 0.0)
                + (record.penalty_amount or 0.0)
            )

    # ==========================================================
    # ÉTAT DE L'AFFECTATION
    # ==========================================================

    @api.depends(
        "payment_id.state",
        "amount_paid",
        "balance_after_payment",
    )
    def _compute_allocation_state(self):
        for record in self:

            if record.payment_id.state == "cancelled":

                record.allocation_state = "cancelled"

            elif record.payment_id.state != "confirmed":

                record.allocation_state = "draft"

            elif record.balance_after_payment > 0:

                record.allocation_state = "partial"

            else:

                record.allocation_state = "confirmed"

    # ==========================================================
    # ONCHANGE
    # ==========================================================

    @api.onchange("subscription_line_id")
    def _onchange_subscription_line_id(self):
        for record in self:

            if not record.subscription_line_id:
                continue

            if record.balance_before_payment > 0:
                record.amount_paid = (
                    record.balance_before_payment
                )

    # ==========================================================
    # CONTRAINTES
    # ==========================================================

    @api.constrains(
        "amount_paid",
        "penalty_amount",
    )
    def _check_amounts(self):
        for record in self:

            if record.amount_paid < 0:
                raise ValidationError(
                    _(
                        "Le montant affecté ne peut pas "
                        "être négatif."
                    )
                )

            if record.penalty_amount < 0:
                raise ValidationError(
                    _(
                        "La pénalité de retard ne peut pas "
                        "être négative."
                    )
                )


    # ==========================================================
    # CONTRÔLE FILIALE
    # ==========================================================

    @api.constrains(
        "payment_id",
        "subscription_line_id",
    )
    def _check_company(self):
        for record in self:

            if (
                record.payment_id
                and record.subscription_line_id
                and record.payment_id.company_id
                != record.subscription_line_id.company_id
            ):
                raise ValidationError(
                    _(
                        "Le paiement et la cotisation doivent "
                        "appartenir à la même Filiale."
                    )
                )
            
    # ==========================================================
    # PROTECTION DE SUPPRESSION
    # ==========================================================

    def unlink(self):
        for record in self:

            if (
                record.payment_id
                and record.payment_id.state == "confirmed"
            ):
                raise ValidationError(
                    _(
                        "Impossible de supprimer cette ligne.\n\n"
                        "Le paiement est déjà confirmé et le montant "
                        "a été affecté à la cotisation.\n\n"
                        "Vous devez d'abord annuler le paiement."
                    )
                )

        return super().unlink()