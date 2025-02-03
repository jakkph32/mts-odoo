import base64
import functools
import os
import xml.etree.ElementTree as ET

import requests

from .models.ir_logging import LOG_ERROR


class LogExternalQuery(object):
    """Adds logs before and after external query.
    Can be used for eval context method.
    Example:

        @LogExternalQuery("Viber->send_messages", eval_context)
        def send_messages(to, messages):
            return viber.send_messages(to, messages)
    """

    def __init__(self, target_name, eval_context):
        self.target_name = target_name
        self.log = eval_context["log"]
        self.log_transmission = eval_context["log_transmission"]

    def __call__(self, func):
        @functools.wraps(func)
        def wrap(*args, **kwargs):
            self.log_transmission(
                self.target_name,
                "*%s, **%s"
                % (
                    args,
                    kwargs,
                ),
            )
            try:
                res = func(*args, **kwargs)
            except Exception as err:
                self.log(
                    str(err), name=self.target_name, log_type="data_in", level=LOG_ERROR
                )
                raise
            self.log("RESULT: %s" % res, name=self.target_name, log_type="data_in")
            return res

        return wrap


def url2bin(url, auth=None):
    if not url:
        return None
    r = requests.get(url, auth=auth, timeout=42)
    return r.content


# E.g. to download file and save into in an attachment or Binary field
def url2base64(url):
    content = url2bin(url)
    if not content:
        return None
    return base64.b64encode(content)


def make_update(progenitor):
    env = progenitor.env
    type_messenger = progenitor.eval_context_ids.name
    all_messengers_bots = env['us.messenger.project'].search([('state', 'in', ["new","active_webhook","enabled_webhook"]),
                                                               ('eval_context_ids.name', '=', type_messenger)])
    for b in all_messengers_bots:
        is_developer_code = compare_codes_bots(b, progenitor)
        update_code(b, is_developer_code)
        b.write({'use_custom_code':not is_developer_code})

    update_code(progenitor, True)


def compare_codes_bots(bot, progenitor):
    if bot.common_code != progenitor.common_code:
        return False

    for t in progenitor.task_ids:
        # t1 = bot.env['us.messenger.task'].search([('name','=',t.name), ('project_id', '=', bot.id)])
        # if not t1 or t.code != t1.code:
        #     return False

        for t1 in bot.task_ids:
            if t.code != t1.code:
                return False

    return True


def update_code(bot, is_developer_code):
    name_module = 'us_' + bot.eval_context_ids.name
    file_path = os.path.dirname(__file__)
    replace_path = r"us_messenger"
    if r"us_messenger" not in file_path:
        replace_path = r"us_messenger"
    path = file_path.replace(replace_path,
                             "".join(r"{}/data/us_project_data.xml".format(name_module)))
    tree = ET.parse(path)
    root = tree.getroot()

    update_code_project(bot, root, is_developer_code)

    update_code_task(bot, root, is_developer_code)


def update_code_project(bot, root, is_developer_code):
    code = root.find(".//record[@model='us.messenger.project']").find("field[@name='common_code']").text
    vals = {'common_code': code, 'common_developer_code': code} if is_developer_code else {'common_developer_code': code}
    bot.write(vals)


def update_code_task(bot, root, is_developer_code):
    for t in bot.task_ids:
        records = root.findall(".//record[@model='us.messenger.task']")
        code = None
        for r in records:
            if r.find("field[@name='name']").text == t.name:
                code = r.find("field[@name='developer_code']").text
                break
        if not code:
            continue
        vals = {'code': code, 'developer_code': code} if is_developer_code else {'developer_code': code}
        t.write(vals)
