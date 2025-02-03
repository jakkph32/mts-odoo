from odoo import api, models, fields, _


class MailMessage(models.Model):
    _inherit = 'mail.message'

    external_messenger_id = fields.Char(help='External id for messenger', default='')
    document_message_id = fields.Many2one('mail.message',help="Relates a message that was duplicated from the document")

    def get_my_messages_action(self):
        return {
            'name': _('My Messages'),
            'res_model': 'mail.message',
            'view_mode': 'list',
            'domain': [
                "&",
                    ("model","=","discuss.channel"),
                    "&",
                        "|",
                            "&",
                                ("author_id.type_messenger","=","none"),
                                ("partner_ids.type_messenger","!=","none"),
                            "&",
                                ("author_id.type_messenger","!=","none"),
                                ("partner_ids.type_messenger","=","none"),
                        "|",
                            ("author_id", "=", self.env.user.partner_id.id),
                            ("partner_ids", "in", self.env.user.partner_id.id)
            ],
            'view_id': self.env.ref("us_messenger.us_messenger_mail_message_list", False).id,
            'type': 'ir.actions.act_window',
        }
