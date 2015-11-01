# -*- coding: utf-8 -*-
#
# Author: Audrius Palenskis <audrius.palenskis@gmail.com>
#
{
    'name': "Employee Birthday Reminders",
    'summary': """Employee birthday reminders""",
    'description': """
* Next employee birthday, next birthday's remind date in employee forms.
* Birthday reminder recipient configuration
* Email template for sending birthday reminders.
* Daily cron job for sending reminders

    """,
    'author': "Audrius Palenskis",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '0.1',

    'depends': [
        'base',
        'base_setup',
        'mail',
        'resource',
        'web_kanban',
        'web_tip',
        'hr',
    ],

    'data': [
        'views/hr_employee.xml',
        'views/reminder_config.xml',
        'data/reminder_mail_template.xml',
        'data/reminder_cron.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
    ],
    'demo': [
    ],
}
