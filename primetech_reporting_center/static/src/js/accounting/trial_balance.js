/** @odoo-module **/

import {
    Component,
    useState,
    onWillStart,
} from "@odoo/owl";

import { rpc } from "@web/core/network/rpc";

import { registry }
from "@web/core/registry";


export class TrialBalance extends Component {

    setup() {

            this.state = useState({

                loading: true,

                data: {

                    lines: [],

                    totals_bilan: {

                        opening_debit: 0,
                        opening_credit: 0,
                        period_debit: 0,
                        period_credit: 0,
                        closing_debit: 0,
                        closing_credit: 0,

                    },

                    totals_gestion: {

                        opening_debit: 0,
                        opening_credit: 0,
                        period_debit: 0,
                        period_credit: 0,
                        closing_debit: 0,
                        closing_credit: 0,

                    },

                    totals_balance: {

                        opening_debit: 0,
                        opening_credit: 0,
                        period_debit: 0,
                        period_credit: 0,
                        closing_debit: 0,
                        closing_credit: 0,

                    },

                },

            });

        onWillStart(
            async () => {

                await this.loadData();

            }
        );

    }

    async loadData() {

        this.state.loading = true;

        try {

            this.state.data =
                await rpc(

                    "/primetech_reporting/accounting/trial_balance",

                    {}

                );

        }

        finally {

            this.state.loading = false;

        }

    }

    formatCurrency(value) {

        return new Intl.NumberFormat(

            "fr-FR"

        ).format(

            value || 0

        );

    }

}

TrialBalance.template =
    "primetech_reporting_center.TrialBalance";


registry
    .category("actions")
    .add(

        "primetech_trial_balance",

        TrialBalance

    );