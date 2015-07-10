# -*- coding: utf-8 -*-

# Copyright (C) 2012-2014 Avencall
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
from hamcrest import equal_to
from hamcrest import has_entries
from mock import Mock, patch

from xivo_dao import cti_directories_dao
from xivo_dao.alchemy.ldapfilter import LdapFilter
from xivo_dao.alchemy.ldapserver import LdapServer
from xivo_dao.alchemy.ctidirectories import CtiDirectories
from xivo_dao.alchemy.ctidirectoryfields import CtiDirectoryFields
from xivo_dao.tests.test_dao import DAOTestCase


class TestCtiSheetsDAO(DAOTestCase):

    def test_get_config(self):
        expected_result = {
            "internal": {
                "uri": u"internal",
                "delimiter": "",
                "name": "",
                "match_direct": [
                    u"userfeatures.firstname",
                    u"userfeatures.lastname"
                ],
                "match_reverse": [],
                u"field_firstname": [
                    u"userfeatures.firstname"
                ],
                u"field_lastname": [
                    u"userfeatures.lastname"
                ],
                u"field_phone": [
                    u"linefeatures.number"
                ]
            },
            "xivodir": {
                "uri": u"phonebook",
                "delimiter": "",
                "name": "",
                "match_direct": [
                    u"phonebook.firstname",
                    u"phonebook.lastname",
                    u"phonebook.displayname",
                    u"phonebook.society",
                    u"phonebooknumber.office.number"
                ],
                "match_reverse": [
                    u"phonebooknumber.office.number",
                    u"phonebooknumber.mobile.number"
                ],
                u"field_company": [
                    u"phonebook.society"
                ],
                u"field_firstname": [
                    u"phonebook.firstname"
                ],
                u"field_fullname": [
                    u"phonebook.fullname"
                ],
                u"field_lastname": [
                    u"phonebook.lastname"
                ],
                u"field_mail": [
                    u"phonebook.email"
                ],
                u"field_phone": [
                    u"phonebooknumber.office.number"
                ],
                u"field_reverse": [
                    u"phonebook.fullname"
                ]
            },
            "ldap1": {
                "uri": u"ldapfilter://test-ldap-filter",
                "delimiter": "",
                "name": "",
                "match_direct": [
                    u"cn",
                    u"phoneNumber",
                    u"email"
                ],
                "match_reverse": [],
                u"field_lastname": [
                    u"sn"
                ],
                u"field_mail": [
                    u"email"
                ],
                u"field_phone": [
                    u"telephoneNumber"
                ]
            }
        }

        match_direct = '["userfeatures.firstname","userfeatures.lastname"]'
        ctidirectory = self._insert_ctidirectory('internal', 'internal', match_direct, '')
        self._insert_ctidirectoryfields(ctidirectory.id, 'firstname', 'userfeatures.firstname')
        self._insert_ctidirectoryfields(ctidirectory.id, 'lastname', 'userfeatures.lastname')
        self._insert_ctidirectoryfields(ctidirectory.id, 'phone', 'linefeatures.number')

        match_direct = '["phonebook.firstname","phonebook.lastname","phonebook.displayname","phonebook.society","phonebooknumber.office.number"]'
        match_reverse = '["phonebooknumber.office.number","phonebooknumber.mobile.number"]'
        ctidirectory = self._insert_ctidirectory('xivodir', 'phonebook', match_direct, match_reverse)
        self._insert_ctidirectoryfields(ctidirectory.id, 'company', 'phonebook.society')
        self._insert_ctidirectoryfields(ctidirectory.id, 'firstname', 'phonebook.firstname')
        self._insert_ctidirectoryfields(ctidirectory.id, 'lastname', 'phonebook.lastname')
        self._insert_ctidirectoryfields(ctidirectory.id, 'fullname', 'phonebook.fullname')
        self._insert_ctidirectoryfields(ctidirectory.id, 'mail', 'phonebook.email')
        self._insert_ctidirectoryfields(ctidirectory.id, 'phone', 'phonebooknumber.office.number')
        self._insert_ctidirectoryfields(ctidirectory.id, 'reverse', 'phonebook.fullname')

        match_direct = '["cn","phoneNumber","email"]'
        ldapserver = self._insert_ldapserver('test-ldap-server')
        self._insert_ldapfilter(ldapserver.id, 'test-ldap-filter')

        ctidirectory = self._insert_ctidirectory('ldap1', 'ldapfilter://test-ldap-filter', match_direct, '')
        self._insert_ctidirectoryfields(ctidirectory.id, 'mail', 'email')
        self._insert_ctidirectoryfields(ctidirectory.id, 'lastname', 'sn')
        self._insert_ctidirectoryfields(ctidirectory.id, 'phone', 'telephoneNumber')

        ctidirectory = self._insert_ctidirectory('ldap2', 'ldapfilter://foobar', '', '')

        result = cti_directories_dao.get_config()

        assert_that(result, has_entries(expected_result))

    def test_valid_uri_normal_uri(self):
        uri = "internal"

        valid_uri = cti_directories_dao._valid_uri(uri)

        assert_that(valid_uri, equal_to(True))

    @patch('xivo_dao.ldap_dao.find_ldapfilter_with_name')
    def test_valid_uri_no_server(self, find_ldapfilter_with_name):
        ldap_name = 'test-ldap-filter'
        find_ldapfilter_with_name.return_value = None

        valid_uri = cti_directories_dao._valid_uri("ldapfilter://%s" % ldap_name)

        assert_that(valid_uri, equal_to(False))
        find_ldapfilter_with_name.assert_called_once_with(ldap_name)

    @patch('xivo_dao.ldap_dao.find_ldapserver_with_id')
    @patch('xivo_dao.ldap_dao.find_ldapfilter_with_name')
    def test_valid_uri_with_server(self, find_ldapfilter_with_name, find_ldapserver_with_id):
        ldap_name = 'foo-server'
        ldapserverid = 1
        find_ldapfilter_with_name.return_value = Mock(ldapserverid=ldapserverid)
        find_ldapserver_with_id.return_value = Mock()

        valid_uri = cti_directories_dao._valid_uri("ldapfilter://%s" % ldap_name)
        find_ldapserver_with_id.assert_called_once_with(ldapserverid)

        assert_that(valid_uri, equal_to(True))

    def _insert_ctidirectoryfields(self, dir_id, fieldname, value):
        ctidirectoryfields = CtiDirectoryFields()
        ctidirectoryfields.dir_id = dir_id
        ctidirectoryfields.fieldname = fieldname
        ctidirectoryfields.value = value

        self.add_me(ctidirectoryfields)

    def _insert_ctidirectory(self, name, uri, match_direct, match_reverse):
        ctidirectory = CtiDirectories()
        ctidirectory.name = name
        ctidirectory.uri = uri
        ctidirectory.match_direct = match_direct
        ctidirectory.match_reverse = match_reverse

        self.add_me(ctidirectory)

        return ctidirectory

    def _insert_ldapfilter(self, ldapserver_id, name, user='user', passwd='pass'):
        ldap = LdapFilter()
        ldap.ldapserverid = ldapserver_id
        ldap.name = name
        ldap.user = user
        ldap.passwd = passwd
        ldap.additionaltype = 'office'
        ldap.basedn = 'dc=lan-quebec,dc=avencall,dc=com'
        ldap.description = 'description'

        self.add_me(ldap)

        return ldap

    def _insert_ldapserver(self, name, securitylayer='tls'):
        ldapserver = LdapServer()
        ldapserver.name = name
        ldapserver.host = name
        ldapserver.port = 389
        ldapserver.securitylayer = securitylayer
        ldapserver.protocolversion = '3'
        ldapserver.description = 'description'

        self.add_me(ldapserver)

        return ldapserver
