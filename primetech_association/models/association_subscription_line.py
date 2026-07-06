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
from odoo.exceptions import UserError, ValidationError


class AssociationSubscriptionLine(models.Model):
    _name = "association.subscription.line"
    _description = "Membre participant à une cotisation"
    _order = "member_id, id"

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
        related="subscription_id.company_id",
        store=True,
        readonly=True,
        index=True,
    )

    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Devise",
        related="subscription_id.currency_id",
        store=True,
        readonly=True,
    )

    # ==========================================================
    # COTISATION
    # ==========================================================

    subscription_id = fields.Many2one(
        comodel_name="association.subscription",
        string="Cotisation",
        required=True,
        ondelete="cascade",
        index=True,
    )

    subscription_state = fields.Selection(
        related="subscription_id.state",
        string="Statut de la cotisation",
        store=True,
        readonly=True,
    )

    subscription_type = fields.Selection(
        related="subscription_id.subscription_type",
        string="Type de cotisation",
        store=True,
        readonly=True,
    )

    current_period_id = fields.Many2one(
        comodel_name="association.subscription.period",
        string="Cycle courant",
        related="subscription_id.current_period_id",
        readonly=True,
    )

    # ==========================================================
    # MEMBRE
    # ==========================================================

    member_id = fields.Many2one(
        comodel_name="association.member",
        string="Membre",
        required=True,
        ondelete="restrict",
        index=True,
    )

    member_code = fields.Char(
        related="member_id.member_code",
        string="Code membre",
        store=True,
        readonly=True,
    )

    image_128 = fields.Image(
        related="member_id.image_128",
        string="Photo du membre",
        readonly=True,
    )

    category_id = fields.Many2one(
        comodel_name="association.member.category",
        related="member_id.category_id",
        string="Catégorie",
        store=True,
        readonly=True,
    )

    function_id = fields.Many2one(
        comodel_name="association.member.function",
        related="member_id.function_id",
        string="Fonction",
        store=True,
        readonly=True,
    )

    phone = fields.Char(
        related="member_id.phone",
        string="Téléphone",
        readonly=True,
    )

    # ==========================================================
    # MONTANT DU CYCLE COURANT
    # ==========================================================

    amount_due = fields.Monetary(
        string="Montant dû",
        currency_field="currency_id",
        compute="_compute_current_cycle_payment",
    )

    amount_paid = fields.Monetary(
        string="Montant payé",
        currency_field="currency_id",
        compute="_compute_current_cycle_payment",
    )

    balance = fields.Monetary(
        string="Reste à payer",
        currency_field="currency_id",
        compute="_compute_current_cycle_payment",
    )

    payment_state = fields.Selection(
        selection=[
            ("not_paid", "Non payé"),
            ("partial", "Partiellement payé"),
            ("paid", "Payé"),
        ],
        string="État du paiement",
        compute="_compute_current_cycle_payment",
    )

    payment_date = fields.Date(
        string="Date du dernier paiement",
        compute="_compute_current_cycle_payment",
    )

    amount_received = fields.Monetary(
        string="Montant reçu",
        currency_field="currency_id",
        default=0.0,
        copy=False,
    )

    # ==========================================================
    # PAIEMENTS
    # ==========================================================

    payment_line_ids = fields.One2many(
        comodel_name="association.payment.line",
        inverse_name="subscription_line_id",
        string="Lignes de paiement",
        readonly=True,
    )

    # ==========================================================
    # COMPTE FINANCIER DU MEMBRE
    # ==========================================================

    member_account_balance = fields.Monetary(
        string="Solde compte membre",
        currency_field="currency_id",
        compute="_compute_member_account_balance",
    )

    # ==========================================================
    # NOTES
    # ==========================================================

    note = fields.Html(
        string="Notes internes",
    )

    # ==========================================================
    # CONTRAINTES SQL
    # ==========================================================

    _sql_constraints = [
        (
            "association_subscription_line_member_unique",
            "unique(subscription_id, member_id)",
            "Un membre ne peut participer qu'une seule fois "
            "à la même cotisation.",
        ),
    ]

    # ==========================================================
    # PAIEMENTS DU CYCLE COURANT
    # ==========================================================

    @api.depends(
        "subscription_id.amount",
        "subscription_id.current_period_id",
        "payment_line_ids.amount_paid",
        "payment_line_ids.payment_id.state",
        "payment_line_ids.payment_id.subscription_period_id",
        "payment_line_ids.payment_id.payment_date",
    )
    def _compute_current_cycle_payment(self):

        for record in self:

            amount_due = 0.0
            amount_paid = 0.0
            payment_date = False

            period = (
                record.subscription_id.current_period_id
            )

            if period:

                amount_due = (
                    record.subscription_id.amount or 0.0
                )

                # ==================================================
                # PAIEMENTS DU CYCLE COURANT UNIQUEMENT
                # ==================================================

                payment_lines = (
                    record.payment_line_ids.filtered(
                        lambda line: (
                            line.payment_id
                            and
                            line.payment_id.state == "confirmed"
                            and
                            line.payment_id.subscription_period_id
                            == period
                        )
                    )
                )

                amount_paid = sum(
                    payment_lines.mapped(
                        "amount_paid"
                    )
                )

                payment_dates = [
                    payment_date
                    for payment_date
                    in payment_lines.mapped(
                        "payment_id.payment_date"
                    )
                    if payment_date
                ]

                payment_date = (
                    max(payment_dates)
                    if payment_dates
                    else False
                )

            # ======================================================
            # SOLDE
            # ======================================================

            balance = max(
                amount_due - amount_paid,
                0.0,
            )

            record.amount_due = amount_due
            record.amount_paid = amount_paid
            record.balance = balance
            record.payment_date = payment_date

            # ======================================================
            # ÉTAT
            # ======================================================

            if amount_paid <= 0:

                record.payment_state = "not_paid"

            elif amount_paid < amount_due:

                record.payment_state = "partial"

            else:

                record.payment_state = "paid"
   
    # ==========================================================
    # SOLDE DU COMPTE MEMBRE
    # ==========================================================

    @api.depends("member_id", "company_id")
    def _compute_member_account_balance(self):
        Account = self.env[
            "association.member.account"
        ]

        for record in self:
            record.member_account_balance = 0.0

            if not record.member_id:
                continue

            account = Account.search(
                [
                    (
                        "member_id",
                        "=",
                        record.member_id.id,
                    ),
                    (
                        "company_id",
                        "=",
                        record.company_id.id,
                    ),
                ],
                limit=1,
            )

            if account:
                record.member_account_balance = (
                    account.balance or 0.0
                )

    # ==========================================================
    # CONTRÔLE DU CYCLE DE PAIEMENT
    # ==========================================================

    def _check_payment_cycle(self):
        self.ensure_one()

        subscription = self.subscription_id

        if not subscription:
            raise UserError(
                _(
                    "Aucune cotisation n'est associée "
                    "à cette ligne."
                )
            )

        # ======================================================
        # RECHERCHE DIRECTE DU CYCLE EN COURS
        #
        # IMPORTANT :
        # Ne pas dépendre uniquement de current_period_id.
        # On recherche directement dans la base.
        # ======================================================

        period = self.env[
            "association.subscription.period"
        ].search(
            [
                (
                    "subscription_id",
                    "=",
                    subscription.id,
                ),
                (
                    "state",
                    "=",
                    "running",
                ),
            ],
            order="sequence desc, id desc",
            limit=1,
        )

        if not period:
            raise UserError(
                _(
                    "Aucun cycle de cotisation en cours "
                    "n'a été trouvé pour %(subscription)s."
                )
                % {
                    "subscription":
                        subscription.display_name,
                }
            )

        # ======================================================
        # CONTRÔLE DU PAIEMENT DU MEMBRE
        # ======================================================

        if self.payment_state == "paid":
            raise ValidationError(
                _(
                    "Le membre %(member)s a déjà réglé "
                    "sa cotisation pour le cycle %(cycle)s."
                )
                % {
                    "member":
                        self.member_id.display_name,

                    "cycle":
                        period.display_name,
                }
            )

        if self.balance <= 0:
            raise ValidationError(
                _(
                    "Cette cotisation ne présente "
                    "aucun reste à payer."
                )
            )

        return period
    # ==========================================================
    # CRÉER UN PAIEMENT DE COTISATION
    # ==========================================================

    def _create_subscription_payment(
        self,
        amount_received,
        payment_method="cash",
        payment_reference=False,
    ):
        self.ensure_one()

        # ======================================================
        # CONTRÔLES
        # ======================================================

        if not self.member_id:
            raise ValidationError(
                _(
                    "Aucun membre n'est associé "
                    "à cette cotisation."
                )
            )

        if not self.subscription_id:
            raise ValidationError(
                _(
                    "Aucune cotisation n'est associée "
                    "à cette ligne."
                )
            )

        if amount_received <= 0:
            raise ValidationError(
                _(
                    "Le montant reçu doit être "
                    "strictement supérieur à zéro."
                )
            )

        # ======================================================
        # CYCLE COURANT
        # ======================================================

        period = self._check_payment_cycle()

        # ======================================================
        # RESTE À PAYER DU CYCLE COURANT
        # ======================================================

        current_balance = max(
            self.balance or 0.0,
            0.0,
        )

        if current_balance <= 0:
            raise ValidationError(
                _(
                    "La cotisation du membre %(member)s "
                    "est déjà entièrement payée pour "
                    "le cycle %(cycle)s."
                )
                % {
                    "member":
                        self.member_id.display_name,

                    "cycle":
                        period.display_name,
                }
            )

        # ======================================================
        # MONTANT À AFFECTER
        # ======================================================

        amount_to_allocate = min(
            amount_received,
            current_balance,
        )

        # ======================================================
        # CRÉATION DU PAIEMENT
        # ======================================================

        payment = self.env[
            "association.payment"
        ].create({
            "member_id":
                self.member_id.id,

            "subscription_period_id":
                period.id,

            "payment_date":
                fields.Date.context_today(self),

            "amount":
                amount_received,

            "payment_method":
                payment_method,

            "payment_reference":
                payment_reference
                or _(
                    "Encaissement %(subscription)s - %(cycle)s"
                )
                % {
                    "subscription":
                        self.subscription_id.display_name,

                    "cycle":
                        period.display_name,
                },

            "company_id":
                self.company_id.id,
        })

        # ======================================================
        # AFFECTATION
        # ======================================================

        self.env[
            "association.payment.line"
        ].create({
            "payment_id":
                payment.id,

            "subscription_line_id":
                self.id,

            "amount_paid":
                amount_to_allocate,
        })

        # ======================================================
        # CONFIRMATION
        # ======================================================

        action = payment.action_confirm()

        return {
            "type": "payment",
            "payment": payment,
            "action": action,
        }
    # ==========================================================
    # ACTION - ENCAISSER
    # ==========================================================

    def action_create_payment(self):
        self.ensure_one()

        amount_received = (
            self.amount_received or 0.0
        )

        if amount_received <= 0:
            raise ValidationError(
                _(
                    "Veuillez saisir un montant reçu "
                    "supérieur à zéro."
                )
            )

        result = self._create_subscription_payment(
            amount_received=amount_received,
            payment_method="cash",
            payment_reference=_(
                "Encaissement cotisation %(subscription)s"
            )
            % {
                "subscription":
                    self.subscription_id.display_name,
            },
        )

        action = result.get("action")

        # ======================================================
        # ACTION RETOURNÉE PAR LE PAIEMENT
        # ======================================================

        if isinstance(action, dict):
            return action

        # ======================================================
        # PAIEMENT CONFIRMÉ
        # ======================================================

        self.amount_received = 0.0

        self.invalidate_recordset([
            "amount_paid",
            "balance",
            "payment_state",
            "payment_date",
        ])

        self.modified([
            "amount_paid",
            "balance",
            "payment_state",
            "payment_date",
        ])

        return False
    # ==========================================================
    # PAYER DEPUIS LE COMPTE MEMBRE
    # ==========================================================

    def action_pay_from_member_account(self):
        self.ensure_one()

        self._check_payment_cycle()

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
                    self.company_id.id,
                ),
            ],
            limit=1,
        )

        if not member_account:
            raise ValidationError(
                _(
                    "Le membre %(member)s ne possède pas "
                    "de compte financier."
                )
                % {
                    "member": self.member_id.display_name,
                }
            )

        available_balance = (
            member_account.balance or 0.0
        )

        if available_balance < self.balance:
            raise ValidationError(
                _(
                    "Solde du compte membre insuffisant.\n\n"
                    "Disponible : %(available).2f %(currency)s\n"
                    "Montant requis : %(required).2f %(currency)s."
                )
                % {
                    "available": available_balance,
                    "required": self.balance,
                    "currency": self.currency_id.name or "",
                }
            )

        amount_to_pay = self.balance

        result = self._create_subscription_payment(
            amount_received=amount_to_pay,
            payment_method="bank",
            payment_reference=_(
                "Paiement depuis le compte du membre"
            ),
        )

        if result["type"] == "surplus":
            raise ValidationError(
                _(
                    "Un paiement depuis le compte membre "
                    "ne peut pas générer de surplus."
                )
            )

        payment = result["payment"]

        transaction = AccountTransaction.create({
            "account_id": member_account.id,
            "transaction_type": "debit",
            "amount": amount_to_pay,
            "transaction_date": fields.Datetime.now(),
            "payment_id": payment.id,
            "description": _(
                "Paiement du cycle %(cycle)s - %(subscription)s"
            )
            % {
                "cycle":
                    self.subscription_id.current_period_id.display_name,
                "subscription":
                    self.subscription_id.display_name,
            },
        })

        if hasattr(transaction, "action_validate"):
            transaction.action_validate()

        elif hasattr(transaction, "action_post"):
            transaction.action_post()

        elif hasattr(transaction, "action_confirm"):
            transaction.action_confirm()

        return False

    # ==========================================================
    # CREATE
    # ==========================================================

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)

        return records

    # ==========================================================
    # CONTRAINTES
    # ==========================================================

    @api.constrains(
        "member_id",
        "subscription_id",
    )
    def _check_member_company(self):
        for record in self:
            if not (
                record.member_id
                and record.subscription_id
            ):
                continue

            if (
                record.member_id.company_id
                != record.subscription_id.company_id
            ):
                raise ValidationError(
                    _(
                        "Le membre et la cotisation doivent "
                        "appartenir à la même filiale."
                    )
                )
