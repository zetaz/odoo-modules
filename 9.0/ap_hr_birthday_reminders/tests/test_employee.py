# -*- coding: utf-8 -*-
#
# Author: 'Audrius Palenskis audrius.palenskis@gmail.com'
#
from openerp.tests import common


class TestBirthdayEmployees(common.TransactionCase):

    # def test_01_staff_department(self):
    #     staff_dep = self.env['hr.employee'].get_staff_department()
    #     self.assertTrue(staff_dep, 'Administration department does not exist.')

    def test_02_security_groups(self):
        hr_user = self.env.ref('base.group_hr_user')
        hr_manager = self.env.ref('base.group_hr_manager')
        self.assertTrue(hr_user, 'HR user group does not exist.')
        self.assertTrue(hr_manager, 'HR manager group does not exist.')


# TODO add tests for next birthday and next birthday reminder search

