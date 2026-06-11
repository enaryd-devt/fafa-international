from odoo import fields, models



class ReportSalesPreviewWizard(
    models.TransientModel
):

    _name = "primetech.sales.preview.wizard"

    _description = "Prévisualisation Rapport Vente"

    name = fields.Char(
        string="Nom du Rapport"
    )

    html = fields.Html(
        string="Aperçu",
        sanitize=False,
        readonly=True,
    )

    pdf_report_ref = fields.Char()

    xlsx_report_ref = fields.Char()

    wizard_id = fields.Integer()

    def action_print_pdf(self):

        self.ensure_one()

        if not self.pdf_report_ref:
            return False

        return self.env.ref(
            self.pdf_report_ref
        ).report_action(
            self.wizard_id
        )

    def action_export_xlsx(self):

        self.ensure_one()

        if not self.xlsx_report_ref:
            return False

        return self.env.ref(
            self.xlsx_report_ref
        ).report_action(
            self.wizard_id
        )

    def action_back(self):

        self.ensure_one()

        return {

            "type": "ir.actions.act_window",

            "name": "Rapport Périodique des Ventes",

            "res_model":
                "primetech.sales.periodic.report.wizard",

            "view_mode": "form",

            "res_id": self.wizard_id,

            "target": "current",

        }