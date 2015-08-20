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

from hamcrest import assert_that, equal_to
from xivo_dao import cti_displays_dao
from xivo_dao.alchemy.cti_displays import CtiDisplays
from xivo_dao.tests.test_dao import DAOTestCase


class TestCTIDisplaysDAO(DAOTestCase):

    def test_get_config(self):
        display_configs = [
            ('switchboard', '{ "10": [ "", "status", "", ""],"20": [ "Name", "name", "", "{db-firstname} {db-lastname}"],"30": [ "Number", "number_office", "", "{db-phone}"]}'),
            ('Display', '{ "10": [ "Firstname", "", "", "{db-firstname}"],"20": [ "Lastname", "", "", "{db-lastname}"],"30": [ "Number", "", "", "{db-number}"] }'),
        ]
        for config in display_configs:
            display = CtiDisplays(
                name=config[0],
                data=config[1],
            )
            self.add_me(display)

        result = cti_displays_dao.get_config()

        expected = {'switchboard': {'10': ['', 'status', '', ''],
                                    '20': ['Name', 'name', '', '{db-firstname} {db-lastname}'],
                                    '30': ['Number', 'number_office', '', '{db-phone}']},
                    'Display': {'10': ['Firstname', '', '', '{db-firstname}'],
                                '20': ['Lastname', '', '', '{db-lastname}'],
                                '30': ['Number', '', '', '{db-number}']}}

        assert_that(result, equal_to(expected))
