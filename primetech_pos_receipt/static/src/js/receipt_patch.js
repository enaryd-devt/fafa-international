/** @odoo-module **/

import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";

patch(PosOrder.prototype, {

    export_for_printing(baseUrl, headerData) {

        const result = super.export_for_printing(
            baseUrl,
            headerData
        );

        const partner =
            this.partner_id ||
            this.partner ||
            false;

        result.partner_name = partner?.name || "";

        return result;
    },

});