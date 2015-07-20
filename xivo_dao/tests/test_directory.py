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
from xivo_dao.alchemy import CtiContexts, CtiDirectories, CtiDirectoryFields, CtiDisplays, Directories
from xivo_dao.tests.test_dao import DAOTestCase

from itertools import chain
from hamcrest import assert_that, contains_inanyorder, empty


class TestDirectorySources(DAOTestCase):

    def setUp(self):
        super(TestDirectorySources, self).setUp()
        self.directory_configs = [
            {'uri': 'http://localhost:9487', 'dirtype': 'xivo', 'name': 'XiVO'},
            {'uri': 'http://mtl.lan.example.com:9487', 'dirtype': 'xivo', 'name': 'XiVO'},
            {'uri': 'phonebook', 'dirtype': 'phonebook', 'name': 'phonebook'},
            {'uri': 'file:///tmp/test.csv', 'dirtype': 'file', 'name': 'my_csv'},
        ]
        self.cti_directory_configs = [
            {'id': 1,
             'name': 'Internal',
             'uri': 'http://localhost:9487',
             'match_direct': '["firstname", "lastname"]'},
            {'id': 2,
             'name': 'mtl',
             'uri': 'http://mtl.lan.example.com:9487',
             'match_direct': '["lastname"]'},
        ]
        self.cti_directory_fields_configs = [
            {'dir_id': 1,
             'fieldname': 'number',
             'value': '{exten}'},
            {'dir_id': 1,
             'fieldname': 'mobile',
             'value': '{mobile_phone_number}'},
            {'dir_id': 2,
             'fieldname': 'number',
             'value': '{exten}'},
            {'dir_id': 2,
             'fieldname': 'mobile',
             'value': '{mobile_phone_number}'},
            {'dir_id': 2,
             'fieldname': 'name',
             'value': '{firstname} {lastname}'},
        ]

    def test_get_all_sources(self):
        directories = [Directories(**config) for config in self.directory_configs]
        cti_directories = [CtiDirectories(**config) for config in self.cti_directory_configs]
        cti_directory_fields = [CtiDirectoryFields(**config) for config in self.cti_directory_fields_configs]
        self.add_me_all(chain(directories, cti_directories, cti_directory_fields))

        result = directory_dao.get_all_sources()

        expected = [
            {'type': 'xivo',
             'name': 'Internal',
             'uri': 'http://localhost:9487',
             'searched_columns': [
                 'firstname',
                 'lastname',
             ],
             'format_columns': {
                 'number': '{exten}',
                 'mobile': '{mobile_phone_number}',
             }},
            {'type': 'xivo',
             'name': 'mtl',
             'uri': 'http://mtl.lan.example.com:9487',
             'searched_columns': [
                 'lastname',
             ],
             'format_columns': {
                 'number': '{exten}',
                 'mobile': '{mobile_phone_number}',
                 'name': '{firstname} {lastname}',
             }}
        ]

        assert_that(result, contains_inanyorder(*expected))

    def test_get_all_sources_no_fields(self):
        directories = [Directories(**config) for config in self.directory_configs]
        cti_directories = [CtiDirectories(**config) for config in self.cti_directory_configs]
        cti_directory_fields = [CtiDirectoryFields(**config) for config in self.cti_directory_fields_configs]
        self.add_me_all(chain(directories, cti_directories, cti_directory_fields[2:]))

        result = directory_dao.get_all_sources()

        expected = [
            {'type': 'xivo',
             'name': 'Internal',
             'uri': 'http://localhost:9487',
             'searched_columns': [
                 'firstname',
                 'lastname',
             ],
             'format_columns': {}},
            {'type': 'xivo',
             'name': 'mtl',
             'uri': 'http://mtl.lan.example.com:9487',
             'searched_columns': [
                 'lastname',
             ],
             'format_columns': {
                 'number': '{exten}',
                 'mobile': '{mobile_phone_number}',
                 'name': '{firstname} {lastname}',
             }}
        ]

        assert_that(result, contains_inanyorder(*expected))

    def test_get_all_sources_no_directories(self):
        results = directory_dao.get_all_sources()

        assert_that(results, empty())


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
