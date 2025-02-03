from odoo import models


class MailThread(models.AbstractModel):

    _inherit = 'mail.thread'

    def _get_message_create_valid_field_names(self):
        result = super(MailThread, self)._get_message_create_valid_field_names()
        result.add('document_message_id')
        result.add('external_messenger_id')
        return result

    def _get_allowed_message_post_params(self):
        return super()._get_allowed_message_post_params() | {"document_message_id"}