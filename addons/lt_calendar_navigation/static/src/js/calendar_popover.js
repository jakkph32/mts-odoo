/** @odoo-module **/

import { AttendeeCalendarCommonPopover } from "@calendar/views/attendee_calendar/common/attendee_calendar_common_popover";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { sprintf } from "@web/core/utils/strings";


patch(AttendeeCalendarCommonPopover.prototype, {
    async onClickNavigateTo() {
        window.location.href = sprintf('https://www.google.com/maps/search/?api=1&query=%s', this.props.record.rawRecord.location);
    }
})