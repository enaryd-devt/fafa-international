from odoo import api, fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    allowed_user_ids = fields.Many2many(
        "res.users",
        "account_journal_allowed_user_rel",
        "journal_id",
        "user_id",
        string="Utilisateurs autorisés",
    )

    @api.model
    def search(self, args=None, offset=0, limit=None, order=None):
        if (
            self.env.user.has_group("base.group_system")
            or
            self.env.user.has_group(
                "primetech_journal_security.group_journal_security_manager"
            )
        ):
            return super().search(
                args,
                offset=offset,
                limit=limit,
                order=order,
            )

        return super().search(
            args,
            offset=offset,
            limit=limit,
            order=order,
        )