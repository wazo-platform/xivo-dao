# -*- coding: utf-8 -*-
# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import unicode_literals

from hamcrest import assert_that
from hamcrest import equal_to

from xivo_dao import cti_reverse_dao
from xivo_dao.alchemy.ctireversedirectories import CtiReverseDirectories
from xivo_dao.tests.test_dao import DAOTestCase


class TestCTIReverseDAO(DAOTestCase):

    def setUp(self):
        super(TestCTIReverseDAO, self).setUp()
        self.add_directory(name='xivodir', dirtype='xivo')
        self.add_directory(name='internal', dirtype='phonebook')

    def test_get_config(self):
        reverse = CtiReverseDirectories(
            directories='["xivodir", "ldapdev", "internal"]',
        )
        self.add_me(reverse)

        result = cti_reverse_dao.get_config()

        expected = {'sources': ['xivodir', 'ldapdev', 'internal'],
                    'types': ['xivo', 'ldap', 'phonebook']}

        assert_that(result, equal_to(expected))

    def test_get_config_when_no_reverse_are_selected(self):
        empty_result = {'sources': [], 'types': []}

        result = cti_reverse_dao.get_config()
        assert_that(result, equal_to(empty_result))

        self.add_me(CtiReverseDirectories(directories=''))

        result = cti_reverse_dao.get_config()
        assert_that(result, equal_to(empty_result))

        self.add_me(CtiReverseDirectories(directories='[]'))

        result = cti_reverse_dao.get_config()
        assert_that(result, equal_to(empty_result))
