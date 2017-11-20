# -*- coding: utf-8 -*-
# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import six

from hamcrest import assert_that
from hamcrest import has_entries

from xivo_dao import ldap_dao
from xivo_dao.alchemy.ldapfilter import LdapFilter
from xivo_dao.alchemy.ldapserver import LdapServer
from xivo_dao.tests.test_dao import DAOTestCase


class TestLdapDAO(DAOTestCase):

    def test_build_ldapinfo_from_ldapfilter_not_found(self):
        self.assertRaises(LookupError, ldap_dao.build_ldapinfo_from_ldapfilter, 42)

    def test_build_ldapinfo_from_ldapfilter_disabled_filter(self):
        filter_name = 'filtername'
        ldap_server = self._insert_ldapserver(name='ldapserver_test')
        ldap_filter = self._insert_ldapfilter(ldap_server.id, name=filter_name, commented=1)

        self.assertRaises(LookupError, ldap_dao.build_ldapinfo_from_ldapfilter, ldap_filter.id)

    def test_build_ldapinfo_from_ldapfilter_disabled_server(self):
        filter_name = 'filtername'
        ldap_server = self._insert_ldapserver(name='ldapserver_test', disable=1)
        ldap_filter = self._insert_ldapfilter(ldap_server.id, name=filter_name)

        self.assertRaises(LookupError, ldap_dao.build_ldapinfo_from_ldapfilter, ldap_filter.id)

    def test_build_ldapinfo_from_ldapfilter_minimum_fields(self):
        filter_name = 'filtername'
        ldap_server = self._insert_ldapserver(name='ldapserver_test')
        ldap_filter = self._insert_ldapfilter(ldap_server.id, name=filter_name)

        result = ldap_dao.build_ldapinfo_from_ldapfilter(ldap_filter.id)

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

        result = ldap_dao.build_ldapinfo_from_ldapfilter(ldap_filter.id)

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

        result = ldap_dao.build_ldapinfo_from_ldapfilter(ldap_filter.id)

        assert_that(result, has_entries({
            'username': six.b(ldap_filter.user),
            'password': six.b(ldap_filter.passwd),
            'basedn': six.b(ldap_filter.basedn),
            'filter': six.b(ldap_filter.filter),
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
