# -*- coding: utf-8 -*-
#
# Author: Audrius Palenskis <audrius.palenskis@gmail.com>
#
from openerp import models, fields, api
from openerp.tools.translate import _
from openerp.exceptions import MissingError
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class ApResPartnerBirthdayReminder(models.Model):
    _inherit = 'res.partner'

    def get_birthday_reminder_partner_list(self):
        return self.env['ap.hr.birthday.reminder.config.settings'].get_reminder_recipients()

    def get_birthday_reminder_mail_template_name(self):
        return 'mail_template_birthday_reminder_template'

    def get_birthday_reminder_email_template(self):
        template = self.env.ref('ap_hr_birthday_reminders.' + self.get_birthday_reminder_mail_template_name())
        if not template:
            raise MissingError(_('Birthday reminder mail template does not exist.'))

        return template

    @api.model
    def send_birthday_reminders(self):
        sent_partners = []

        partners = self.get_birthday_reminder_partner_list()
        if not partners:
            return sent_partners

        hr_obj = self.env['hr.employee']
        birthday_employees = hr_obj.get_birthday_employees()
        if not birthday_employees:
            return sent_partners

        mail_obj = self.env['mail.mail']
        mail_tmpl = self.get_birthday_reminder_email_template()
        mail_tmpl = mail_tmpl.with_context(
            birthday=hr_obj.get_check_birthday_date(),
            employees=birthday_employees.mapped('name'),
        )
        birthday_date = hr_obj.get_check_birthday_date().strftime(DEFAULT_SERVER_DATE_FORMAT)
        employee_names = birthday_employees.mapped('name')
        for partner in partners:
            email = mail_tmpl.generate_email(partner)
            email['body_html'] = self._parse_birthday_email(birthday_date, employee_names, email['body_html'])
            if mail_obj.create(email).send():
                sent_partners.append(partner)

        return sent_partners

    def _parse_birthday_email(self, birthday, employee_names, email_body):
        email_body = email_body.replace('__birthday__', birthday)
        employee_html = '<ol>{}</ol>'.format(''.join(['<li>{}</li>'.format(emp_name) for emp_name in employee_names])) \
            if employee_names else ''
        email_body = email_body.replace('__employees__', employee_html)

        return email_body
