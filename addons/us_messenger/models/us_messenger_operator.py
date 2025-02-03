from odoo import api, fields, models, tools

MESSENGER_TYPES = ["telegram", "viber", "whatsapp_twilio", "instagram"]


class UsMessengerOperator(models.Model):
    _name = "us.messenger.operator"
    _auto = False
    _description = "Operators"

    user_id = fields.Many2one('res.users', string="User")
    bot_id = fields.Many2one('us.messenger.project', string="Bot")
    name = fields.Char('User Name')
    channel_count = fields.Integer(compute='_compute_channel_count', string='Channel count')
    activity_state = fields.Selection([('telegram', 'Telegram'),
                                       ('viber', 'Viber'),
                                       ('whatsapp', 'WhatsApp'),
                                       ('instagram', 'Instagram')],
                                      string='Activity State',
                                      compute='_compute_activity_state')
    color = fields.Integer(string='Color', compute="_compute_color")
    messenger_color = fields.Integer(string='Color', compute="_compute_messenger_color")

    def _compute_color(self):
        for record in self:
            if not record.user_id:
                record.color = 1
            else:
                record.color = record.messenger_color

    def _compute_messenger_color(self):
        colors = {'telegram': 4,
                  'viber': 5,
                  'whatsapp': 10,
                  'instagram': 9,
                  'none': 0,
                  }
        for record in self:
            if colors.get(record.activity_state):
                record.messenger_color = colors[record.activity_state]
            else:
                record.messenger_color = colors["none"]

    def _compute_activity_state(self):
        for record in self:
            for state in record.sudo().bot_id.eval_context_ids:
                record.activity_state = state.name

    def _compute_channel_count(self):
        for record in self:
            us_messenger_links = self.env['us.messenger.link'].sudo().search(
                [('bot_id', '=', record.sudo().bot_id.id), ('model', '=', 'discuss.channel')])
            channel_by_link_ids = tuple(map(lambda o: o.ref2, us_messenger_links))
            record.channel_count = self.env['discuss.channel'].sudo().search_count(
                [('messenger_operator_id', '=', record.user_id.partner_id.id), ('id', 'in', channel_by_link_ids)])

    @api.model
    def init(self):
        tools.drop_view_if_exists(self._cr, 'us_messenger_operator')
        self._cr.execute("""
                    CREATE OR REPLACE VIEW us_messenger_operator AS (
                        SELECT
                            row_number() OVER () as id,
                            ru.id as user_id,
                            ump.bot_id as bot_id,
                            COALESCE(rp.name, 'NO OPERATOR') as name
                        FROM us_messenger_partner ump
                        LEFT JOIN discuss_channel dc ON dc.id = ump.channel_id
                        LEFT JOIN res_partner rp ON rp.id = dc.messenger_operator_id
                        LEFT JOIN res_users ru ON ru.partner_id = rp.id
                        WHERE ump.channel_id IS NOT NULL
                        GROUP BY ump.bot_id, ru.id, rp.name
                        
                    )
                """)

    def get_action(self):
        user_partner_id = self.sudo().user_id.partner_id.id
        us_messenger_links = self.env['us.messenger.link'].sudo().search([('bot_id', '=', self.sudo().bot_id.id), ('model', '=', 'discuss.channel')])
        channel_by_link_ids = tuple(map(lambda o: o.ref2, us_messenger_links))
        channels_by_operator = self.env['discuss.channel'].sudo().search([('messenger_operator_id', '=', user_partner_id), ('id', 'in', channel_by_link_ids)])

        return {
            'name': 'Messenger Channels',
            'res_model': 'us.messenger.partner',
            'view_mode': 'list',
            'domain': [('channel_id', 'in', channels_by_operator.ids)],
            'type': 'ir.actions.act_window',
            'view_id': self.env.ref('us_messenger.discuss_channel_view_list').id,
        }
