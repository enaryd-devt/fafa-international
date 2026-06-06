# wizard/trial_balance_wizard.py

from odoo import fields, models

class TrialBalanceWizard(models.TransientModel):

    _name = 'primetech.trial.balance.wizard'

    _description = "Balance Générale"

    date_from = fields.Date(
        required=True
    )

    date_to = fields.Date(
        required=True
    )

    level = fields.Selection(
        [
            ("1", "Niveau 1"),
            ("2", "Niveau 2"),
            ("3", "Niveau 3"),
            ("4", "Détail"),
        ],
        default="4",
        string="Niveau"
    )

    posted_only = fields.Boolean(
        string="Écritures validées uniquement",
        default=True
    )

    def action_open_report(self):

        return {

            "type":
                "ir.actions.client",

            "tag":
                "primetech_trial_balance",

            "context": {

                "date_from":
                    str(self.date_from),

                "date_to":
                    str(self.date_to),

                "level":
                    self.level,

            }

        }
