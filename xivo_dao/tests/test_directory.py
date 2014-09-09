# -*- coding: utf-8 -*-

# Copyright (C) 2007-2014 Avencall
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

from xivo_dao import directory_dao
from xivo_dao.alchemy.cti_contexts import CtiContexts
from xivo_dao.alchemy.cti_displays import CtiDisplays
from xivo_dao.tests.test_dao import DAOTestCase


class TestDirectoryDAO(DAOTestCase):

    def test_get_directory_headers(self):
        display_name = 'mydisplay'
        context_name = 'myctx'

        cti_contexts = CtiContexts(
            name=context_name,
            directories='myldapdir',
            display=display_name
        )
        cti_display = CtiDisplays(
            name=display_name,
            data='{ "10": [ "Name","name","","{db-name}" ],"20": [ "Number","number_office","","{db-number}" ],"30": [ "Location","","","{db-location}" ] }'
        )

        self.add_me_all([cti_display, cti_contexts])

        result = directory_dao.get_directory_headers(context_name)
        expected_result = [
            ('Name', 'name'),
            ('Number', 'number'),
            ('Location', '')
        ]

        self.assertEquals(result, expected_result)

    def test_get_directory_headers_unknown_context(self):
        context_name = 'myctx'

        result = directory_dao.get_directory_headers(context_name)

        self.assertEqual(result, [], 'Should return an empty list')

    def test_get_directory_headers_many_number_fields(self):
        display_name = 'mydisplay'
        context_name = 'myctx'

        cti_contexts = CtiContexts(
            name=context_name,
            directories='myldapdir',
            display=display_name
        )
        cti_display = CtiDisplays(
            name=display_name,
            data='{ "10": [ "Name","name","","{db-name}" ],"20": [ "Number","number_office","","{db-number}" ],"30": [ "Location","","","{db-location}" ], "40": [ "Number","number_mobile","","{db-mobile}" ] }'
        )

        self.add_me_all([cti_display, cti_contexts])

        result = directory_dao.get_directory_headers(context_name)
        expected_result = [
            ('Name', 'name'),
            ('Number', 'number'),
            ('Location', '')
        ]

        self.assertEqual(result, expected_result)
