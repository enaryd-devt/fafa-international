/** @odoo-module **/

import {
    Component,
    useState,
    onWillStart,
} from "@odoo/owl";

export class FinanceKpis extends Component {

    setup() {

        this.state = useState({

            loading: true,

            data: {},

        });

        onWillStart(async () => {

            await this.loadData();

        });

    }

    async loadData() {

        try {

            const response = await fetch(

                "/primetech_reporting/dashboard/finance_kpis",

                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/json",

                    },

                }

            );

            const result =
                await response.json();

            this.state.data =
                result.result || result;

        }

        finally {

            this.state.loading = false;

        }

    }

    formatCurrency(value) {

        return (

            new Intl.NumberFormat(
                "fr-FR"
            ).format(value || 0)

            + " FCFA"

        );

    }

}

FinanceKpis.template =
    "primetech_reporting_center.FinanceKpis";