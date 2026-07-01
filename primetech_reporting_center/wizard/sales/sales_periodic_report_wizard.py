# -*- coding: utf-8 -*-

from datetime import datetime

from odoo import fields, models


class SalesPeriodicReportWizard(models.TransientModel):
    _name = "primetech.sales.periodic.report.wizard"
    _description = "Rapport Périodique des Ventes"

    date_from = fields.Date(
        string="Date début",
        required=True,
        default=fields.Date.context_today,
    )

    date_to = fields.Date(
        string="Date fin",
        required=True,
        default=fields.Date.context_today,
    )

    company_id = fields.Many2one(
        "res.company",
        string="Société",
        required=True,
        default=lambda self: self.env.company,
    )

    user_id = fields.Many2one(
        "res.users",
        string="Commercial",
    )

    partner_id = fields.Many2one(
        "res.partner",
        string="Client",
    )

    state_filter = fields.Selection(
        [
            ("all", "Toutes les ventes"),
            ("sale", "Commandes confirmées"),
            ("invoiced", "Facturées"),
        ],
        string="État",
        default="all",
    )

    # =====================================================
    # CONTEXTE COMMUN PDF / PREVIEW
    # =====================================================

    def _get_render_context(self):

        self.ensure_one()

        generated_at = datetime.now()

        report_data = self.env[
            "primetech.sales.periodic.report"
        ].get_report_data(

            date_from=self.date_from,

            date_to=self.date_to,

            company_id=self.company_id.id,

            user_id=(
                self.user_id.id
                if self.user_id
                else False
            ),

            partner_id=(
                self.partner_id.id
                if self.partner_id
                else False
            ),

            state_filter=self.state_filter,

        )

        return {

            # -------------------------------------
            # Odoo
            # -------------------------------------

            "doc_ids":
                self.ids,

            "doc_model":
                "primetech.sales.periodic.report.wizard",

            "docs":
                self,

            # -------------------------------------
            # Wizard
            # -------------------------------------

            "wizard":
                self,

            # -------------------------------------
            # Société
            # -------------------------------------

            "company":
                self.company_id,

            "company_name":
                self.company_id.name,

            "company_logo":
                self.company_id.logo,

            "currency":
                self.company_id.currency_id,

            # -------------------------------------
            # Utilisateur
            # -------------------------------------

            "generated_by":
                self.env.user,

            "generated_at":
                generated_at,

            "print_date":
                generated_at.strftime(
                    "%d/%m/%Y %H:%M:%S"
                ),

            # -------------------------------------
            # Période
            # -------------------------------------

            "date_from":
                self.date_from,

            "date_to":
                self.date_to,

            "period_days":
                (
                    self.date_to - self.date_from
                ).days + 1,

            # -------------------------------------
            # Informations
            # -------------------------------------

            "year":
                generated_at.year,

            "month":
                generated_at.strftime("%B"),

            "day":
                generated_at.day,

            # -------------------------------------
            # Données
            # -------------------------------------

            "report_data":
                report_data,

        }

    # =====================================================
    # APERÇU HTML
    # =====================================================

    def action_preview(self):

        self.ensure_one()

        context = self._get_render_context()

        html = self.env["ir.qweb"]._render(

            "primetech_reporting_center.sales_periodic_pdf",

            context,

        )

        preview = self.env[
            "primetech.sales.preview.wizard"
        ].create({

            "name":
                "Rapport Périodique des Ventes",

            "html":
                html.decode()
                if isinstance(html, bytes)
                else html,

            "pdf_report_ref":
                "primetech_reporting_center.sales_periodic_pdf_report",

            "xlsx_report_ref":
                "primetech_reporting_center.sales_periodic_xlsx_report",

            "wizard_id":
                self.id,

        })

        return {

            "type":
                "ir.actions.act_window",

            "name":
                "Aperçu du Rapport",

            "res_model":
                "primetech.sales.preview.wizard",

            "res_id":
                preview.id,

            "view_mode":
                "form",

            "view_id":
                self.env.ref(
                    "primetech_reporting_center.view_sales_preview_wizard_form"
                ).id,

            "target":
                "current",

        }

    # =====================================================
    # IMPRESSION PDF
    # =====================================================

    def action_print_pdf(self):

        self.ensure_one()

        return self.env.ref(
            "primetech_reporting_center.sales_periodic_pdf_report"
        ).report_action(self)

    # =====================================================
    # EXPORT EXCEL
    # =====================================================

    def action_export_xlsx(self):

        self.ensure_one()

        return self.env.ref(
            "primetech_reporting_center.sales_periodic_xlsx_report"
        ).report_action(self)