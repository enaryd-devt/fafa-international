# -*- coding: utf-8 -*-
from odoo import models


class ExecutivePartnerBalancePdfReport(models.AbstractModel):
    _name = 'report.primetech_reporting_center.executive_partner_balance_pdf'
    _description = 'Executive Partner Balance PDF Report'

    def _get_report_values(self, docids, data=None):
        data = data or {}
        report_data = self.env['primetech.dashboard'].get_partner_balance_report_data(
            data.get('partner_type'), data.get('rows'), data.get('summary')
        )
        return {
            'doc_ids': docids,
            'doc_model': 'res.company',
            'docs': self.env.company,
            'report_data': report_data,
        }
