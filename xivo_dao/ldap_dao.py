# -*- coding: utf-8 -*-

# Copyright (C) 2012-2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
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

from __future__ import unicode_literals

from xivo_dao.helpers.db_manager import daosession
from xivo_dao.alchemy.ldapfilter import LdapFilter
from xivo_dao.alchemy.ldapserver import LdapServer


@daosession
def build_ldapinfo_from_ldapfilter(session, ldapfilter_id):
    ldap_config = (session.query(LdapFilter.name,
                                 LdapFilter.user,
                                 LdapFilter.passwd,
                                 LdapFilter.basedn,
                                 LdapFilter.filter,
                                 LdapServer.securitylayer,
                                 LdapServer.host,
                                 LdapServer.port)
                   .join(LdapServer,
                         LdapServer.id == LdapFilter.ldapserverid)
                   .filter(LdapFilter.id == ldapfilter_id,
                           LdapFilter.commented == 0,
                           LdapServer.disable == 0)
                   .first())

    if not ldap_config:
        raise LookupError('No ldap config matching filter %s', ldapfilter_id)

    ssl = ldap_config.securitylayer == 'ssl'
    host = ldap_config.host or 'localhost'
    port = ldap_config.port or _determine_default_port(ssl)

    username = ''
    password = ''
    basedn = None
    basefilter = None

    if ldap_config.user:
        username = ldap_config.user.encode('utf8').replace('\\', '\\\\')

    if ldap_config.passwd:
        password = ldap_config.passwd.encode('utf8')

    if ldap_config.basedn:
        basedn = ldap_config.basedn.encode('utf8')

    if ldap_config.filter:
        basefilter = ldap_config.filter.encode('utf8')

    ldapinfo = {'username': username,
                'password': password,
                'basedn': basedn,
                'filter': basefilter,
                'host': host,
                'port': port,
                'ssl': ssl,
                'uri': _build_uri(ssl, host, port)}

    return ldapinfo


def _determine_default_port(ssl):
    if ssl:
        return 636
    return 389


def _build_uri(ssl, host, port):
    scheme = 'ldaps' if ssl else 'ldap'
    return u"%s://%s:%s" % (scheme, host, port)
