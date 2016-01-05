# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from xivo_dao import cti_reverse_dao
from xivo_dao.alchemy.ctireversedirectories import CtiReverseDirectories
from xivo_dao.tests.test_dao import DAOTestCase

from hamcrest import assert_that
from hamcrest import equal_to


class TestCTIReverseDAO(DAOTestCase):

    def setUp(self):
        super(TestCTIReverseDAO, self).setUp()
        self.add_directory(name='xivodir', dirtype='xivo')
        self.add_directory(name='internal', dirtype='phonebook')
        reverse = CtiReverseDirectories(
            directories='["xivodir", "ldapdev", "internal"]',
        )
        self.add_me(reverse)

    def test_get_config(self):
        result = cti_reverse_dao.get_config()

        expected = {'sources': [u'xivodir', u'ldapdev', u'internal'],
                    'types': [u'xivo', u'ldap', u'phonebook']}

        assert_that(result, equal_to(expected))
