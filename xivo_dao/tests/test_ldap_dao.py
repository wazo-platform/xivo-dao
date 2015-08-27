# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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
from hamcrest import has_entries

from xivo_dao import ldap_dao
from xivo_dao.alchemy.ldapfilter import LdapFilter
from xivo_dao.alchemy.ldapserver import LdapServer
from xivo_dao.tests.test_dao import DAOTestCase


class TestLdapDAO(DAOTestCase):

    def test_find_ldapserver_with_id(self):
        ldapserver = self._insert_ldapserver(name='ldapserver_test')

        ldapserver_result = ldap_dao.find_ldapserver_with_id(ldapserver.id)

        self.assertEqual(ldapserver.id, ldapserver_result.id)

    def test_find_ldapfilter_with_name(self):
        ldapserver = self._insert_ldapserver(name='ldapserver_test')
        ldapfilter = self._insert_ldapfilter(ldapserver.id, name='ldapfilter_test')

        ldapfilter_result = ldap_dao.find_ldapfilter_with_name(ldapfilter.name)

        self.assertEqual(ldapfilter.name, ldapfilter_result.name)

    def test_build_ldapinfo_from_ldapfilter_not_found(self):
        self.assertRaises(LookupError, ldap_dao.build_ldapinfo_from_ldapfilter, 'unknown')

    def test_build_ldapinfo_from_ldapfilter_disabled_filter(self):
        filter_name = 'filtername'
        ldap_server = self._insert_ldapserver(name='ldapserver_test')
        ldap_filter = self._insert_ldapfilter(ldap_server.id, name=filter_name, commented=1)

        self.assertRaises(LookupError, ldap_dao.build_ldapinfo_from_ldapfilter, ldap_filter.name)

    def test_build_ldapinfo_from_ldapfilter_disabled_server(self):
        filter_name = 'filtername'
        ldap_server = self._insert_ldapserver(name='ldapserver_test', disable=1)
        ldap_filter = self._insert_ldapfilter(ldap_server.id, name=filter_name)

        self.assertRaises(LookupError, ldap_dao.build_ldapinfo_from_ldapfilter, ldap_filter.name)

    def test_build_ldapinfo_from_ldapfilter_minimum_fields(self):
        filter_name = 'filtername'
        ldap_server = self._insert_ldapserver(name='ldapserver_test')
        ldap_filter = self._insert_ldapfilter(ldap_server.id, name=filter_name)

        result = ldap_dao.build_ldapinfo_from_ldapfilter(ldap_filter.name)

        assert_that(result, has_entries({
            'username': '',
            'password': '',
            'basedn': None,
            'filter': None,
            'host': 'localhost',
            'port': 389,
            'ssl': False,
            'uri': 'ldap://localhost:389'
        }))

    def test_build_ldapinfo_from_ldapfilter_ssl(self):
        filter_name = 'filtername'
        ldap_server = self._insert_ldapserver(name='ldapserver_test', securitylayer='ssl', port=636)
        ldap_filter = self._insert_ldapfilter(ldap_server.id, name=filter_name)

        result = ldap_dao.build_ldapinfo_from_ldapfilter(ldap_filter.name)

        assert_that(result, has_entries({
            'username': '',
            'password': '',
            'basedn': None,
            'filter': None,
            'host': 'localhost',
            'port': 636,
            'ssl': True,
            'uri': 'ldaps://localhost:636'
        }))

    def test_build_ldapinfo_from_ldapfilter_all_fields(self):
        ldap_server = self._insert_ldapserver(name='ldapserver_test',
                                              securitylayer='ssl',
                                              host='myhost',
                                              port=1234)
        ldap_filter = self._insert_ldapfilter(ldap_server.id,
                                              user='username',
                                              passwd='password',
                                              basedn='cn=User,dc=company,dc=com',
                                              filter='sn=*')

        result = ldap_dao.build_ldapinfo_from_ldapfilter(ldap_filter.name)

        assert_that(result, has_entries({
            'username': ldap_filter.user,
            'password': ldap_filter.passwd,
            'basedn': ldap_filter.basedn,
            'filter': ldap_filter.filter,
            'host': ldap_server.host,
            'port': ldap_server.port,
            'ssl': True,
            'uri': 'ldaps://%s:%s' % (ldap_server.host, ldap_server.port)
        }))

    def _insert_ldapfilter(self, ldapserver_id, **kwargs):
        ldap = LdapFilter()
        ldap.ldapserverid = ldapserver_id
        ldap.name = kwargs.get('name', None)
        ldap.user = kwargs.get('user', None)
        ldap.passwd = kwargs.get('passwd', None)
        ldap.basedn = kwargs.get('basedn', None)
        ldap.filter = kwargs.get('filter', None)
        ldap.additionaltype = kwargs.get('additionaltype', 'office')
        ldap.description = kwargs.get('description', '')
        ldap.commented = kwargs.get('commented', '0')

        self.add_me(ldap)

        return ldap

    def _insert_ldapserver(self, name, **kwargs):
        ldapserver = LdapServer()
        ldapserver.name = name
        ldapserver.host = kwargs.get('host', None)
        ldapserver.port = kwargs.get('port', 389)
        ldapserver.securitylayer = kwargs.get('securitylayer', None)
        ldapserver.protocolversion = kwargs.get('protocolversion', None)
        ldapserver.description = kwargs.get('description', '')
        ldapserver.disable = kwargs.get('disable', '0')

        self.add_me(ldapserver)

        return ldapserver
