# -*- coding: utf-8 -*-
# Copyright 2007-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

import six

from xivo_dao import directory_dao
from xivo_dao.alchemy.ctidirectories import CtiDirectories
from xivo_dao.alchemy.ctidirectoryfields import CtiDirectoryFields
from xivo_dao.alchemy.directories import Directories
from xivo_dao.alchemy.ldapserver import LdapServer
from xivo_dao.alchemy.ldapfilter import LdapFilter
from xivo_dao.tests.test_dao import DAOTestCase

from hamcrest import assert_that, contains_inanyorder, empty


class TestDirectoryLdapSources(DAOTestCase):

    def setUp(self):
        super(TestDirectoryLdapSources, self).setUp()
        ldap_server = LdapServer(
            name='myldap',
            host='myldap.example.com',
            port=636,
            securitylayer='ssl',
            protocolversion='3',
        )
        self.add_me(ldap_server)
        ldap_filter_1 = LdapFilter(
            ldapserverid=ldap_server.id,
            name='thefilter',
            user='cn=admin,dc=example,dc=com',
            passwd='53c8e7',
            basedn='dc=example,dc=com',
        )
        self.add_me(ldap_filter_1)
        ldap_filter_2 = LdapFilter(
            ldapserverid=ldap_server.id,
            name='secondfilter',
            user='cn=admin,dc=example,dc=com',
            passwd='53c8e7',
            basedn='dc=example,dc=com',
            filter='l=Québec',
        )
        self.add_me(ldap_filter_2)
        directory_1 = Directories(
            name='ldap_1',
            dirtype='ldapfilter',
            ldapfilter_id=ldap_filter_1.id,
        )
        self.add_me(directory_1)
        directory_2 = Directories(
            name='ldap_2',
            dirtype='ldapfilter',
            ldapfilter_id=ldap_filter_2.id,
        )
        self.add_me(directory_2)
        self.cti_directory_1 = CtiDirectories(
            name='ldapdirectory_1',
            match_direct='["cn"]',
            match_reverse='["telephoneNumber"]',
            directory_id=directory_1.id,
        )
        self.add_me(self.cti_directory_1)
        self.cti_directory_2 = CtiDirectories(
            name='ldapdirectory_2',
            match_direct='["cn"]',
            match_reverse='["telephoneNumber"]',
            directory_id=directory_2.id,
        )
        self.add_me(self.cti_directory_2)
        fields = {'firstname': '{givenName}',
                  'lastname': '{sn}',
                  'number': '{telephoneNumber}'}
        for name, column in six.iteritems(fields):
            self.add_me(CtiDirectoryFields(dir_id=self.cti_directory_1.id,
                                           fieldname=name,
                                           value=column))
            self.add_me(CtiDirectoryFields(dir_id=self.cti_directory_2.id,
                                           fieldname=name,
                                           value=column))

        self.expected_result_1 = {
            'type': 'ldap',
            'name': 'ldapdirectory_1',
            'ldap_uri': 'ldaps://myldap.example.com:636',
            'ldap_base_dn': 'dc=example,dc=com'.encode('utf8'),
            'ldap_username': 'cn=admin,dc=example,dc=com'.encode('utf8'),
            'ldap_password': '53c8e7'.encode('utf8'),
            'ldap_custom_filter': ''.encode('utf8'),
            'searched_columns': ['cn'],
            'first_matched_columns': ['telephoneNumber'],
            'format_columns': {
                'firstname': '{givenName}',
                'lastname': '{sn}',
                'number': '{telephoneNumber}',
            }}
        self.expected_result_2 = {
            'type': 'ldap',
            'name': 'ldapdirectory_2',
            'ldap_uri': 'ldaps://myldap.example.com:636',
            'ldap_base_dn': 'dc=example,dc=com'.encode('utf8'),
            'ldap_username': 'cn=admin,dc=example,dc=com'.encode('utf8'),
            'ldap_password': '53c8e7'.encode('utf8'),
            'ldap_custom_filter': '(l=Québec)'.encode('utf8'),
            'searched_columns': ['cn'],
            'first_matched_columns': ['telephoneNumber'],
            'format_columns': {
                'firstname': '{givenName}',
                'lastname': '{sn}',
                'number': '{telephoneNumber}',
            }}

    def test_get_all_sources(self):
        result = directory_dao.get_all_sources()

        expected = [self.expected_result_1, self.expected_result_2]

        assert_that(result, contains_inanyorder(*expected))

    def test_that_a_missing_ldap_config_does_not_break_get_all_sources(self):
        directory_with_no_matching_config = CtiDirectories(
            name='brokenldap',
            match_direct='["cn"]',
            match_reverse='["telephoneNumber"]',
            directory_id=None,
        )
        self.add_me(directory_with_no_matching_config)

        result = directory_dao.get_all_sources()

        expected = [self.expected_result_1, self.expected_result_2]

        assert_that(result, contains_inanyorder(*expected))

    def test_ldap_with_no_direct_match(self):
        self.cti_directory_1.match_direct = ''

        result = directory_dao.get_all_sources()

        expected_result_1 = dict(self.expected_result_1)
        expected_result_1['searched_columns'] = []
        expected = [expected_result_1, self.expected_result_2]

        assert_that(result, contains_inanyorder(*expected))

    def test_ldap_with_no_reverse_match(self):
        self.cti_directory_1.match_reverse = ''

        result = directory_dao.get_all_sources()

        expected_result_1 = dict(self.expected_result_1)
        expected_result_1['first_matched_columns'] = []
        expected = [expected_result_1, self.expected_result_2]

        assert_that(result, contains_inanyorder(*expected))


