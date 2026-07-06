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

from odoo import fields, models, _
from odoo.exceptions import UserError, ValidationError


class AssociationPaymentSurplusWizard(models.TransientModel):
    _name = "association.payment.surplus.wizard"
    _description = "Traitement du surplus de paiement"

    # ==========================================================
    # PAIEMENT
    # ==========================================================

    payment_id = fields.Many2one(
        comodel_name="association.payment",
        string="Paiement",
        required=True,
        readonly=True,
        ondelete="cascade",
    )

    member_id = fields.Many2one(
        comodel_name="association.member",
        string="Membre",
        required=True,
        readonly=True,
    )

    company_id = fields.Many2one(
        related="payment_id.company_id",
        string="Filiale",
        readonly=True,
    )

    currency_id = fields.Many2one(
        related="payment_id.currency_id",
        string="Devise",
        readonly=True,
    )

    # ==========================================================
    # MONTANTS
    # ==========================================================

    received_amount = fields.Monetary(
        string="Montant reçu",
        currency_field="currency_id",
        required=True,
        readonly=True,
    )

    allocated_amount = fields.Monetary(
        string="Affecté à la cotisation",
        currency_field="currency_id",
        required=True,
        readonly=True,
    )

    surplus_amount = fields.Monetary(
        string="Surplus",
        currency_field="currency_id",
        required=True,
        readonly=True,
    )

    # ==========================================================
    # TRAITEMENT DU SURPLUS
    # ==========================================================

    surplus_action = fields.Selection(
        selection=[
            (
                "credit_account",
                "Créditer le compte du membre",
            ),
            (
                "refund",
                "Rembourser le membre",
            ),
        ],
        string="Traitement du surplus",
        required=True,
        default="credit_account",
    )

    note = fields.Text(
        string="Observation",
    )

    # ==========================================================
    # ACTION - CONFIRMER
    # ==========================================================

    def action_confirm(self):
        self.ensure_one()

        payment = self.payment_id

        if not payment:
            raise UserError(
                _("Aucun paiement n'est associé à cet assistant.")
            )

        if payment.state != "draft":
            raise UserError(
                _(
                    "Le paiement %(payment)s n'est plus "
                    "en brouillon."
                )
                % {
                    "payment": payment.display_name,
                }
            )

        if self.surplus_amount <= 0:
            raise ValidationError(
                _("Aucun surplus positif n'est disponible.")
            )

        # ======================================================
        # CRÉDITER LE COMPTE DU MEMBRE
        # ======================================================

        if self.surplus_action == "credit_account":

            MemberAccount = self.env[
                "association.member.account"
            ]

            AccountTransaction = self.env[
                "association.member.account.transaction"
            ]

            member_account = MemberAccount.search(
                [
                    (
                        "member_id",
                        "=",
                        self.member_id.id,
                    ),
                    (
                        "company_id",
                        "=",
                        payment.company_id.id,
                    ),
                ],
                limit=1,
            )

            # ==================================================
            # CRÉATION DU COMPTE SI INEXISTANT
            # ==================================================

            if not member_account:

                member_account = MemberAccount.create({
                    "member_id":
                        self.member_id.id,

                    "company_id":
                        payment.company_id.id,
                })

            # ==================================================
            # CRÉATION DE LA TRANSACTION DE CRÉDIT
            # ==================================================

            transaction = AccountTransaction.create({
                "account_id":
                    member_account.id,

                "transaction_type":
                    "credit",

                "amount":
                    self.surplus_amount,

                "transaction_date":
                    fields.Datetime.now(),

                "payment_id":
                    payment.id,

                "description":
                    _(
                        "Surplus du paiement %(payment)s "
                        "crédité au compte du membre %(member)s"
                    )
                    % {
                        "payment":
                            payment.display_name,

                        "member":
                            self.member_id.display_name,
                    },
            })

            # ==================================================
            # VALIDATION DE LA TRANSACTION
            # ==================================================

            if hasattr(
                transaction,
                "action_validate",
            ):
                transaction.action_validate()

            elif hasattr(
                transaction,
                "action_post",
            ):
                transaction.action_post()

            elif hasattr(
                transaction,
                "action_confirm",
            ):
                transaction.action_confirm()

            payment.message_post(
                body=_(
                    "Surplus de %(amount).2f %(currency)s "
                    "crédité au compte du membre %(member)s."
                )
                % {
                    "amount":
                        self.surplus_amount,

                    "currency":
                        self.currency_id.name or "",

                    "member":
                        self.member_id.display_name,
                }
            )

        # ======================================================
        # REMBOURSEMENT DU MEMBRE
        # ======================================================

        elif self.surplus_action == "refund":

            payment.message_post(
                body=_(
                    "Surplus de %(amount).2f %(currency)s "
                    "remboursé au membre %(member)s."
                )
                % {
                    "amount":
                        self.surplus_amount,

                    "currency":
                        self.currency_id.name or "",

                    "member":
                        self.member_id.display_name,
                }
            )

        else:

            raise ValidationError(
                _(
                    "Veuillez sélectionner le traitement "
                    "à appliquer au surplus."
                )
            )

        # ======================================================
        # CONFIRMATION DU PAIEMENT
        # ======================================================

        payment.with_context(
            surplus_processed=True
        ).action_confirm()

        # ======================================================
        # INVALIDATION DES COTISATIONS
        # ======================================================

        payment._invalidate_subscription_lines()

        # ======================================================
        # RETOUR
        # ======================================================

        return {
            "type": "ir.actions.act_window_close",
        }