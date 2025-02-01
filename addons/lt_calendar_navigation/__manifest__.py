##############################################################################
# Copyright (c) 2022 lumitec GmbH (https://www.lumitec.solutions)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################
{
    'name': 'Direct Navigate to Client from Appointment',
    'summary': 'One-Click Feature to Address Navigation and Route Planning ',
    'author': "lumitec GmbH",
    'website': "https://www.lumitec.solutions",
    'category': 'Extra Tools',
    'version': '18.0.1.0.0',
    'license': 'OPL-1',
    'images': ['static/description/thumbnail.png'],
    'depends': [
        'base',
        'calendar',
    ],
    'data': [],
    'assets': {
        'web.assets_backend': [
            'lt_calendar_navigation/static/src/xml/web_calendar.xml',
            'lt_calendar_navigation/static/src/js/calendar_popover.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
