/* @odoo-module */

import { Thread } from "@mail/core/common/thread_model";
//import { nextId } from "@mail/core/web/thread_service_patch";

import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";

import { user } from "@web/core/user";

let nextRecipientId = 1;
patch(Thread.prototype, {
    /**
     * @override
     */
    async fetchData(requestList) {
        const result = await super.fetchData(requestList);
        if (requestList.some(item => item == "followers") || requestList.some(item => item == "suggestedRecipients")) {
            await this.insertMessengerRecipients(this.suggestedRecipients, this.followers);
        }
        return result;
    },
    /**
     * @param {import("models").Thread} thread
     * @param {import("@mail/core/web/suggested_recipient").SuggestedRecipient[]} dataRecipients
     * @param {import("models").Follower} dataFollowers
     */
    async insertMessengerRecipients(dataRecipients, dataFollowers) {
        const recipients = [];
        const partners = [];

        dataRecipients.map((recipient) => partners.push(recipient.persona?.id));
        dataFollowers.map((follower) => partners.push(follower.partner?.id));

        let userPartnerId = await this.store.env.services.orm.call("res.users", "search_read", [], {
                domain: [
                    ["id", "=", user.userId],
                ],
                fields: ['partner_id'],
            },
        );

        let userPartner = await this.store.env.services.orm.call("res.partner", "search_read", [], {
                domain: [
                    ["id", "=", userPartnerId[0].partner_id[0]],
                ],
                fields: ['channel_ids'],
            },
        );

        if(!userPartner[0].channel_ids){
            this.store.env.services.notification.add("The user " + user.name + " hasn't any channels",{
                    type: 'warning',
                });
            return;
        }

        let partnerIds = await this.store.env.services.orm.call("res.partner", "search_read", [], {
                    domain: [
                         "|",
                        ["parent_id", "in", partners],
                        ["id", "in", partners],
                    ],
                    fields: ['id','name','user_ids','type_messenger','channel_ids'],
                },
        );
        partnerIds = partnerIds.filter( partner => !partner.user_ids.length);
        for (const partner of partnerIds) {
            let intersectionChannels = partner.channel_ids.filter(value => userPartner[0].channel_ids.includes(value));
            if (partner && partner.type_messenger && partner.type_messenger !== "none" && intersectionChannels.length != 0) {
                recipients.push({
                    id: nextRecipientId++,
                    name: partner.name,
                    persona: partner.id ? { type: "partner", id: partner.id } : false,
                    type_messenger: partner.type_messenger,
                    checked: false,
                });
            }
        }
        Object.assign(this, {messengerRecipients:recipients});
    },
});