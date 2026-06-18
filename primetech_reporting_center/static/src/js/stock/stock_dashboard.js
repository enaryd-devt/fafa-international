/** @odoo-module **/

import { Component } from "@odoo/owl";
import { useState } from "@odoo/owl";
import { onMounted } from "@odoo/owl";
import { onWillStart } from "@odoo/owl";

import { registry } from "@web/core/registry";

import { rpc } from "@web/core/network/rpc";

export class StockDashboard extends Component {

    setup() {

        this.state = useState({

            loading: true,

            products_count: 0,

            stock_qty: 0,

            stock_value: 0,

            out_of_stock: 0,

            dormant_products: 0,

            locations_count: 0,

            lots_count: 0,

            pending_pickings: 0,

            incoming_count: 0,

            outgoing_count: 0,

            internal_count: 0,

            top_products: [],

            categories: [],

            monthly_moves: [],
        });

        this.categoryChart = null;

        this.monthlyChart = null;

        onWillStart(
            async () => {

                await this.loadDashboard();

            }
        );

        onMounted(
            () => {

                this.renderCharts();

            }
        );
    }
    
    formatCurrency(value) {

        return new Intl.NumberFormat(
            "fr-FR",
            {
                minimumFractionDigits: 0,
                maximumFractionDigits: 0,
            }
        ).format(value || 0) + " FCFA";
    }

    async loadDashboard() {

        try {

            const data = await rpc(

                "/primetech/stock/dashboard",

                {}

            );

            Object.assign(
                this.state,
                data
            );

            this.state.loading = false;

        } catch (error) {

            console.error(
                "Erreur Dashboard Stock",
                error
            );

        }
    }

    renderCharts() {

        if (
            typeof Chart === "undefined"
        ) {

            console.warn(
                "Chart.js non chargé"
            );

            return;
        }

        this.renderCategoryChart();

        this.renderMonthlyChart();
    }
        renderCategoryChart() {

        const canvas = document.getElementById(
            "stockCategoryChart"
        );

        if (!canvas) {
            return;
        }

        if (
            !this.state.categories
            ||
            !this.state.categories.length
        ) {
            return;
        }

        if (
            this.categoryChart
        ) {

            this.categoryChart.destroy();

        }

        const labels =
            this.state.categories.map(
                category => category.name
            );

        const values =
            this.state.categories.map(
                category => category.value
            );

        this.categoryChart = new Chart(

            canvas,

            {

                type: "pie",

                data: {

                    labels: labels,

                    datasets: [

                        {

                            label:
                                "Valeur Stock",

                            data:
                                values,

                            borderWidth: 1,

                        }

                    ]

                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    plugins: {

                        legend: {

                            position: "right",

                        }

                    }

                }

            }

        );
    }

    renderMonthlyChart() {

        const canvas = document.getElementById(
            "stockMonthlyChart"
        );

        if (!canvas) {
            return;
        }

        if (
            !this.state.monthly_moves
            ||
            !this.state.monthly_moves.length
        ) {
            return;
        }

        if (
            this.monthlyChart
        ) {

            this.monthlyChart.destroy();

        }

        const labels =
            this.state.monthly_moves.map(
                item => item.month
            );

        const incoming =
            this.state.monthly_moves.map(
                item => item.incoming
            );

        const outgoing =
            this.state.monthly_moves.map(
                item => item.outgoing
            );

        const internal =
            this.state.monthly_moves.map(
                item => item.internal || 0
            );

        this.monthlyChart = new Chart(

            canvas,

            {

                type: "line",

                data: {

                    labels,

                    datasets: [

                        {

                            label:
                                "Entrées",

                            data:
                                incoming,

                            tension: 0.3,

                        },

                        {

                            label:
                                "Sorties",

                            data:
                                outgoing,

                            tension: 0.3,

                        },

                        {

                            label:
                                "Transferts",

                            data:
                                internal,

                            tension: 0.3,

                        }

                    ]

                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    interaction: {

                        intersect: false,

                        mode: "index",

                    },

                    plugins: {

                        legend: {

                            position: "top",

                        }

                    }

                }

            }

        );
    }

}

StockDashboard.template =
    "primetech_reporting_center.StockDashboard";

registry
    .category("actions")
    .add(

        "primetech_stock_dashboard",

        StockDashboard

    );
