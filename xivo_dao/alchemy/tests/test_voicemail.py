# -*- coding: utf-8 -*-

# Copyright (C) 2016 Proformatique Inc.
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

from hamcrest import assert_that, equal_to

from xivo_dao.tests.test_dao import DAOTestCase


class TestGetOldNumberContext(DAOTestCase):

    def test_when_number_context_are_modified(self):
        voicemail = self.add_voicemail(number='1000', context='default')
        voicemail.number = '1001'
        voicemail.context = 'not_default'

        old_number, old_context = voicemail.get_old_number_context()

        assert_that(old_number, equal_to('1000'))
        assert_that(old_context, equal_to('default'))

    def test_when_only_number_is_modified(self):
        voicemail = self.add_voicemail(number='1000', context='default')
        voicemail.number = '1001'

        old_number, old_context = voicemail.get_old_number_context()

        assert_that(old_number, equal_to('1000'))
        assert_that(old_context, equal_to('default'))

    def test_when_only_context_is_modified(self):
        voicemail = self.add_voicemail(number='1000', context='default')
        voicemail.context = 'not_default'

        old_number, old_context = voicemail.get_old_number_context()

        assert_that(old_number, equal_to('1000'))
        assert_that(old_context, equal_to('default'))
