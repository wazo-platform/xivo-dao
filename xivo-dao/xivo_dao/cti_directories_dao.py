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


import json
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.alchemy.ctidirectories import CtiDirectories
from xivo_dao.alchemy.ctidirectoryfields import CtiDirectoryFields
from xivo_dao import ldap_dao


@daosession
def get_config(session):
    res = {}
    ctidirectories = session.query(CtiDirectories).all()
    for directory in ctidirectories:
        uri = _build_uri(directory.uri)
        if uri is None:
            continue

        dird_match_direct = json.loads(directory.match_direct) if directory.match_direct else []
        dird_match_reverse = json.loads(directory.match_reverse) if directory.match_reverse else []

        dir_id = directory.name
        res[dir_id] = {}
        res[dir_id]['uri'] = uri
        res[dir_id]['delimiter'] = directory.delimiter if directory.delimiter else ''
        res[dir_id]['name'] = directory.description if directory.description else ''
        res[dir_id]['match_direct'] = dird_match_direct
        res[dir_id]['match_reverse'] = dird_match_reverse

        directoryfields = _build_directoryfields(directory.id)
        res[dir_id].update(directoryfields)

    return res


def _build_uri(uri):
    if uri.startswith('ldapfilter://'):
        ldap_name = uri.replace('ldapfilter://', '')
        return _build_ldap_uri(ldap_name)
    else:
        return uri


def _build_ldap_uri(ldap_name):
    ldapfilter = ldap_dao.get_ldapfilter_with_name(ldap_name)
    if ldapfilter is None:
        return None

    ldapserver = ldap_dao.get_ldapserver_with_id(ldapfilter.ldapserverid)
    if ldapserver is None:
        return None

    secure = 'ldaps' if ldapserver.securitylayer == 'ssl' else 'ldap'
    uri = '%s://%s:%s@%s:%s/%s???%s' % (secure,
                                        ldapfilter.user or '',
                                        ldapfilter.passwd or '',
                                        ldapserver.host,
                                        ldapserver.port,
                                        ldapfilter.basedn,
                                        ldapfilter.filter)
    return uri


@daosession
def _build_directoryfields(session, dir_id):
    ctidirectoryfields = session.query(CtiDirectoryFields).filter(CtiDirectoryFields.dir_id == dir_id).all()

    res = {}
    if ctidirectoryfields:
        for field in ctidirectoryfields:
            dir_key = 'field_%s' % field.fieldname
            res[dir_key] = [field.value]
    return res
