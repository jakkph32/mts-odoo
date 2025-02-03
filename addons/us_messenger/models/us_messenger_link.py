import logging

from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

from .ir_logging import LOG_DEBUG

_logger = logging.getLogger(__name__)

ODOO = "__odoo__"
ODOO_REF = "ref2"
EXTERNAL = "__external__"
EXTERNAL_REF = "ref1"


class UsMessengerLink(models.Model):

    _name = "us.messenger.link"
    _description = "Resource Links"
    _order = "id desc"

    relation = fields.Char("Relation Name", required=True)
    system1 = fields.Char("System 1", required=True)
    # index system2 only to make search "Odoo links"
    system2 = fields.Char("System 2", required=True, index=True)
    ref1 = fields.Char("Ref 1", required=True)
    ref2 = fields.Char("Ref 2", required=True)
    date = fields.Datetime(
        string="Date", default=fields.Datetime.now, required=True
    )
    model = fields.Char("Odoo Model", index=True)
    active = fields.Boolean('Active', default=True)

    bot_id = fields.Many2one('us.messenger.project', ondelete='cascade')

    def _auto_init(self):
        res = super(UsMessengerLink, self)._auto_init()
        tools.create_unique_index(
            self._cr,
            "messenger_link_refs_uniq_index",
            self._table,
            ["relation", "system1", "system2", "ref1", "ref2", "model"],
        )
        return res

    @api.model
    def _log(self, *args, **kwargs):
        log = self.env.context.get("log_function")
        if not log:
            return
        kwargs.setdefault("name", "us.messenger.link")
        kwargs.setdefault("level", LOG_DEBUG)
        return log(*args, **kwargs)

    # External links
    @api.model
    def refs2vals(self, external_refs):
        '''references to vals for creating model'''
        external_refs = sorted(
            external_refs.items(), key=lambda code_value: code_value[0]
        )
        system1, ref1 = external_refs[0]
        system2, ref2 = external_refs[1]
        vals = {
            "system1": system1,
            "system2": system2,
            "ref1": ref1,
            "ref2": ref2,
        }
        for k in ["ref1", "ref2"]:
            if vals[k] is None:
                continue
            if isinstance(vals[k], list):
                vals[k] = [str(i) for i in vals[k]]
            else:
                vals[k] = str(vals[k])
        return vals

    # delete_my_code_new
    @api.model
    def _set_link_external(
            self, relation, external_refs, bot_id, sync_date=None, allow_many2many=False, model=None
    ):

        vals = self.refs2vals(external_refs)
        # Check for existing records
        if allow_many2many:
            existing = self._search_links_external(relation, external_refs, bot_id)
        else:
            # check existing links for a part of external_refs
            refs1 = external_refs.copy()
            refs2 = external_refs.copy()
            for i, k in enumerate(external_refs.keys()):
                if i:
                    refs1[k] = None
                else:
                    refs2[k] = None
            existing = self._search_links_external(
                relation, refs1, bot_id
            ) or self._search_links_external(relation, refs2, bot_id)
            if existing and not (
                    existing.ref1 == vals["ref1"] and existing.ref2 == vals["ref2"]
            ):
                raise ValidationError(
                    _("%s link already exists: %s=%s, %s=%s")
                    % (
                        relation,
                        existing.system1,
                        existing.ref1,
                        existing.system2,
                        existing.ref2,
                    )
                )

        if existing:
            self._log("{} Use existing link: {}".format(relation, vals))
            existing.update_links(sync_date)
            return existing

        if sync_date:
            vals["date"] = sync_date
        vals["relation"] = relation
        if model:
            vals["model"] = model
        vals['bot_id'] = bot_id
        self._log("Create link: %s" % vals)
        return self.create(vals)

    # delete_my_code_new
    @api.model
    def _get_link_external(self, relation, external_refs, bot_id, model=None):
        links = self._search_links_external(relation, external_refs, bot_id, model=model)
        self._log("Get link: {} {} -> {}".format(relation, external_refs, links))
        return links

    @api.model
    def _search_links_external(
            self, relation, external_refs, bot_id, model=None, make_logs=False
    ):
        vals = self.refs2vals(external_refs)
        domain = [("relation", "=", relation)]
        if model:
            domain.append(("model", "=", model))
        for k, v in vals.items():
            if not v:
                continue
            operator = "in" if isinstance(v, list) else "="
            domain.append((k, operator, v))
        domain.append(('bot_id', '=', bot_id))
        links = self.search(domain)
        if make_logs:
            self._log("Search links: {} -> {}".format(domain, links))
        return links

    def get(self, system):
        res = []
        for r in self:
            if r.system1 == system:
                res.append(r.ref1)
            elif r.system2 == system:
                res.append(r.ref2)
            else:
                raise ValueError(
                    _("Cannot find value for %s. Found: %s and %s")
                    % (system, r.system1, r.system2)
                )
        return res

    # Odoo links
    @property
    def odoo(self):
        res = set()
        model = self.env.context.get("messenger_link_odoo_model")
        for r in self:
            if model is None:
                model = r.model
            elif model != r.model:
                raise ValidationError(
                    _("Mixing apples and oranges: %s and %s") % (model, r.model)
                )
            res.add(int(r[ODOO_REF]))
        return self.env[model].browse(res) if model else None

    @property
    def external(self):
        res = [getattr(r, EXTERNAL_REF) for r in self]
        if len(res) == 1:
            return res[0]
        return res

    # delete_my_code_new
    def _set_link_odoo(
        self, record, relation, ref, bot_id, sync_date=None, allow_many2many=False
    ):
        refs = {ODOO: record.id, EXTERNAL: ref}
        return self._set_link_external(
            relation, refs, bot_id, sync_date, allow_many2many, record._name
        )

    def _get_link_odoo(self, relation, ref, bot_id, model=None):
        refs = {ODOO: None, EXTERNAL: ref}
        return self._get_link_external(relation, refs, bot_id, model=model)

    def _search_links_odoo(self, records, relation, bot_id, refs=None):
        refs = {ODOO: records.ids, EXTERNAL: refs}
        return self._search_links_external(
            relation, refs, bot_id, model=records._name, make_logs=True
        )

    # Common API

    def _get_link(self, rel, ref_info, bot_id, model=None):
        if isinstance(ref_info, dict):
            # External link
            external_refs = ref_info
            return self._get_link_external(rel, external_refs, bot_id, model=model)
        else:
            # Odoo link
            ref = ref_info
            return self._get_link_odoo(rel, ref, bot_id, model=model)

    @property
    def sync_date(self):
        return min(r.date for r in self)

    def update_links(self, sync_date=None):
        if not sync_date:
            sync_date = fields.Datetime.now()
        self.write({"date": sync_date})
        return self

    def __xor__(self, other):
        return (self | other) - (self & other)

    def unlink(self):
        self._log("Delete links: %s" % self)
        return super(UsMessengerLink, self).unlink()

    @api.model
    def _get_eval_context(self):
        env = self.env

        # delete_my_code_new
        def set_link(
            rel, external_refs, bot_id, sync_date=None, allow_many2many=False, model=None
        ):
            # Works for external links only
            return env["us.messenger.link"]._set_link_external(
                rel, external_refs, bot_id, sync_date, allow_many2many, model
            )

        def search_links(rel, external_refs, bot_id):
            # Works for external links only
            return env["us.messenger.link"]._search_links_external(
                rel, external_refs, bot_id, make_logs=True
            )

        def get_link(rel, ref_info, bot_id, model=None):
            return env["us.messenger.link"]._get_link(rel, ref_info, bot_id, model=model)

        return {
            "set_link": set_link,
            "search_links": search_links,
            "get_link": get_link,
        }
