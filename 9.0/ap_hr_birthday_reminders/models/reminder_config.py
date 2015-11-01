# -*- coding: utf-8 -*-
#
# Author: Audrius Palenskis <audrius.palenskis@gmail.com>
#
from openerp import models, fields, api


class ApHrBirthdayReminderConfigSettings(models.TransientModel):
    _name = 'ap.hr.birthday.reminder.config.settings'
    _inherit = 'res.config.settings'

    remind_days_before = fields.Integer('Remind days before', required=True,
                                        default=lambda self: self.get_remind_days_before())
    reminder_recipients = fields.Many2many('res.partner', 'ap_hr_birthday_reminder_recipient_rel',
                                           'reminder_recipients_id', 'partner_reminder_recipients', string='Recipients',
                                           default=lambda self: self.get_reminder_recipients())
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get(None))

    @api.model
    def create(self, values):
        self._save_form_values(values)
        return super(ApHrBirthdayReminderConfigSettings, self).create(values)

    @api.one
    def write(self, values):
        self._save_form_values(values)
        return super(ApHrBirthdayReminderConfigSettings, self).write(values)

    def _save_form_values(self, values):
        remind_days = values.get('remind_days_before')
        reminder_recipient_ids = values.get('reminder_recipients', [])

        if reminder_recipient_ids:
            reminder_recipient_ids = reminder_recipient_ids[0][2]

        self._set_reminder_recipients(reminder_recipient_ids)
        if remind_days:
            self._set_reminder_company_days_before(remind_days)

    @api.one
    def apply_settings(self):
        """
        Dummy form saving trigger
        """
        return True

    def _set_reminder_recipients(self, recipient_ids):
        cfg_model = self.env['ap.hr.birthday.reminder.recipient']
        stored_recs = cfg_model.search([])

        stored_partner_ids = stored_recs.mapped('partner_id.id')
        old_partner_ids = list(set(stored_partner_ids) - set(recipient_ids))
        new_partner_ids = list(set(recipient_ids) - set(stored_partner_ids))

        if old_partner_ids:
            get_old_recs = cfg_model.search([('partner_id', 'in', old_partner_ids)])
            get_old_recs.unlink()

        for partner_id in new_partner_ids:
            cfg_model.create({'partner_id': partner_id})

    def get_remind_days_before(self):
        return self.env['res.company']._company_default_get(None).birthday_remind_days_before

    def get_reminder_recipients(self):
        recipients = self.env['ap.hr.birthday.reminder.recipient'].search([])
        return recipients.mapped('partner_id.id') if recipients else []

    def _set_reminder_company_days_before(self, remind_days):
        self.env.user.company_id.write({
            'birthday_remind_days_before': remind_days,
        })


class ApHrBirthdayReminderRecipients(models.Model):
    _name = 'ap.hr.birthday.reminder.recipient'

    partner_id = fields.Many2one('res.partner', 'Partners')
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get(None))


class ApResCompany(models.Model):
    _inherit = 'res.company'

    birthday_remind_days_before = fields.Integer('Birthday Reminder Days', default=1)
