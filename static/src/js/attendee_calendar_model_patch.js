/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { AttendeeCalendarModel } from "@calendar/views/attendee_calendar/attendee_calendar_model";

patch(AttendeeCalendarModel.prototype, {
    /**
     * @override
     * Force la couleur des événements à être basée sur le produit récurrent
     * lié, plutôt que sur le participant (comportement standard d'Odoo).
     */
    async updateAttendeeData(data) {
        await super.updateAttendeeData(...arguments);

        for (const record of Object.values(data.records)) {
            const productField = record.rawRecord.recurring_product_id;
            if (productField) {
                // Many2one renvoie [id, display_name]
                record.colorIndex = Array.isArray(productField) ? productField[0] : productField;
            }
        }
    },
});