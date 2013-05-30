# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

from hamcrest import assert_that
from hamcrest.core import equal_to
from xivo_dao.alchemy.linefeatures import LineFeatures as LineSchema
from xivo_dao.dao import line_dao
from xivo_dao.models.line import Line
from xivo_dao.tests.test_dao import DAOTestCase


class TestGetLineDao(DAOTestCase):

    tables = [LineSchema]

    def setUp(self):
        self.empty_tables()

    def test_get_by_user_id_no_line(self):
        self.assertRaises(LookupError, line_dao.get_line_by_user_id, 666)

    def test_get_by_user_id(self):
        user_id = 123
        properties = {
            'iduserfeatures': user_id,
            'number': '1001',
            'context': 'notdefault',
            'name': 'sdklfj',
            'protocolid': 123,
            'provisioningid': 543,
        }
        self.add_me(LineSchema(**properties))

        expected_line = Line.from_user_data(properties)

        line = line_dao.get_line_by_user_id(user_id)

        assert_that(line, equal_to(expected_line))

    def test_get_by_user_id_commented(self):
        user_id = 123
        properties = {
            'iduserfeatures': user_id,
            'number': '1001',
            'context': 'notdefault',
            'name': 'sdklfj',
            'protocolid': 123,
            'provisioningid': 543,
            'commented': 1,
        }
        self.add_me(LineSchema(**properties))

        self.assertRaises(LookupError, line_dao.get_line_by_user_id, user_id)

    def test_get_by_number_context_no_line(self):
        self.assertRaises(LookupError, line_dao.get_line_by_number_context, '1234', 'default')

    def test_get_by_number_context(self):
        number, context = '1235', 'notdefault'
        properties = {
            'iduserfeatures': 1234,
            'number': number,
            'context': context,
            'name': 'sdklfj',
            'protocolid': 123,
            'provisioningid': 543,
        }
        self.add_me(LineSchema(**properties))

        expected_line = Line.from_user_data(properties)

        line = line_dao.get_line_by_number_context(number, context)

        assert_that(line, equal_to(expected_line))

    def test_get_by_number_context_commented(self):
        number, context = '1235', 'notdefault'
        properties = {
            'iduserfeatures': 1234,
            'number': number,
            'context': context,
            'name': 'sdklfj',
            'protocolid': 123,
            'provisioningid': 543,
            'commented': 1,
        }
        self.add_me(LineSchema(**properties))

        self.assertRaises(LookupError, line_dao.get_line_by_number_context, number, context)
