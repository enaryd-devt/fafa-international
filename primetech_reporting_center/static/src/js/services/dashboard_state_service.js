/** @odoo-module **/

export const dashboardState = {

    save(key, state) {

        sessionStorage.setItem(
            key,
            JSON.stringify(state)
        );

    },

    load(key) {

        const value =
            sessionStorage.getItem(key);

        return value
            ? JSON.parse(value)
            : null;

    },

};