from odoo import http
from odoo.http import request


class AccountingController(http.Controller):

    @http.route(
        "/primetech_reporting/accounting/dashboard",
        type="json",
        auth="user"
    )
    def accounting_dashboard(self, **kwargs):

        return request.env[
            "primetech.accounting.dashboard"
        ].get_dashboard_data()
    
    @http.route(
    "/primetech_reporting/accounting/kpis",
    type="json",
    auth="user"
    )
    def finance_kpis(self, **kwargs):

        return request.env[
            "primetech.accounting.dashboard"
        ].get_finance_kpis()
    

    @http.route(
        "/primetech_reporting/accounting/kpis",
        type="json",
        auth="user"
    )
    def finance_kpis(
        self,
        **kwargs
    ):

        return request.env[
            "primetech.accounting.dashboard"
        ].get_finance_kpis()
    
    @http.route(
        "/primetech_reporting/accounting/financial_health",
        type="json",
        auth="user"
    )
    def financial_health(self, **kwargs):

        return request.env[
            "primetech.accounting.dashboard"
        ].get_financial_health()
    
    @http.route(
        "/primetech_reporting/accounting/receivables",
        type="json",
        auth="user"
    )
    def receivables_analysis(
        self,
        **kwargs
    ):

        return request.env[
            "primetech.accounting.dashboard"
        ].get_receivables_analysis()
    
    @http.route(
    "/primetech_reporting/accounting/financial_position",
    type="json",
    auth="user"
    )
    def financial_position(
        self,
        **kwargs
    ):

        return request.env[
            "primetech.accounting.dashboard"
        ].get_financial_position()
    
    
    @http.route(
        "/primetech_reporting/accounting/trial_balance",
        type="json",
        auth="user"
    )
    def trial_balance(self, **kwargs):

        return request.env[
            "primetech.trial.balance"
        ].get_trial_balance(
            kwargs.get("date_from"),
            kwargs.get("date_to"),
        )