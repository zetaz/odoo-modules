# -*- coding: utf-8 -*-
#
# Author: Audrius Palenskis <audrius.palenskis@gmail.com>
#
import datetime
from openerp import models, fields, api
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class ApHrEmployeeBirthdayReminder(models.Model):
    _inherit = 'hr.employee'

    birthday_reminders = fields.Boolean('Birthday Reminders', default=True,
                                        help='Include me in birthday reminder program')
    next_birthday_date = fields.Date('Next Birthday', compute='_get_next_birthday_date',
                                     search='_search_next_birthday_date')
    next_birthday_reminder_date = fields.Date('Next Birthday Reminder', compute='_get_next_birthday_reminder_date',
                                              search='_search_next_birthday_reminder_date')

    def get_birthday_employees(self):
        """
        Create list of employees with upcoming birthdays using days before reminder.
        :return: employee list
        :rtype: list
        """
        birthday_employees = []

        employees = self.search([
            ('birthday_reminders', '=', True),
            ('birthday', '!=', False),
        ])
        if not employees:
            return birthday_employees

        return employees.filtered(lambda x: self.check_emp_birthday(x.birthday))

    def check_emp_birthday(self, birthday):
        birthday_date = self.get_check_birthday_date()
        bday_date = datetime.datetime.strptime(birthday, DEFAULT_SERVER_DATE_FORMAT)
        if bday_date.month == birthday_date.month and bday_date.day == birthday_date.day:
            return True

        return False

    def get_staff_department(self):
        return self.env.ref('hr.dep_administration')

    def get_check_birthday_date(self):
        reminder_days = self.env.user.company_id.birthday_remind_days_before
        return datetime.datetime.today().date() + datetime.timedelta(days=reminder_days)

    def _get_next_birthday_date(self):
        for emp in self:
            emp.next_birthday_date = self._calc_next_birthday(emp.birthday) if emp.birthday else None

    def _get_next_birthday_reminder_date(self):
        for emp in self:
            reminder_date = self._calc_next_birthday_reminder_date(emp.birthday) \
                if emp.birthday else None

            emp.next_birthday_reminder_date = reminder_date

    @staticmethod
    def _calc_next_birthday(birthday):
        birthday = datetime.datetime.strptime(birthday, DEFAULT_SERVER_DATE_FORMAT) \
            if isinstance(birthday, str) else birthday
        today = datetime.date.today()
        year = today.year
        if (today.month > birthday.month) or (
                        today.month == birthday.month and today.day > birthday.day):
            year += 1

        return datetime.date(year, birthday.month, birthday.day)

    def _calc_next_birthday_reminder_date(self, birthday):
        birthday = datetime.datetime.strptime(birthday, DEFAULT_SERVER_DATE_FORMAT) \
            if isinstance(birthday, str) else birthday
        next_birthday = self._calc_next_birthday(birthday)
        reminder_days = self.env.user.company_id.birthday_remind_days_before
        reminder_date = next_birthday - datetime.timedelta(days=reminder_days)
        return reminder_date

    @api.model
    def _search_next_birthday_date(self, operator, operand):
        filtered_ids = []
        all_recs = self.search([])
        if operator == '=':
            filtered_recs = all_recs.filtered(lambda x: x.birthday and self._calc_next_birthday(x.birthday).strftime(
                DEFAULT_SERVER_DATE_FORMAT) == operand)
            filtered_ids = filtered_recs.ids

        return [('id', 'in', filtered_ids)]

    @api.model
    def _search_next_birthday_reminder_date(self, operator, operand):
        filtered_ids = []
        all_recs = self.search([])
        if operator == '=':
            filtered_recs = all_recs.filtered(
                lambda x: x.birthday and self._calc_next_birthday_reminder_date(x.birthday).strftime(
                              DEFAULT_SERVER_DATE_FORMAT) == operand)
            print filtered_recs
            filtered_ids = filtered_recs.ids
        return [('id', 'in', filtered_ids)]
