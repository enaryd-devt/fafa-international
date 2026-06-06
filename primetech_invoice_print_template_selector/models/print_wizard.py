from odoo import fields, models
from odoo.exceptions import UserError

WARRANTY_LABELS = {
"15": "QUINZE (15) mois",
"12": "DOUZE (12) mois",
"6": "SIX (06) mois",
"1": "UN (01) mois",
}

class InvoicePrintWizard(models.TransientModel):
    _name = "primetech.invoice.print.wizard"
    _description = "Assistant d'impression de facture"


    warranty_period = fields.Selection(
        [
            ("15", "Garantie 15 mois"),
            ("12", "Garantie 12 mois"),
            ("6", "Garantie 06 mois"),
            ("1", "Garantie 01 mois"),
        ],
        string="Durée de garantie",
        required=True,
        default="15",
    )

    print_agreement_protocol = fields.Boolean(
        string="Joindre le protocole d'accord SAV",
        default=False,
        help="Ajoute le protocole d'accord à la suite de la facture dans le même document PDF.",
    )

    def action_print(self):
        self.ensure_one()

        active_id = self.env.context.get("active_id")

        if not active_id:
            raise UserError(
                "Aucune facture n'a été sélectionnée."
            )

        invoice = self.env["account.move"].browse(active_id)

        if not invoice.exists():
            raise UserError(
                "La facture sélectionnée est introuvable."
            )

        warranty_months = int(self.warranty_period)
        warranty_label = WARRANTY_LABELS.get(
            self.warranty_period,
            ""
        )

        return self.env.ref(
            "primetech_invoice_print_template_selector.action_report_invoice_custom"
        ).with_context(
            warranty_months=warranty_months,
            warranty_label=warranty_label,
            print_agreement_protocol=self.print_agreement_protocol,
        ).report_action(invoice)
