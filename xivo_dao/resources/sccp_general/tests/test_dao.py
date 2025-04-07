# Copyright 2017-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


from hamcrest import assert_that, contains_exactly, contains_inanyorder, empty

from xivo_dao.alchemy.sccpgeneralsettings import SCCPGeneralSettings
from xivo_dao.tests.test_dao import DAOTestCase

from .. import dao as sccp_general_dao


class TestFindAll(DAOTestCase):
    def test_find_all_no_sccp_general(self):
        result = sccp_general_dao.find_all()

        assert_that(result, empty())

    def test_find_all(self):
        row1 = self.add_sccp_general_settings()
        row2 = self.add_sccp_general_settings()

        sccp_general = sccp_general_dao.find_all()

        assert_that(sccp_general, contains_inanyorder(row1, row2))


class TestEditAll(DAOTestCase):
    def test_edit_all(self):
        row1 = SCCPGeneralSettings(option_name='setting1', option_value='value1')
        row2 = SCCPGeneralSettings(option_name='setting2', option_value='value1')

        sccp_general_dao.edit_all([row1, row2])

        sccp_general = sccp_general_dao.find_all()
        assert_that(sccp_general, contains_inanyorder(row1, row2))

    def test_delete_old_entries(self):
        self.add_sccp_general_settings()
        self.add_sccp_general_settings()
        row = SCCPGeneralSettings(option_name='nat', option_value='value1')

        sccp_general_dao.edit_all([row])

        sccp_general = sccp_general_dao.find_all()
        assert_that(sccp_general, contains_exactly(row))
