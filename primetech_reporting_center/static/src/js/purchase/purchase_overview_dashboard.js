/** @odoo-module **/

import { Component, onWillStart, onMounted, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class PrimetechPurchaseOverviewDashboard extends Component {

    setup() {

        this.orm = useService("orm");
        this.action = useService("action");

        this.state = useState({
            loading: true,

            purchase_count: 0,
            supplier_count: 0,
            total_ht: 0,
            total_ttc: 0,
            average_order: 0,

            pending_receipts: 0,
            vendor_bills_to_validate: 0,

            growth_percentage: 0,

            monthly_evolution: [],
            top_suppliers: [],
            top_products: [],
            expense_by_category: [],

            late_purchase_orders: [],
            incomplete_receipts: [],
            blocked_vendor_bills: [],

            recent_purchase_orders: [],
        });

        onWillStart(async () => {
            await this.loadDashboard();
        });

        onMounted(() => {
            this.renderCharts();
        });
    }

    async loadDashboard() {

        try {

            const result = await this.orm.call(
                "primetech.purchase.overview",
                "get_dashboard_data",
                []
            );

            Object.assign(this.state, result);

            this.state.loading = false;

            setTimeout(() => {
                this.renderCharts();
            }, 100);

        } catch (error) {

            console.error(
                "Primetech Purchase Dashboard Error",
                error
            );

            this.state.loading = false;
        }
    }

    formatCurrency(value) {

        return new Intl.NumberFormat(
            "fr-FR",
            {
                minimumFractionDigits: 0,
                maximumFractionDigits: 0,
            }
        ).format(value || 0);
    }

    renderCharts() {

        if (typeof Chart === "undefined") {
            return;
        }

        this.renderMonthlyEvolutionChart();
        this.renderSuppliersChart();
        this.renderProductsChart();
        this.renderCategoryChart();
    }

    renderMonthlyEvolutionChart() {

        const canvas =
            document.getElementById(
                "pt_purchase_monthly_chart"
            );

        if (!canvas) {
            return;
        }

        const existing =
            Chart.getChart(canvas);

        if (existing) {
            existing.destroy();
        }

        new Chart(canvas, {
            type: "line",
            data: {
                labels:
                    this.state.monthly_evolution.map(
                        item => item.month
                    ),

                datasets: [{
                    label: "Achats",
                    data:
                        this.state.monthly_evolution.map(
                            item => item.amount
                        ),
                    tension: 0.4,
                    fill: true,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
            }
        });
    }

    renderSuppliersChart() {

        const canvas =
            document.getElementById(
                "pt_supplier_chart"
            );

        if (!canvas) {
            return;
        }

        const existing =
            Chart.getChart(canvas);

        if (existing) {
            existing.destroy();
        }

        new Chart(canvas, {

            type: "doughnut",

            data: {

                labels:
                    this.state.top_suppliers.map(
                        item => item.name
                    ),

                datasets: [{
                    data:
                        this.state.top_suppliers.map(
                            item => item.amount
                        ),
                }]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,
            }
        });
    }

    renderProductsChart() {

        const canvas =
            document.getElementById(
                "pt_products_chart"
            );

        if (!canvas) {
            return;
        }

        const existing =
            Chart.getChart(canvas);

        if (existing) {
            existing.destroy();
        }

        new Chart(canvas, {

            type: "bar",

            data: {

                labels:
                    this.state.top_products.map(
                        item => item.name
                    ),

                datasets: [{
                    data:
                        this.state.top_products.map(
                            item => item.amount
                        ),
                }]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,
            }
        });
    }

    renderCategoryChart() {

        const canvas =
            document.getElementById(
                "pt_category_chart"
            );

        if (!canvas) {
            return;
        }

        const existing =
            Chart.getChart(canvas);

        if (existing) {
            existing.destroy();
        }

        new Chart(canvas, {

            type: "pie",

            data: {

                labels:
                    this.state.expense_by_category.map(
                        item => item.category
                    ),

                datasets: [{
                    data:
                        this.state.expense_by_category.map(
                            item => item.amount
                        ),
                }]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,
            }
        });
    }

    getGrowthClass() {

        return this.state.growth_percentage >= 0
            ? "text-success"
            : "text-danger";
    }

    getGrowthIcon() {

        return this.state.growth_percentage >= 0
            ? "fa-arrow-trend-up"
            : "fa-arrow-trend-down";
    }
}

PrimetechPurchaseOverviewDashboard.template =
    "primetech_reporting_center.PurchaseOverviewDashboard";

registry.category("actions").add(
    "primetech_purchase_overview_dashboard",
    PrimetechPurchaseOverviewDashboard
);

export default PrimetechPurchaseOverviewDashboard;