class TestDirectoryNonLdapSources(DAOTestCase):

    def setUp(self):
        super(TestDirectoryNonLdapSources, self).setUp()
        dir_1 = {
            'uri': 'https://localhost:9486',
            'dirtype': 'xivo',
            'name': 'XiVO',
            'xivo_username': 'foo',
            'xivo_password': 'bar',
            'auth_backend': 'wazo_user',
            'auth_host': 'localhost',
            'auth_port': 9497,
            'auth_verify_certificate': True,
            'auth_custom_ca_path': '/custom/ca/path',
            'xivo_verify_certificate': True,
            'xivo_custom_ca_path': '/custom/ca/path',
        }
        dir_2 = {
            'uri': 'https://mtl.lan.example.com:9486',
            'dirtype': 'xivo',
            'name': 'XiVO',
            'xivo_username': 'test',
            'xivo_password': 'test',
            'auth_backend': 'xivo_service',
            'auth_host': 'mtl.lan.example.com',
            'auth_port': 9497,
            'auth_verify_certificate': True,
            'auth_custom_ca_path': None,
            'xivo_verify_certificate': True,
            'xivo_custom_ca_path': None,
        }
        dir_3 = {
            'uri': 'phonebook',
            'dirtype': 'phonebook',
            'name': 'phonebook',
        }
        dir_4 = {
            'uri': 'file:///tmp/test.csv',
            'dirtype': 'file',
            'name': 'my_csv',
        }
        dir_5 = {
            'uri': 'postgresql://',
            'dirtype': 'dird_phonebook',
            'name': 'dird',
            'dird_tenant': 'tenant',
            'dird_phonebook': 'thephonebook',
        }

        self.directory_configs = [dir_1, dir_2, dir_3, dir_4, dir_5]

        d1, d2, _, d4, d5 = directories = [Directories(**config) for config in self.directory_configs]
        self.add_me_all(directories)
        self.cti_directory_configs = [
            {'name': 'Internal',
             'directory_id': d1.id,
             'match_direct': '["firstname", "lastname"]',
             'match_reverse': '["exten"]'},
            {'name': 'mtl',
             'directory_id': d2.id,
             'match_direct': '',
             'match_reverse': '[]'},
            {'name': 'acsvfile',
             'directory_id': d4.id,
             'match_direct': '["firstname", "lastname"]',
             'match_reverse': '["exten"]',
             'delimiter': '|'},
            {'name': 'mydirdphonebook',
             'directory_id': d5.id,
             'match_direct': '',
             'match_reverse': '[]'},
        ]
        c1, c2, c3, c4 = cti_directories = [CtiDirectories(**config) for config in self.cti_directory_configs]
        self.add_me_all(cti_directories)
        self.cti_directory_fields_configs = [
            {'dir_id': c1.id,
             'fieldname': 'number',
             'value': '{exten}'},
            {'dir_id': c1.id,
             'fieldname': 'mobile',
             'value': '{mobile_phone_number}'},
            {'dir_id': c2.id,
             'fieldname': 'number',
             'value': '{exten}'},
            {'dir_id': c2.id,
             'fieldname': 'mobile',
             'value': '{mobile_phone_number}'},
            {'dir_id': c2.id,
             'fieldname': 'name',
             'value': '{firstname} {lastname}'},
            {'dir_id': c3.id,
             'fieldname': 'name',
             'value': '{firstname} {lastname}'},
            {'dir_id': c4.id,
             'fieldname': 'name',
             'value': '{firstname} {lastname}'},
        ]

        self.expected_result_1 = {
            'type': 'xivo',
            'name': 'Internal',
            'uri': 'https://localhost:9486',
            'xivo_username': 'foo',
            'xivo_password': 'bar',
            'auth_backend': 'wazo_user',
            'auth_verify_certificate': True,
            'auth_custom_ca_path': '/custom/ca/path',
            'xivo_verify_certificate': True,
            'xivo_custom_ca_path': '/custom/ca/path',
            'auth_host': 'localhost',
            'auth_port': 9497,
            'delimiter': None,
            'searched_columns': [
                'firstname',
                'lastname',
            ],
            'first_matched_columns': ['exten'],
            'format_columns': {
                'number': '{exten}',
                'mobile': '{mobile_phone_number}',
            }}

        self.expected_result_2 = {
            'type': 'xivo',
            'name': 'mtl',
            'uri': 'https://mtl.lan.example.com:9486',
            'xivo_username': 'test',
            'xivo_password': 'test',
            'auth_backend': 'xivo_service',
            'auth_host': 'mtl.lan.example.com',
            'auth_port': 9497,
            'xivo_verify_certificate': True,
            'xivo_custom_ca_path': None,
            'auth_verify_certificate': True,
            'auth_custom_ca_path': None,
            'delimiter': None,
            'searched_columns': [],
            'first_matched_columns': [],
            'format_columns': {
                'number': '{exten}',
                'mobile': '{mobile_phone_number}',
                'name': '{firstname} {lastname}',
            }}

        self.expected_result_3 = {
            'type': 'file',
            'name': 'acsvfile',
            'uri': 'file:///tmp/test.csv',
            'delimiter': '|',
            'searched_columns': [
                'firstname',
                'lastname',
            ],
            'first_matched_columns': ['exten'],
            'format_columns': {
                'name': '{firstname} {lastname}',
            }}

        self.expected_result_4 = {
            'type': 'dird_phonebook',
            'name': 'mydirdphonebook',
            'uri': 'postgresql://',
            'dird_tenant': 'tenant',
            'dird_phonebook': 'thephonebook',
            'searched_columns': [],
            'first_matched_columns': [],
            'format_columns': {'name': '{firstname} {lastname}'},
            'delimiter': None,
        }

    def test_get_all_sources(self):
        cti_directory_fields = [CtiDirectoryFields(**config) for config in self.cti_directory_fields_configs]
        self.add_me_all(cti_directory_fields)

        result = directory_dao.get_all_sources()

        assert_that(result, contains_inanyorder(self.expected_result_1,
                                                self.expected_result_2,
                                                self.expected_result_3,
                                                self.expected_result_4))

    def test_get_all_sources_no_fields(self):
        cti_directory_fields = [CtiDirectoryFields(**config) for config in self.cti_directory_fields_configs]
        self.add_me_all(cti_directory_fields[2:])

        result = directory_dao.get_all_sources()

        expected_result_1 = dict(self.expected_result_1)
        expected_result_1['format_columns'] = {}
        expected = [expected_result_1, self.expected_result_2, self.expected_result_3, self.expected_result_4]

        assert_that(result, contains_inanyorder(*expected))


class TestDirectoryNoSources(DAOTestCase):

    def test_get_all_sources_no_directories(self):
        results = directory_dao.get_all_sources()

        assert_that(results, empty())
