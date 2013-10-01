# -*- coding: utf-8 -*-

# Copyright (C) 2012-2013 Avencall
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
from xivo_dao import cti_directories_dao
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.alchemy.ldapfilter import LdapFilter
from xivo_dao.alchemy.ldapserver import LdapServer
from xivo_dao.alchemy.ctidirectories import CtiDirectories
from xivo_dao.alchemy.ctidirectoryfields import CtiDirectoryFields


class TestCtiSheetsDAO(DAOTestCase):

    tables = [LdapServer, LdapFilter, CtiDirectories, CtiDirectoryFields]

    def setUp(self):
        self.empty_tables()

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
                "uri": u"ldap://user:pass@test-ldap-server:389/dc=lan-quebec,dc=avencall,dc=com???",
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

        ldapserver = self._insert_ldapserver('test-ldap-server')
        self._insert_ldapfilter(ldapserver.id, 'test-ldap-filter')

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
        ctidirectory = self._insert_ctidirectory('ldap1', 'ldapfilter://test-ldap-filter', match_direct, '')
        self._insert_ctidirectoryfields(ctidirectory.id, 'mail', 'email')
        self._insert_ctidirectoryfields(ctidirectory.id, 'lastname', 'sn')
        self._insert_ctidirectoryfields(ctidirectory.id, 'phone', 'telephoneNumber')

        match_direct = '["cn","phoneNumber","email"]'
        ctidirectory = self._insert_ctidirectory('ldap2', 'ldapfilter://foobar', '', '')

        result = cti_directories_dao.get_config()

        assert_that(result, equal_to(expected_result))

    def test_build_ldap_uri_no_server(self):
        ldap_name = 'test-ldap-filter'
        self._insert_ldapfilter(42, ldap_name)

        ldap_uri = cti_directories_dao._build_ldap_uri(ldap_name)

        self.assertEqual(ldap_uri, None)

    def test_build_ldap_uri_no_username_no_passwd(self):
        ldap_server = self._insert_ldapserver('foo-server', securitylayer=None)
        ldap_filter = self._insert_ldapfilter(ldap_server.id, 'foo-filter', user=None, passwd=None)

        uri = cti_directories_dao._build_ldap_uri(ldap_filter.name)

        expected_uri = 'ldap://:@%s:%s/%s???' % (ldap_server.host, ldap_server.port, ldap_filter.basedn)
        self.assertEqual(expected_uri, uri)

    def _insert_ctidirectoryfields(self, dir_id, fieldname, value):
        ctidirectoryfields = CtiDirectoryFields()
        ctidirectoryfields.dir_id = dir_id
        ctidirectoryfields.fieldname = fieldname
        ctidirectoryfields.value = value

        self.session.begin()
        self.session.add(ctidirectoryfields)
        self.session.commit()

    def _insert_ctidirectory(self, name, uri, match_direct, match_reverse):
        ctidirectory = CtiDirectories()
        ctidirectory.name = name
        ctidirectory.uri = uri
        ctidirectory.match_direct = match_direct
        ctidirectory.match_reverse = match_reverse

        self.session.begin()
        self.session.add(ctidirectory)
        self.session.commit()

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

        self.session.begin()
        self.session.add(ldap)
        self.session.commit()

        return ldap

    def _insert_ldapserver(self, name, securitylayer='tls'):
        ldapserver = LdapServer()
        ldapserver.name = name
        ldapserver.host = name
        ldapserver.port = 389
        ldapserver.securitylayer = securitylayer
        ldapserver.protocolversion = '3'
        ldapserver.description = 'description'

        self.session.begin()
        self.session.add(ldapserver)
        self.session.commit()

        return ldapserver
