/** @odoo-module **/

import { Component, onMounted, onWillStart, useRef, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class InterAgencyTransferDashboard extends Component {
    static template = "primetech_inter_agency_transfer.Dashboard";

    setup() {
        this.orm = useService("orm");
        this.state = useState({ html: "", loading: true });
        this.content = useRef("content");
        onWillStart(async () => {
            this.state.html = await this.orm.call(
                "primetech.inter.agency.transfer.dashboard",
                "get_dashboard_html",
                []
            );
            this.state.loading = false;
        });
        onMounted(() => {
            this.content.el.innerHTML = this.state.html;
        });
    }
}

registry.category("actions").add(
    "primetech_inter_agency_transfer.dashboard",
    InterAgencyTransferDashboard
);
