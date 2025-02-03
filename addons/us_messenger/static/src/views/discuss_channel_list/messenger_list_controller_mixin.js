import { useState } from "@odoo/owl";

import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

export const MessengerListControllerMixin = (ViewController) =>
    class extends ViewController {
        setup() {
            super.setup(...arguments);
            this.store = useState(useService("mail.store"));
            this.ui = useState(useService("ui"));
        }

        async openRecord(record) {
            const thread = await this.store.Thread.getOrFetch({
                model: "discuss.channel",
                id: record.data.channel_id[0],
            });
            if (thread) {
                thread.pin();
                return thread.open();
            }
            return super.openRecord(record);
        }
    };
