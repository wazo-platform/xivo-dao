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
import logging
import ldap_dao

from itertools import izip
from sqlalchemy import func
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.alchemy.ctidirectories import CtiDirectories
from xivo_dao.alchemy.ctidirectoryfields import CtiDirectoryFields
from xivo_dao.alchemy.directories import Directories


logger = logging.getLogger(__name__)


NUMBER_TYPE = 'number'


def _format_columns(fields, value):
    if fields == value == [None]:
        return {}

    return dict(izip(fields, value))


@daosession
def get_all_sources(session):
    nonldap_sources = _get_nonldap_sources(session)
    ldap_sources = _get_ldap_sources(session)

    return nonldap_sources + ldap_sources


def _get_ldap_sources(session):
    ldap_cti_directories = session.query(
        CtiDirectories.name,
        CtiDirectories.uri,
        CtiDirectories.match_direct,
        CtiDirectories.match_reverse,
        func.array_agg(CtiDirectoryFields.fieldname).label('fields'),
        func.array_agg(CtiDirectoryFields.value).label('values'),
    ).outerjoin(
        CtiDirectoryFields,
        CtiDirectoryFields.dir_id == CtiDirectories.id
    ).filter(
        CtiDirectories.uri.like('ldapfilter://%%')
    ).group_by(
        CtiDirectories.name,
        CtiDirectories.uri,
        CtiDirectories.match_direct,
        CtiDirectories.match_reverse,
    )

    source_configs = []
    for dir in ldap_cti_directories.all():
        _, _, name = dir.uri.partition('ldapfilter://')
        try:
            ldap_config = ldap_dao.build_ldapinfo_from_ldapfilter(name)
        except LookupError:
            logger.warning('Skipping LDAP source %s', dir.name)
            continue

        custom_filter = ldap_config.get('filter') or ''
        if custom_filter:
            custom_filter = '({})'.format(custom_filter)

        source_configs.append({'type': 'ldap',
                               'name': dir.name,
                               'searched_columns': json.loads(dir.match_direct or '[]'),
                               'first_matched_columns': json.loads(dir.match_reverse or '[]'),
                               'format_columns': _format_columns(dir.fields, dir.values),
                               'ldap_uri': ldap_config['uri'],
                               'ldap_base_dn': ldap_config['basedn'],
                               'ldap_username': ldap_config['username'],
                               'ldap_password': ldap_config['password'],
                               'ldap_custom_filter': custom_filter})

    return source_configs


def _get_nonldap_sources(session):
    sources = session.query(
        CtiDirectories.name,
        CtiDirectories.uri,
        Directories.dirtype,
        CtiDirectories.delimiter,
        CtiDirectories.match_direct,
        CtiDirectories.match_reverse,
        func.array_agg(CtiDirectoryFields.fieldname).label('fields'),
        func.array_agg(CtiDirectoryFields.value).label('values'),
    ).join(
        Directories,
        Directories.uri == CtiDirectories.uri
    ).outerjoin(
        CtiDirectoryFields,
        CtiDirectoryFields.dir_id == CtiDirectories.id
    ).group_by(
        CtiDirectories.name,
        CtiDirectories.uri,
        Directories.dirtype,
        CtiDirectories.delimiter,
        CtiDirectories.match_direct,
        CtiDirectories.match_reverse,
    )

    return [{'name': source.name,
             'type': source.dirtype,
             'uri': source.uri,
             'delimiter': source.delimiter,
             'searched_columns': json.loads(source.match_direct or '[]'),
             'first_matched_columns': json.loads(source.match_reverse or '[]'),
             'format_columns': _format_columns(source.fields, source.values)}
            for source in sources.all()]
