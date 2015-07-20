# -*- coding: utf-8 -*-

# Copyright (C) 2012-2015 Avencall
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
from xivo_dao import ldap_dao
from xivo_dao.alchemy import CtiDirectories, CtiDirectoryFields, Directories


@daosession
def get_config(session):
    res = {}
    ctidirectories = _find_valid_directories(session)
    for directory in ctidirectories:

        dird_match_direct = json.loads(directory.match_direct) if directory.match_direct else []
        dird_match_reverse = json.loads(directory.match_reverse) if directory.match_reverse else []

        dir_id = directory.name
        res[dir_id] = {}
        res[dir_id]['uri'] = directory.uri
        res[dir_id]['type'] = directory.dirtype
        res[dir_id]['delimiter'] = directory.delimiter if directory.delimiter else ''
        res[dir_id]['name'] = directory.description if directory.description else ''
        res[dir_id]['match_direct'] = dird_match_direct
        res[dir_id]['match_reverse'] = dird_match_reverse

        directoryfields = _build_directoryfields(directory.id)
        res[dir_id].update(directoryfields)

    return res


def _find_valid_directories(session):
    ctidirectories = session.query(
        CtiDirectories.id,
        CtiDirectories.uri,
        CtiDirectories.name,
        CtiDirectories.delimiter,
        CtiDirectories.description,
        CtiDirectories.match_direct,
        CtiDirectories.match_reverse,
        Directories.dirtype,
    ).outerjoin(
        Directories,
        Directories.uri == CtiDirectories.uri
    )
    valid = []

    for directory in ctidirectories.all():
        if not _valid_uri(directory.uri):
            continue

        if not directory.dirtype:
            directory.dirtype = 'ldap'

        valid.append(directory)

    return valid


def _valid_uri(uri):
    if not uri.startswith('ldapfilter://'):
        return True

    ldap_name = uri.replace('ldapfilter://', '', 1)
    ldap_filter = ldap_dao.find_ldapfilter_with_name(ldap_name)
    if not ldap_filter:
        return False

    ldap_server = ldap_dao.find_ldapserver_with_id(ldap_filter.ldapserverid)
    return ldap_server is not None


@daosession
def _build_directoryfields(session, dir_id):
    ctidirectoryfields = session.query(CtiDirectoryFields).filter(CtiDirectoryFields.dir_id == dir_id).all()

    res = {}
    if ctidirectoryfields:
        for field in ctidirectoryfields:
            dir_key = 'field_%s' % field.fieldname
            res[dir_key] = [field.value]
    return res
