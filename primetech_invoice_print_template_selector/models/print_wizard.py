from odoo import models, fields

class InvoicePrintWizard(models.TransientModel):
    _name = 'primetech.invoice.print.wizard'
    _description = 'Invoice Print Wizard'

    template = fields.Selection([
        ('template_1', 'Modèle facture Garantie 15 mois'),
        ('template_2', 'Modèle facture Garantie 12 mois'),
        ('template_3', 'Modèle facture Garantie 06 mois'),
        ('template_4', 'Modèle facture Garantie 01 mois'),
    ], required=True, default='template_1')

    def action_print(self):
        self.ensure_one()

        invoice = self.env['account.move'].browse(
            self.env.context.get('active_id')
        )

        return self.env.ref(
            'primetech_invoice_print_template_selector.action_report_invoice_custom'
        ).with_context(
            selected_template=self.template
        ).report_action(invoice)