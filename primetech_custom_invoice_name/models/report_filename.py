from odoo import models
import re


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    TARGET_REPORTS = [
        'account.account_invoices',
        'sale.action_report_saleorder',
        'purchase.report_purchaseorder',
    ]

    def _get_report_base_filename(self, report_ref, records):
        """
        Rename only selected reports:
        Partner Name - Document Number
        """

        report_name = report_ref.report_name if report_ref else ''

        if report_name in self.TARGET_REPORTS and records and len(records) == 1:

            record = records[0]

            partner_name = ''
            document_name = ''

            # Partner Name
            if hasattr(record, 'partner_id') and record.partner_id:
                partner_name = record.partner_id.name or ''

            # Document Number
            if hasattr(record, 'name'):
                document_name = record.name or ''

            if not document_name and hasattr(record, 'display_name'):
                document_name = record.display_name or ''

            if partner_name and document_name:

                filename = f"{partner_name} - {document_name}"

                # Remove invalid Windows filename chars
                filename = re.sub(r'[\\/*?:"<>|]', '', filename)

                return filename

        return super()._get_report_base_filename(report_ref, records)