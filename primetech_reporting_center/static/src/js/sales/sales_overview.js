/** @odoo-module **/

import { Component, onWillStart, useState }
from "@odoo/owl";

import { registry }
from "@web/core/registry";

import { useService }
from "@web/core/utils/hooks";

import { xml, onMounted,} from "@odoo/owl";


export class SalesOverviewDashboard
extends Component {


    setup() {

        this.orm =
            useService("orm");

        this.state = useState({

            loaded: false,

            data: {},

        });

        onWillStart(
            async () => {

                this.state.data =
                    await this.orm.call(

                        "primetech.sales.overview",

                        "get_dashboard_data",

                        []

                    );

                this.state.loaded = true;
            }
        );

        onMounted(() => {

            setTimeout(() => {

                this.renderChart();

            }, 100);

        });

        
    }

    renderChart() {

        const canvas =
            document.getElementById(
                "salesEvolutionChart"
            );

        if (!canvas) {
            return;
        }

        const labels =
            this.state.data.monthly_sales.map(
                item => item.month
            );

        const values =
            this.state.data.monthly_sales.map(
                item => item.amount
            );

        new Chart(
            canvas,
            {

                type: "line",

                data: {

                    labels,

                    datasets: [

                        {

                            label:
                                "CA HT",

                            data: values,

                            tension: 0.3,

                        },

                    ],

                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                },

            }
        );

    }


    }

    SalesOverviewDashboard.template =
    "primetech_reporting_center.SalesOverviewDashboard";

    registry.category("actions").add(
    "primetech_sales_overview_dashboard",
    SalesOverviewDashboard
    );
