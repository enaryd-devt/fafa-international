# -*- coding: utf-8 -*-

from datetime import datetime

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class SalesPeriodicPdfReport(models.AbstractModel):
    _name = "report.primetech_reporting_center.sales_periodic_pdf"
    _description = "Rapport PDF Périodique des Ventes"

    def _get_report_values(self, docids, data=None):

        wizard = self.env[
            "primetech.sales.periodic.report.wizard"
        ].browse(docids)

        if not wizard.exists():
            return {
                "docs": [],
                "report_data": {},
            }

        wizard.ensure_one()

        company = wizard.company_id

        generated_at = datetime.now()

        report_data = self.env[
            "primetech.sales.periodic.report"
        ].get_report_data(

            date_from=wizard.date_from,
            date_to=wizard.date_to,
            company_id=company.id,
            user_id=wizard.user_id.id if wizard.user_id else False,
            partner_id=wizard.partner_id.id if wizard.partner_id else False,
            state_filter=wizard.state_filter,
        )

        return {

            # =====================================
            # Odoo
            # =====================================

            "doc_ids": wizard.ids,

            "doc_model":
                "primetech.sales.periodic.report.wizard",

            "docs":
                wizard,

            # =====================================
            # Société
            # =====================================

            "company":
                company,

            "currency":
                company.currency_id,

            # =====================================
            # Assistant de génération
            # =====================================

            "generated_by":
                self.env.user,

            "generated_at":
                generated_at,

            # =====================================
            # Période
            # =====================================

            "date_from":
                wizard.date_from,

            "date_to":
                wizard.date_to,

            "period_days":
                (
                    wizard.date_to - wizard.date_from
                ).days + 1,

            # =====================================
            # Informations
            # =====================================

            "year":
                generated_at.year,

            "month":
                generated_at.strftime("%B"),

            "day":
                generated_at.day,

            "company_name":
                company.name,

            "company_logo":
                company.logo,

            # =====================================
            # Données
            # =====================================

            "report_data":
                report_data,

            "wizard": wizard,

        }