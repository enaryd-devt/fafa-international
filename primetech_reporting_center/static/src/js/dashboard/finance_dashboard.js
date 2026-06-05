/** @odoo-module **/

import { Component } from "@odoo/owl";

import { FinanceKpis } from "../finance_kpis";

export class FinanceDashboard extends Component {

    static template =
        "primetech_reporting_center.FinanceDashboard";

    static components = {

        FinanceKpis,

    };

}