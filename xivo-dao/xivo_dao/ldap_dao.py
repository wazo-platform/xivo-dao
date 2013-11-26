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


from xivo_dao.helpers.db_manager import daosession, xivo_daosession
from xivo_dao.alchemy.ldapfilter import LdapFilter
from xivo_dao.alchemy.ldapserver import LdapServer


@daosession
def find_ldapfilter_with_name(session, ldap_name):
    return session.query(LdapFilter).filter(LdapFilter.name == ldap_name).first()


@xivo_daosession
def find_ldapserver_with_id(session, ldapserver_id):
    return session.query(LdapServer).filter(LdapServer.id == ldapserver_id).first()


def build_ldapinfo_from_ldapfilter(ldap_filter_name):
    ldapfilter = find_ldapfilter_with_name(ldap_filter_name)
    ldapserver = find_ldapserver_with_id(ldapfilter.ldapserverid)

    ssl = ldapserver.securitylayer == 'ssl'
    host = ldapserver.host or 'localhost'
    port = ldapserver.port or _determine_default_port(ssl)

    username = u''
    password = u''
    basedn = None
    basefilter = None

    if ldapfilter.user:
        username = ldapfilter.user.encode('utf8').replace('\\', '\\\\')

    if ldapfilter.passwd:
        password = ldapfilter.passwd.encode('utf8')

    if ldapfilter.basedn:
        basedn = ldapfilter.basedn.encode('utf8')

    if ldapfilter.filter:
        basefilter = ldapfilter.filter.encode('utf8')

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
