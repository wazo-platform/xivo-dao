# -*- coding: utf-8 -*-

# Copyright (C) 2007-2015 Avencall
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
from xivo_dao.alchemy.directories import Directories
from xivo_dao.tests.test_dao import DAOTestCase

from hamcrest import assert_that, equal_to, empty, has_length


class TestDirectoryDAO(DAOTestCase):

    def test_get_all(self):
        configs = [
            {'uri': 'http://localhost:9487', 'dirtype': 'xivo', 'name': 'XiVO'},
            {'uri': 'http://mtl.lan.example.com:9487', 'dirtype': 'xivo', 'name': 'XiVO'},
            {'uri': 'phonebook', 'dirtype': 'phonebook', 'name': 'phonebook'},
            {'uri': 'file:///tmp/test.csv', 'dirtype': 'file', 'name': 'my_csv'},
        ]
        directories = [Directories(**config) for config in configs]
        self.add_me_all(directories)

        results = directory_dao.get_all()

        assert_that(results, has_length(4))
        for config in configs:
            matching_results = [result for result in results
                                if result['uri'] == config['uri'] and result['dirtype'] == config['dirtype']]
            assert_that(matching_results, has_length(1))
            matching_result = matching_results[0]
            assert_that(matching_result['name'], equal_to(config['name']))
            assert_that('id' in matching_result)

    def test_get_all_no_directories(self):
        results = directory_dao.get_all()

        assert_that(results, empty())

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
