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


class AssociationPayment(models.Model):
    _name = "association.payment"
    _description = "Paiement d'association"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "payment_date desc, id desc"
    _rec_name = "name"

    # ==========================================================
    # TECHNIQUE
    # ==========================================================

    active = fields.Boolean(
        string="Actif",
        default=True,
        tracking=True,
    )

    sequence = fields.Integer(
        string="Séquence",
        default=10,
    )

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Filiale",
        required=True,
        default=lambda self: self.env.company,
        index=True,
        tracking=True,
    )

    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Devise",
        related="company_id.currency_id",
        readonly=True,
        store=True,
    )

    color = fields.Integer(
        string="Couleur",
    )

    # ==========================================================
    # IDENTIFICATION
    # ==========================================================

    name = fields.Char(
        string="Référence du paiement",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _("Nouveau"),
        tracking=True,
        index=True,
    )

    description = fields.Text(
        string="Description",
    )

    # ==========================================================
    # MEMBRE
    # ==========================================================

    member_id = fields.Many2one(
        comodel_name="association.member",
        string="Membre",
        required=True,
        tracking=True,
        ondelete="restrict",
        index=True,
    )

    member_code = fields.Char(
        related="member_id.member_code",
        string="Code membre",
        readonly=True,
        store=True,
    )

    member_image_128 = fields.Image(
        related="member_id.image_128",
        string="Photo du membre",
        readonly=True,
    )

    category_id = fields.Many2one(
        related="member_id.category_id",
        string="Catégorie",
        readonly=True,
        store=True,
    )

    function_id = fields.Many2one(
        related="member_id.function_id",
        string="Fonction",
        readonly=True,
        store=True,
    )

    # ==========================================================
    # PAIEMENT
    # ==========================================================

    payment_date = fields.Date(
        string="Date de paiement",
        default=fields.Date.context_today,
        required=True,
        tracking=True,
        index=True,
    )

    amount = fields.Monetary(
        string="Montant du paiement",
        currency_field="currency_id",
        required=True,
        default=0.0,
        tracking=True,
    )

    allocated_amount = fields.Monetary(
        string="Montant affecté",
        currency_field="currency_id",
        compute="_compute_payment_totals",
    )

    remaining_amount = fields.Monetary(
        string="Montant non affecté",
        currency_field="currency_id",
        compute="_compute_payment_totals",
    )

    payment_method = fields.Selection(
        selection=[
            ("cash", "Espèces"),
            ("bank", "Virement bancaire"),
            ("cheque", "Chèque"),
            ("mobile_money", "Mobile Money"),
            ("other", "Autre"),
        ],
        string="Mode de paiement",
        required=True,
        default="cash",
        tracking=True,
        index=True,
    )

    payment_reference = fields.Char(
        string="Référence externe",
        tracking=True,
        help=(
            "Référence Mobile Money, numéro de chèque, "
            "référence bancaire ou autre référence externe."
        ),
    )

    state = fields.Selection(
        selection=[
            ("draft", "Brouillon"),
            ("confirmed", "Confirmé"),
            ("cancelled", "Annulé"),
        ],
        string="Statut",
        default="draft",
        required=True,
        tracking=True,
        index=True,
    )

    # ==========================================================
    # LIGNES DE PAIEMENT
    # ==========================================================

    line_ids = fields.One2many(
        comodel_name="association.payment.line",
        inverse_name="payment_id",
        string="Affectations du paiement",
        copy=True,
    )

    line_count = fields.Integer(
        string="Nombre de lignes",
        compute="_compute_payment_totals",
    )


    # ==========================================================
    # CYCLE DE COTISATION
    # ==========================================================

    subscription_period_id = fields.Many2one(
        comodel_name="association.subscription.period",
        string="Cycle de cotisation",
        ondelete="restrict",
        readonly=True,
        copy=False,
        index=True,
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
            "association_payment_name_company_unique",
            "unique(name, company_id)",
            "La référence du paiement doit être unique par filiale.",
        ),
        (
            "association_payment_amount_positive",
            "CHECK(amount >= 0)",
            "Le montant du paiement ne peut pas être négatif.",
        ),
    ]

    # ==========================================================
    # CALCUL DES TOTAUX
    # ==========================================================

    @api.depends(
        "amount",
        "line_ids",
        "line_ids.amount_paid",
    )
    def _compute_payment_totals(self):
        for record in self:
            allocated_amount = sum(
                record.line_ids.mapped("amount_paid")
            )

            record.line_count = len(record.line_ids)
            record.allocated_amount = allocated_amount
            record.remaining_amount = (
                record.amount - allocated_amount
            )

    # ==========================================================
    # INVALIDATION DES COTISATIONS ET CYCLES
    # ==========================================================

    def _invalidate_subscription_lines(self):

        # ======================================================
        # LIGNES DE COTISATION
        # ======================================================

        subscription_lines = self.line_ids.mapped(
            "subscription_line_id"
        )

        if subscription_lines:

            subscription_lines.invalidate_recordset([
                "amount_paid",
                "balance",
                "payment_state",
                "payment_date",
            ])

            subscription_lines.modified([
                "amount_paid",
                "balance",
                "payment_state",
                "payment_date",
            ])

        # ======================================================
        # CYCLES DE COTISATION CONCERNÉS
        # ======================================================

        periods = self.env[
            "association.subscription.period"
        ]

        subscriptions = subscription_lines.mapped(
            "subscription_id"
        )

        if subscriptions:

            periods = self.env[
                "association.subscription.period"
            ].search([
                (
                    "subscription_id",
                    "in",
                    subscriptions.ids,
                ),
                (
                    "state",
                    "=",
                    "running",
                ),
            ])

        # ======================================================
        # INVALIDATION DES STATISTIQUES DE CAGNOTTE
        # ======================================================

        if periods:

            period_fields = [
                field_name
                for field_name in (
                    "collected_amount",
                    "allocated_amount",
                    "available_amount",
                    "member_count",
                    "paid_member_count",
                    "partial_member_count",
                    "unpaid_member_count",
                    "recovery_rate",
                    "beneficiary_count",
                )
                if field_name in periods._fields
            ]

            if period_fields:

                periods.invalidate_recordset(
                    period_fields
                )

                periods.modified(
                    period_fields
                )

        return True
    # ==========================================================
    # CREATE
    # ==========================================================

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("Nouveau")) == _("Nouveau"):
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code(
                        "association.payment"
                    )
                    or _("Nouveau")
                )

        return super().create(vals_list)

    # ==========================================================
    # ONCHANGE MEMBRE
    # ==========================================================

    @api.onchange("member_id")
    def _onchange_member_id(self):
        for record in self:
            if record.member_id:
                record.company_id = record.member_id.company_id

            record.line_ids = [(5, 0, 0)]


    # ==========================================================
    # ONCHANGE
    # ==========================================================

    @api.onchange(
        "line_ids",
        "line_ids.amount_paid",
    )
    def _onchange_line_ids(self):

        # Le montant du paiement représente
        # le montant réellement reçu du membre.
        #
        # Il ne doit jamais être remplacé automatiquement
        # par le montant affecté aux cotisations.

        return

    # ==========================================================
    # CONTRAINTES MÉTIER
    # ==========================================================

    @api.constrains("member_id", "company_id")
    def _check_member_company(self):
        for record in self:
            if (
                record.member_id
                and record.company_id
                and record.member_id.company_id
                != record.company_id
            ):
                raise ValidationError(
                    _(
                        "Le membre et le paiement doivent appartenir "
                        "à la même filiale."
                    )
                )

    @api.constrains(
        "amount",
        "line_ids",
        "line_ids.amount_paid",
    )
    def _check_allocated_amount(self):
        for record in self:
            allocated_amount = sum(
                record.line_ids.mapped("amount_paid")
            )

            if allocated_amount > record.amount:
                raise ValidationError(
                    _(
                        "Le montant total affecté (%(allocated)s) "
                        "ne peut pas dépasser le montant du paiement "
                        "(%(amount)s)."
                    )
                    % {
                        "allocated": allocated_amount,
                        "amount": record.amount,
                    }
                )

    # ==========================================================
    # ACTION - GÉNÉRER LES COTISATIONS
    # ==========================================================

    def action_generate_subscription_lines(self):
        SubscriptionLine = self.env[
            "association.subscription.line"
        ]

        for record in self:
            if record.state != "draft":
                raise UserError(
                    _(
                        "Les cotisations peuvent uniquement être "
                        "chargées sur un paiement en brouillon."
                    )
                )

            if not record.member_id:
                raise UserError(
                    _("Veuillez sélectionner un membre.")
                )

            existing_subscription_line_ids = set(
                record.line_ids.mapped(
                    "subscription_line_id"
                ).ids
            )

            subscription_lines = SubscriptionLine.search(
                [
                    (
                        "member_id",
                        "=",
                        record.member_id.id,
                    ),
                    (
                        "subscription_id.company_id",
                        "=",
                        record.company_id.id,
                    ),
                    (
                        "subscription_id.state",
                        "in",
                        ["confirmed", "running"],
                    ),
                    (
                        "balance",
                        ">",
                        0,
                    ),
                ],
                order="due_date asc, id asc",
            )

            new_lines = []

            for subscription_line in subscription_lines:
                if (
                    subscription_line.id
                    not in existing_subscription_line_ids
                ):
                    new_lines.append(
                        (
                            0,
                            0,
                            {
                                "subscription_line_id":
                                    subscription_line.id,
                                "amount_paid": 0.0,
                            },
                        )
                    )

            if not new_lines:
                raise UserError(
                    _(
                        "Aucune cotisation impayée ou partiellement "
                        "payée n'a été trouvée pour ce membre."
                    )
                )

            record.write({
                "line_ids": new_lines,
            })

            record.message_post(
                body=_(
                    "%s cotisation(s) chargée(s) pour le membre."
                )
                % len(new_lines)
            )

        return True

    # ==========================================================
    # ACTION - RÉPARTITION AUTOMATIQUE
    # ==========================================================

    def action_auto_allocate(self):
        for record in self:
            if record.state != "draft":
                raise UserError(
                    _(
                        "La répartition automatique est uniquement "
                        "possible sur un paiement en brouillon."
                    )
                )

            if record.amount <= 0:
                raise UserError(
                    _(
                        "Le montant du paiement doit être supérieur "
                        "à zéro."
                    )
                )

            if not record.line_ids:
                raise UserError(
                    _(
                        "Chargez d'abord les cotisations du membre."
                    )
                )

            remaining_amount = record.amount

            lines = record.line_ids.sorted(
                key=lambda line: (
                    (
                        line.subscription_line_id.current_period_id.due_date
                        if line.subscription_line_id.current_period_id
                        else fields.Date.today()
                    ),
                    line.id or 0,
                )
            )

            for line in lines:
                balance_to_pay = max(
                    line.balance_before_payment or 0.0,
                    0.0,
                )

                amount_to_allocate = min(
                    remaining_amount,
                    balance_to_pay,
                )

                line.amount_paid = amount_to_allocate

                remaining_amount -= amount_to_allocate

                if remaining_amount <= 0:
                    remaining_amount = 0.0

            record.message_post(
                body=_(
                    "Le montant du paiement a été réparti "
                    "automatiquement sur les cotisations."
                )
            )

        return True

    # ==========================================================
    # ACTION - CONFIRMER
    # ==========================================================

    def action_confirm(self):

        for record in self:

            # ======================================================
            # CONTRÔLE DE L'ÉTAT
            # ======================================================

            if record.state != "draft":

                raise UserError(
                    _(
                        "Seul un paiement en brouillon "
                        "peut être confirmé."
                    )
                )

            # ======================================================
            # CONTRÔLE DU MONTANT
            # ======================================================

            if record.amount <= 0:

                raise ValidationError(
                    _(
                        "Le montant du paiement doit être "
                        "strictement supérieur à zéro."
                    )
                )

            # ======================================================
            # CONTRÔLE DES AFFECTATIONS
            # ======================================================

            if not record.line_ids:

                raise ValidationError(
                    _(
                        "Le paiement doit être affecté "
                        "à au moins une cotisation."
                    )
                )

            # ======================================================
            # CONTRÔLE DU CYCLE
            # ======================================================

            period = record.subscription_period_id

            if not period:

                raise ValidationError(
                    _(
                        "Aucun cycle de cotisation n'est "
                        "associé au paiement."
                    )
                )

            if period.state != "running":

                raise ValidationError(
                    _(
                        "Le cycle %(cycle)s n'est pas en cours."
                    )
                    % {
                        "cycle":
                            period.display_name,
                    }
                )

            # ======================================================
            # MONTANT REÇU
            # ======================================================

            received_amount = (
                record.amount or 0.0
            )

            total_allocated = 0.0

            # ======================================================
            # CALCUL DU MONTANT RÉELLEMENT DÛ
            # ======================================================

            for line in record.line_ids:

                subscription_line = (
                    line.subscription_line_id
                )

                # ==================================================
                # CONTRÔLE DE LA LIGNE DE COTISATION
                # ==================================================

                if not subscription_line:

                    raise ValidationError(
                        _(
                            "Une ligne de paiement n'est "
                            "affectée à aucune cotisation."
                        )
                    )

                # ==================================================
                # CONTRÔLE DE LA COTISATION
                # ==================================================

                if not subscription_line.subscription_id:

                    raise ValidationError(
                        _(
                            "Aucune cotisation n'est associée "
                            "à la ligne du membre %(member)s."
                        )
                        % {
                            "member":
                                subscription_line.member_id.display_name,
                        }
                    )

                # ==================================================
                # CONTRÔLE DU CYCLE DE LA COTISATION
                # ==================================================

                current_period = (
                    subscription_line
                    .subscription_id
                    .current_period_id
                )

                if not current_period:

                    raise ValidationError(
                        _(
                            "Aucun cycle courant n'est ouvert "
                            "pour la cotisation %(subscription)s."
                        )
                        % {
                            "subscription":
                                subscription_line
                                .subscription_id
                                .display_name,
                        }
                    )

                if current_period != period:

                    raise ValidationError(
                        _(
                            "Le paiement est associé au cycle "
                            "%(payment_cycle)s alors que la cotisation "
                            "du membre %(member)s utilise actuellement "
                            "le cycle %(current_cycle)s."
                        )
                        % {
                            "payment_cycle":
                                period.display_name,

                            "member":
                                subscription_line
                                .member_id
                                .display_name,

                            "current_cycle":
                                current_period.display_name,
                        }
                    )

                # ==================================================
                # AUTRES PAIEMENTS CONFIRMÉS DU MÊME CYCLE
                # ==================================================

                other_payment_lines = (
                    subscription_line
                    .payment_line_ids
                    .filtered(
                        lambda payment_line: (
                            payment_line.payment_id
                            and
                            payment_line.payment_id.state
                            == "confirmed"
                            and
                            payment_line.payment_id.id
                            != record.id
                            and
                            payment_line
                            .payment_id
                            .subscription_period_id
                            == period
                        )
                    )
                )

                # ==================================================
                # MONTANT DÉJÀ PAYÉ SUR LE CYCLE
                # ==================================================

                already_paid = sum(
                    other_payment_lines.mapped(
                        "amount_paid"
                    )
                )

                # ==================================================
                # MONTANT DÛ
                # ==================================================

                amount_due = (
                    subscription_line.amount_due
                    or 0.0
                )

                # ==================================================
                # RESTE À PAYER DU CYCLE
                # ==================================================

                remaining_amount = max(
                    amount_due - already_paid,
                    0.0,
                )

                # ==================================================
                # MONTANT DEMANDÉ SUR LA LIGNE
                # ==================================================

                requested_amount = max(
                    line.amount_paid or 0.0,
                    0.0,
                )

                # ==================================================
                # MONTANT RÉELLEMENT AFFECTABLE
                # ==================================================

                allocated_amount = min(
                    requested_amount,
                    remaining_amount,
                )

                # ==================================================
                # MISE À JOUR DE L'AFFECTATION
                # ==================================================

                if line.amount_paid != allocated_amount:

                    line.amount_paid = allocated_amount

                total_allocated += allocated_amount

            # ======================================================
            # CALCUL DU SURPLUS
            # ======================================================

            surplus_amount = max(
                received_amount - total_allocated,
                0.0,
            )

            # ======================================================
            # OUVERTURE DE L'ASSISTANT DE SURPLUS
            # ======================================================

            if (
                surplus_amount > 0
                and not self.env.context.get(
                    "surplus_processed"
                )
            ):

                wizard = self.env[
                    "association.payment.surplus.wizard"
                ].create({
                    "payment_id":
                        record.id,

                    "member_id":
                        record.member_id.id,

                    "received_amount":
                        received_amount,

                    "allocated_amount":
                        total_allocated,

                    "surplus_amount":
                        surplus_amount,
                })

                return {
                    "type":
                        "ir.actions.act_window",

                    "name":
                        _("Gestion du surplus"),

                    "res_model":
                        "association.payment.surplus.wizard",

                    "res_id":
                        wizard.id,

                    "view_mode":
                        "form",

                    "target":
                        "new",
                }

            # ======================================================
            # CONTRÔLE FINAL DE L'AFFECTATION
            # ======================================================

            if total_allocated <= 0:

                raise ValidationError(
                    _(
                        "Aucun montant n'a pu être affecté "
                        "au cycle %(cycle)s."
                    )
                    % {
                        "cycle":
                            period.display_name,
                    }
                )

            # ======================================================
            # CONFIRMATION DU PAIEMENT
            # ======================================================

            record.write({
                "state": "confirmed",
            })

            # ======================================================
            # INVALIDATION DES LIGNES DE COTISATION
            # ======================================================

            record._invalidate_subscription_lines()

            # ======================================================
            # MESSAGE DE SUIVI
            # ======================================================

            record.message_post(
                body=_(
                    "Le paiement a été confirmé.<br/>"
                    "Cycle : %(cycle)s<br/>"
                    "Montant reçu : %(received).2f %(currency)s<br/>"
                    "Montant affecté : %(allocated).2f %(currency)s"
                )
                % {
                    "cycle":
                        period.display_name,

                    "received":
                        received_amount,

                    "allocated":
                        total_allocated,

                    "currency":
                        record.currency_id.name or "",
                }
            )

        return True

    # ==========================================================
    # ACTION - ANNULER
    # ==========================================================

    def action_cancel(self):
        for record in self:
            if record.state == "cancelled":
                continue

            record.write({
                "state": "cancelled",
            })

            record._invalidate_subscription_lines()

            record.message_post(
                body=_(
                    "Le paiement a été annulé."
                )
            )

        return True

    # ==========================================================
    # ACTION - REMETTRE EN BROUILLON
    # ==========================================================

    def action_reset_draft(self):
        for record in self:
            if record.state != "cancelled":
                raise UserError(
                    _(
                        "Seul un paiement annulé peut être "
                        "remis en brouillon."
                    )
                )

            record.write({
                "state": "draft",
            })

            record._invalidate_subscription_lines()

            record.message_post(
                body=_(
                    "Le paiement a été remis en brouillon."
                )
            )

        return True

    # ==========================================================
    # CONTRÔLE DU MONTANT
    # ==========================================================

    @api.constrains("amount")
    def _check_amount(self):
        for record in self:
            if record.amount < 0:
                raise ValidationError(
                    _(
                        "Le montant du paiement ne peut pas "
                        "être négatif."
                    )
                )

    # ==========================================================
    # WRITE
    # ==========================================================

    def write(self, vals):
        protected_fields = {
            "member_id",
            "company_id",
            "payment_date",
            "amount",
            "payment_method",
            "payment_reference",
            "line_ids",
        }

        if protected_fields.intersection(vals):
            confirmed_records = self.filtered(
                lambda record: record.state == "confirmed"
            )

            if confirmed_records:
                raise UserError(
                    _(
                        "Un paiement confirmé ne peut plus "
                        "être modifié."
                    )
                )

        return super().write(vals)
    
    # ==========================================================
    # ACTION - VOIR LES AFFECTATIONS
    # ==========================================================

    def action_view_payment_lines(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": _("Affectations du paiement"),
            "res_model": "association.payment.line",
            "view_mode": "list,form",
            "domain": [
                (
                    "payment_id",
                    "=",
                    self.id,
                ),
            ],
            "context": {
                "default_payment_id": self.id,
                "create": self.state == "draft",
            },
        }