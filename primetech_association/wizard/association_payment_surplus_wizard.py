# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


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
    )

    member_id = fields.Many2one(
        comodel_name="association.member",
        string="Membre",
        related="payment_id.member_id",
        readonly=True,
    )

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Filiale",
        related="payment_id.company_id",
        readonly=True,
    )

    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Devise",
        related="payment_id.currency_id",
        readonly=True,
    )

    # ==========================================================
    # MONTANTS
    # ==========================================================

    payment_amount = fields.Monetary(
        string="Montant reçu",
        currency_field="currency_id",
        related="payment_id.amount",
        readonly=True,
    )

    allocated_amount = fields.Monetary(
        string="Montant affecté aux cotisations",
        currency_field="currency_id",
        related="payment_id.allocated_amount",
        readonly=True,
    )

    surplus_amount = fields.Monetary(
        string="Surplus disponible",
        currency_field="currency_id",
        compute="_compute_surplus_amount",
        readonly=True,
    )

    # ==========================================================
    # TRAITEMENT
    # ==========================================================

    surplus_action = fields.Selection(
        selection=[
            (
                "member_account",
                "Approvisionner le compte du membre",
            ),
            (
                "refund",
                "Rembourser le membre",
            ),
        ],
        string="Traitement du surplus",
        required=True,
        default="member_account",
    )

    note = fields.Text(
        string="Observation",
    )

    # ==========================================================
    # CALCUL DU SURPLUS
    # ==========================================================

    @api.depends(
        "payment_id.amount",
        "payment_id.allocated_amount",
    )
    def _compute_surplus_amount(self):

        for record in self:

            if not record.payment_id:

                record.surplus_amount = 0.0

                continue

            record.surplus_amount = max(
                (
                    record.payment_id.amount
                    - record.payment_id.allocated_amount
                ),
                0.0,
            )

    # ==========================================================
    # TRAITER
    # ==========================================================

    def action_process_surplus(self):

        self.ensure_one()

        if not self.payment_id:

            raise UserError(
                _("Aucun paiement n'est défini.")
            )

        if not self.member_id:

            raise UserError(
                _("Aucun membre n'est défini.")
            )

        surplus_amount = self.surplus_amount or 0.0

        if surplus_amount <= 0:

            raise ValidationError(
                _(
                    "Ce paiement ne présente aucun surplus "
                    "à traiter."
                )
            )

        # ======================================================
        # APPROVISIONNEMENT DU COMPTE MEMBRE
        # ======================================================

        if self.surplus_action == "member_account":

            return self._credit_member_account(
                surplus_amount
            )

        # ======================================================
        # REMBOURSEMENT
        # ======================================================

        if self.surplus_action == "refund":

            return self._refund_member(
                surplus_amount
            )

        raise ValidationError(
            _(
                "Veuillez sélectionner le traitement "
                "du surplus."
            )
        )

    # ==========================================================
    # CRÉDITER LE COMPTE MEMBRE
    # ==========================================================

    def _credit_member_account(self, amount):

        self.ensure_one()

        MemberAccount = self.env[
            "association.member.account"
        ]

        AccountTransaction = self.env[
            "association.member.account.transaction"
        ]

        # ======================================================
        # CONTRÔLES
        # ======================================================

        if amount <= 0:

            raise ValidationError(
                _(
                    "Le montant à créditer doit être "
                    "strictement supérieur à zéro."
                )
            )

        if not self.member_id:

            raise ValidationError(
                _("Aucun membre n'est défini.")
            )

        if not self.company_id:

            raise ValidationError(
                _("Aucune filiale n'est définie.")
            )

        # ======================================================
        # CONTRÔLE DU DOUBLE CRÉDIT
        # ======================================================

        existing_transaction = AccountTransaction.search(
            [
                (
                    "payment_id",
                    "=",
                    self.payment_id.id,
                ),
            ],
            limit=1,
        )

        if existing_transaction:

            raise ValidationError(
                _(
                    "Le surplus de ce paiement a déjà été "
                    "affecté au compte du membre."
                )
            )

        # ======================================================
        # RECHERCHE DU COMPTE MEMBRE
        # ======================================================

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
                    self.company_id.id,
                ),
            ],
            limit=1,
        )

        # ======================================================
        # CRÉATION AUTOMATIQUE DU COMPTE
        # ======================================================

        if not member_account:

            member_account = MemberAccount.create(
                {
                    "member_id":
                        self.member_id.id,

                    "company_id":
                        self.company_id.id,
                }
            )

        # ======================================================
        # VALEURS DU MOUVEMENT
        # ======================================================

        transaction_values = {
            "account_id":
                member_account.id,

            "transaction_type":
                "credit",

            "amount":
                amount,

            "transaction_date":
                fields.Datetime.now(),

            "payment_id":
                self.payment_id.id,

            "description":
                _(
                    "Surplus du paiement %(payment)s"
                )
                % {
                    "payment":
                        self.payment_id.display_name,
                },
        }

        # ======================================================
        # CRÉATION DU MOUVEMENT
        # ======================================================

        transaction = AccountTransaction.create(
            transaction_values
        )

        # ======================================================
        # VALIDATION DU MOUVEMENT
        #
        # IMPORTANT :
        # ON UTILISE UNIQUEMENT UNE ACTION MÉTIER EXISTANTE.
        # ON N'INVENTE AUCUNE VALEUR DE STATE.
        # ======================================================

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

        # ======================================================
        # MESSAGE SUR LE PAIEMENT
        # ======================================================

        self.payment_id.message_post(
            body=_(
                "Le surplus de %(amount).2f %(currency)s "
                "a été crédité sur le compte du membre "
                "%(member)s."
            )
            % {
                "amount":
                    amount,

                "currency":
                    self.currency_id.name or "",

                "member":
                    self.member_id.display_name,
            }
        )

        # ======================================================
        # FINALISATION DU PAIEMENT
        # ======================================================

        if self.payment_id.state == "draft":

            self.payment_id.write(
                {
                    "state":
                        "confirmed",
                }
            )

            self.payment_id._invalidate_subscription_lines()

            self.payment_id.message_post(
                body=_(
                    "Encaissement confirmé après "
                    "affectation du surplus au compte membre."
                )
            )

        # ======================================================
        # OUVERTURE DU COMPTE MEMBRE
        # ======================================================

        return {
            "type":
                "ir.actions.act_window",

            "name":
                _("Compte membre"),

            "res_model":
                "association.member.account",

            "res_id":
                member_account.id,

            "view_mode":
                "form",

            "target":
                "current",
        }
    
    # ==========================================================
    # REMBOURSER LE MEMBRE
    # ==========================================================

    def _refund_member(self, amount):

        self.ensure_one()

        self.payment_id.message_post(
            body=_(
                "Le surplus de %(amount).2f %(currency)s "
                "doit être remboursé au membre %(member)s."
            )
            % {
                "amount":
                    amount,

                "currency":
                    self.currency_id.name or "",

                "member":
                    self.member_id.display_name,
            }
        )

        if self.payment_id.state == "draft":

            self.payment_id.write(
                {
                    "state":
                        "confirmed",
                }
            )

            self.payment_id._invalidate_subscription_lines()

            self.payment_id.message_post(
                body=_(
                    "Encaissement confirmé après "
                    "traitement du surplus par remboursement."
                )
            )

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title":
                    _("Remboursement enregistré"),

                "message":
                    _(
                        "Le surplus de %(amount).2f "
                        "%(currency)s est marqué "
                        "comme remboursé."
                    )
                    % {
                        "amount":
                            amount,

                        "currency":
                            self.currency_id.name or "",
                    },

                "type":
                    "success",

                "sticky":
                    False,

                "next": {
                    "type":
                        "ir.actions.act_window_close",
                },
            },
        }
