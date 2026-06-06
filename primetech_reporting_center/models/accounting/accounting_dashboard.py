from odoo import api, fields, models
from dateutil.relativedelta import relativedelta


class PrimetechAccountingDashboard(models.AbstractModel):

    _name = "primetech.accounting.dashboard"

    _description = "Primetech Accounting Dashboard"

    @api.model
    def get_dashboard_data(self):

        return {

            "title": "Comptabilité",

        }


    @api.model
    def get_finance_kpis(self):

        today = fields.Date.today()

        current_month_start = today.replace(
            day=1
        )

        previous_month_start = (
            current_month_start
            - relativedelta(months=1)
        )

        previous_month_end = (
            current_month_start
            - relativedelta(days=1)
        )

        current_revenue = sum(

            self.env[
                "sale.report"
            ].search([

                (
                    "date",
                    ">=",
                    current_month_start
                )

            ]).mapped(

                "price_total"

            )

        )

        previous_revenue = sum(

            self.env[
                "sale.report"
            ].search([

                (
                    "date",
                    ">=",
                    previous_month_start
                ),

                (
                    "date",
                    "<=",
                    previous_month_end
                )

            ]).mapped(

                "price_total"

            )

        )

        revenue_variation = 0

        if previous_revenue:

            revenue_variation = (

                (
                    current_revenue
                    - previous_revenue
                )
                / previous_revenue

            ) * 100

        receivables = sum(

            self.env[
                "account.move"
            ].search([

                (
                    "move_type",
                    "=",
                    "out_invoice"
                ),

                (
                    "state",
                    "=",
                    "posted"
                )

            ]).mapped(

                "amount_residual"

            )

        )

        payables = sum(

            self.env[
                "account.move"
            ].search([

                (
                    "move_type",
                    "=",
                    "in_invoice"
                ),

                (
                    "state",
                    "=",
                    "posted"
                )

            ]).mapped(

                "amount_residual"

            )

        )

        cash = 0

        accounts = self.env[
            "account.account"
        ].search([

            (
                "account_type",
                "=",
                "asset_cash"
            )

        ])

        for account in accounts:

            cash += getattr(
                account,
                "current_balance",
                0
            )

        return {

            "revenue": {

                "value":
                    round(
                        current_revenue
                    ),

                "variation":
                    round(
                        revenue_variation,
                        1
                    ),

            },

            "receivables":
                round(
                    receivables
                ),

            "payables":
                round(
                    payables
                ),

            "cash":
                round(
                    cash
                ),

        }
        
    @api.model
    def get_financial_health(self):

        kpis = self.get_finance_kpis()

        receivables = kpis["receivables"]

        payables = kpis["payables"]

        cash = kpis["cash"]

        revenue = kpis["revenue"]["value"]

        score = 100

        if receivables > revenue * 0.50:
            score -= 20

        if payables > cash:
            score -= 20

        if cash <= 0:
            score -= 30

        if score >= 85:

            level = "Excellent"

            color = "success"

        elif score >= 70:

            level = "Bon"

            color = "info"

        elif score >= 50:

            level = "Attention"

            color = "warning"

        else:

            level = "Risque"

            color = "danger"

        return {

            "score": score,

            "level": level,

            "color": color,

            "cash": cash,

            "receivables": receivables,

            "payables": payables,

        }
    
    @api.model
    def get_receivables_analysis(self):

        invoices = self.env[
            "account.move"
        ].search([

            (
                "move_type",
                "=",
                "out_invoice"
            ),

            (
                "state",
                "=",
                "posted"
            ),

            (
                "payment_state",
                "!=",
                "paid"
            ),

        ])

        total_receivables = sum(

            invoices.mapped(
                "amount_residual"
            )

        )

        overdue_invoices = invoices.filtered(

            lambda inv:

            inv.invoice_date_due

            and

            inv.invoice_date_due
            < fields.Date.today()

        )

        overdue_amount = sum(

            overdue_invoices.mapped(
                "amount_residual"
            )

        )

        risk_customers = len(

            overdue_invoices.mapped(
                "partner_id"
            )

        )

        top_debtors = []

        grouped = {}

        for invoice in invoices:

            partner = invoice.partner_id

            grouped.setdefault(

                partner.id,

                {

                    "id": partner.id,

                    "name": partner.name,

                    "amount": 0,

                }

            )

            grouped[
                partner.id
            ]["amount"] += (

                invoice.amount_residual

            )

        top_debtors = sorted(

            grouped.values(),

            key=lambda x: x["amount"],

            reverse=True,

        )[:5]

        return {

            "total_receivables":
                total_receivables,

            "overdue_amount":
                overdue_amount,

            "risk_customers":
                risk_customers,

            "top_debtors":
                top_debtors,

        }
    @api.model
    def get_cashflow_forecast(self):

        incoming = sum(

            self.env[
                "account.move"
            ].search([

                (
                    "move_type",
                    "=",
                    "out_invoice"
                ),

                (
                    "payment_state",
                    "!=",
                    "paid"
                )

            ]).mapped(

                "amount_residual"

            )

        )

        outgoing = sum(

            self.env[
                "account.move"
            ].search([

                (
                    "move_type",
                    "=",
                    "in_invoice"
                ),

                (
                    "payment_state",
                    "!=",
                    "paid"
                )

            ]).mapped(

                "amount_residual"

            )

        )

        projected = incoming - outgoing

        return {

            "incoming": incoming,

            "outgoing": outgoing,

            "projected": projected,

        }
    

    @api.model
    def get_financial_position(self):

        assets = sum(

            self.env["account.account"].search([

                ("account_type", "like", "asset")

            ]).mapped(

                "current_balance"

            )

        )

        liabilities = sum(

            self.env["account.account"].search([

                ("account_type", "like", "liability")

            ]).mapped(

                "current_balance"

            )

        )

        equity = assets - liabilities

        liquidity_ratio = 0

        if liabilities:

            liquidity_ratio = (

                assets / liabilities

            )

        debt_ratio = 0

        if assets:

            debt_ratio = (

                liabilities / assets

            )

        if liquidity_ratio >= 2:

            level = "Excellent"

        elif liquidity_ratio >= 1.2:

            level = "Bon"

        else:

            level = "À surveiller"

        return {

            "assets": assets,

            "liabilities": liabilities,

            "equity": equity,

            "liquidity_ratio": round(
                liquidity_ratio,
                2
            ),

            "debt_ratio": round(
                debt_ratio,
                2
            ),

            "level": level,

        }
