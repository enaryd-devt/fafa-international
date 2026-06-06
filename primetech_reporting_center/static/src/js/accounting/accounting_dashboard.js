/** @odoo-module **/

import {Component, onWillStart, useState,} from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";
import { FinanceKpis } from "./finance_kpis";
import { FinancialHealth }from "./financial_health";
import { ReceivablesAnalysis } from "./receivables_analysis";
import { CashflowForecast } from "./cashflow_forecast";
import { FinancialPosition } from "./financial_position";

export class AccountingDashboard extends Component {
    
    
    setup() {

        

        this.state = useState({

            loading: true,

            title: "",

        });

        onWillStart(async () => {

            await this.loadData();

        });

    }

    async loadData() {

        try {

            const data = await rpc(

                "/primetech_reporting/accounting/dashboard",

                {}

            );

            console.log(
                "ACCOUNTING DATA",
                data
            );

            this.state.title =
                data.title;

        } catch (error) {

            console.error(
                "Erreur Comptabilité",
                error
            );

        } finally {

            this.state.loading =
                false;

        }

    }

}

AccountingDashboard.template =
    "primetech_reporting_center.AccountingDashboard";


AccountingDashboard.components = {

    FinanceKpis,
    FinancialHealth,
    ReceivablesAnalysis,
    CashflowForecast,
    FinancialPosition

};


