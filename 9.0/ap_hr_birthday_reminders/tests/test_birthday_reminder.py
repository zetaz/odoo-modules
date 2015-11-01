# -*- coding: utf-8 -*-
#
# Author: Audrius Palenskis <audrius.palenskis@gmail.com>
#
import datetime
import logging
from openerp.tests import common
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

_logger = logging.getLogger(__name__)

try:
    from freezegun import freeze_time
except ImportError:
    freeze_time = None
    _logger.exception("Library missing. pip install freezegun")
    raise


class TestBirthdayEmployees(common.TransactionCase):
    old_today_date1 = '2012-01-01'
    old_today_date2 = '2014-05-11'

    def setUp(self):
        super(TestBirthdayEmployees, self).setUp()

        self.reminder_days = 2
        old_date1 = datetime.datetime.strptime(self.old_today_date1, DEFAULT_SERVER_DATE_FORMAT)
        self.included_date = old_date1 + datetime.timedelta(days=self.reminder_days)
        self.not_included_date = old_date1 + datetime.timedelta(days=self.reminder_days + 1)

        # TODO add date checks for leap years
        # employees
        self.emp1 = self.env['hr.employee'].create({
            'name': 'Employee 1',
            'birthday': self.included_date.strftime(DEFAULT_SERVER_DATE_FORMAT),
        })
        self.emp2 = self.env['hr.employee'].create({
            'name': 'Employee 2',
            'birthday': self.not_included_date.strftime(DEFAULT_SERVER_DATE_FORMAT),
        })
        # partners
        self.partner1 = self.env['res.partner'].create({
            'name': 'Partner 1',
            'is_company': True,
            'email': 'email1@odoo.local'
        })
        self.assertTrue(self.partner1, 'Failed create Partner 1')

        self.partner2 = self.env['res.partner'].create({
            'name': 'Partner 2',
            'is_company': True,
            'email': 'email2@odoo.local'
        })
        self.assertTrue(self.partner1, 'Failed create Partner 2')

        self.partner3 = self.env['res.partner'].create({
            'name': 'Partner 3',
            'is_company': False,
            'email': 'email3@odoo.local'
        })
        self.assertTrue(self.partner1, 'Failed create Partner 3')

        # configured recipient list
        self.recipient_list = [self.partner1.id, self.partner2.id]
        self.env['ap.hr.birthday.reminder.config.settings']._set_reminder_recipients(self.recipient_list)
        # reminder days
        self.env.user.company_id.write({'birthday_remind_days_before': self.reminder_days})

    @freeze_time(old_today_date1)
    def test_01_test_time_mockup_date1(self):
        old_date = datetime.datetime.strptime(self.old_today_date1, DEFAULT_SERVER_DATE_FORMAT).date()
        today = datetime.date.today()
        self.assertEqual(today, old_date, "Failed to mock up {} date.".format(self.old_today_date1))

    @freeze_time(old_today_date2)
    def test_02_test_time_mockup_date2(self):
        old_date = datetime.datetime.strptime(self.old_today_date2, DEFAULT_SERVER_DATE_FORMAT).date()
        today = datetime.date.today()
        self.assertEqual(today, old_date, "Failed to mock up {} date.".format(self.old_today_date2))

    def test_10_recipient_list(self):
        recipients = self.env['res.partner'].get_birthday_reminder_partner_list()
        self.assertEqual(sorted(self.recipient_list), sorted(recipients), 'Recipient list is incorrect.')

    @freeze_time(old_today_date1)
    def test_11_employee_list(self):
        employees = self.env['hr.employee'].get_birthday_employees()
        self.assertEqual(1, len(employees), 'Employee list is incorrect.')
        self.assertEqual('Employee 1', employees[0].name, 'Incorrect employees.')

    @freeze_time(old_today_date2)
    def test_12_employee_list(self):
        employees = self.env['hr.employee'].get_birthday_employees()
        self.assertEqual(0, len(employees), 'Employee list is incorrect.')

    def test_13_reminder_email_template(self):
        template = self.env['res.partner'].get_birthday_reminder_email_template()
        template_name = self.env['res.partner'].get_birthday_reminder_mail_template_name()
        model_rec = self.env['ir.model.data'].search([
            ('module', '=', 'ap_hr_birthday_reminders'),
            ('name', '=', template_name)])

        self.assertEqual(template.id, model_rec.res_id, 'Incorrect birthday reminder mail template.')

    @freeze_time(old_today_date1)
    def test_20_check_reminder_sending_with_date1(self):
        sent_partners = self.env['res.partner'].send_birthday_reminders()
        self.assertEqual(2, len(sent_partners), 'Incorrect reminder sent partner list.')

    @freeze_time(old_today_date2)
    def test_30_check_reminder_sending_with_date2(self):
        sent_partners = self.env['res.partner'].send_birthday_reminders()
        self.assertEqual(0, len(sent_partners), 'Incorrect reminder sent partner list.')
