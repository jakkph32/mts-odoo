/** @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { Thread } from "@mail/core/common/thread_model";
import { patch } from "@web/core/utils/patch";
import { user } from "@web/core/user";
import { rpc } from "@web/core/network/rpc";
import { url } from "@web/core/utils/urls";

patch(Thread.prototype, {
    /**
    * @override
    */
    async post(body, postData = {}, extraData = {}) {
        const message = await super.post(...arguments);
        if(this.model === "discuss.channel"){
            return message;
        }
        let tmpMsg;
        const params = await this.store.getMessagePostParams({ body, postData, thread: this });
        Object.assign(params, {thread_model:'discuss.channel'});
        Object.assign(params.post_data, {document_message_id:message.id});

        let model_name = await rpc(`/mail/get_model_name`, {model:this.model});
        if (!model_name){
            model_name = this.model;
        }

        params.post_data.body += `<b><a href="${url(`/mail/message/${message.id}`)}"><br/><br/>Link on Message in ${model_name} "${this.name}". </a></b>`;
        let checked_recipients = this.messengerRecipients.filter((recipient) => recipient.checked === true)
        let recipients_ids = checked_recipients.map((recipient) => recipient.persona?.id);

        let undefined_recipients = this.messengerRecipients.filter((recipient) => !recipient.persona?.id);
        if (undefined_recipients.length > 0){
            let names = undefined_recipients.map((recipient) => recipient.name);
            this.store.env.services.notification.add(_t(names.join() + " hasn't partner"),{
                    type: 'warning',
                });
            return;
        }

        let userPartnerId = await this.store.env.services.orm.call("res.users", "search_read", [], {
                domain: [
                    ["id", "=", user.userId],
                ],
                fields: ['partner_id'],
            },
        );
        if(!userPartnerId) {
            this.store.env.services.notification.add("The user " + user.name + " hasn't partner in Contacts",{
                    type: 'warning',
                });
            return;
        }

        let userPartner = await this.store.env.services.orm.call("res.partner", "search_read", [], {
                domain: [
                    ["id", "=", userPartnerId[0].partner_id[0]],
                ],
                fields: ['channel_ids'],
            },
        );

        let partners = await this.store.env.services.orm.call("res.partner", "search_read", [], {
                domain: [
                    ["id", "in", recipients_ids],
                ],
                fields: ['channel_ids'],
            },
        );

        for(let partner of partners){
            let intersectionChannels = partner.channel_ids.filter(value => userPartner[0].channel_ids.includes(value));
            if (intersectionChannels[0] === undefined){
                this.env.services.notification.add(_t("The user is not attached to the channel"),{
                    type: 'warning',
                });
                return;
            }
            Object.assign(params, {thread_id:intersectionChannels[0]});
            await this.store.doMessagePost(params, tmpMsg);
        }
        return message;


        // 17.0 version
//        if (thread.type === 'chatter'){
//             let params = await this.getMessagePostParams({
//                attachments,
//                body,
//                cannedResponseIds,
//                isNote,
//                mentionedChannels,
//                mentionedPartners,
//                thread,
//            });
//
//            Object.assign(params.post_data, {document_message_id:message.id});
//            Object.assign(params, {thread_model:'discuss.channel'});
//
//            let model_name = thread.model_name;
//            if (!model_name){
//                model_name = await this.rpc(`/mail/get_model_name`, {model:thread.model});
//                if (!model_name){
//                    model_name = thread.model;
//                }
//            }
//
//            params.post_data.body += `<b><a href="/web#id=${thread.id}&model=${thread.model}"><br/><br/>Link on model ${model_name} "${thread.name}". </a></b>`;
//
//            let checked_recipients = thread.messengerRecipients.filter((recipient) => recipient.checked === true)
//            let recipients_ids = checked_recipients.map((recipient) => recipient.persona?.id);
//
//            let undefined_recpients = thread.messengerRecipients.filter((recipient) => !recipient.persona?.id);
//            if (undefined_recpients.length > 0){
//                let names = undefined_recpients.map((recipient) => recipient.name);
//                this.env.services.notification.add(_t(names.join() + " hasn't partner"),{
//                        type: 'warning',
//                    });
//                    return;
//            }
//
//            let userPartner = this.user.partnerId;
//
//            let userPartnerS = await this.orm.call("res.partner", "search_read", [], {
//                    domain: [
//                        ["id", "=", userPartner],
//                    ],
//                },
//            );
//
//            let partners = await this.orm.call("res.partner", "search_read", [], {
//                    domain: [
//                        ["id", "in", recipients_ids],
//                    ],
//                },
//            );
//
//
//            for(let partner of partners){
//                let intersectionChannels = partner.channel_ids.filter(value => userPartnerS[0].channel_ids.includes(value));
//                if (intersectionChannels[0] === undefined){
//                    this.env.services.notification.add(_t("The user is not attached to the channel"),{
//                        type: 'warning',
//                    });
//                    return;
//                }
//                Object.assign(params, {thread_id:intersectionChannels[0]});
//                await this.rpc(this.getMessagePostRoute(thread), params);
//            }
//        }
    },
});
