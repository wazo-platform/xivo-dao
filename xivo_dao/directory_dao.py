# -*- coding: utf-8 -*-
# Copyright 2012-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

import json
import logging
import six

from sqlalchemy import func
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.alchemy.ctidirectories import CtiDirectories
from xivo_dao.alchemy.ctidirectoryfields import CtiDirectoryFields
from xivo_dao.alchemy.directories import Directories
from . import ldap_dao


logger = logging.getLogger(__name__)


NUMBER_TYPE = 'number'


def _format_columns(fields, value):
    if fields == value == [None]:
        return {}

    return dict(six.moves.zip(fields, value))


@daosession
def get_all_sources(session):
    nonldap_sources = _get_nonldap_sources(session)
    ldap_sources = _get_ldap_sources(session)

    return nonldap_sources + ldap_sources


def _get_ldap_sources(session):
    ldap_cti_directories = session.query(
        Directories.ldapfilter_id,
        CtiDirectories.name,
        CtiDirectories.match_direct,
        CtiDirectories.match_reverse,
        func.array_agg(CtiDirectoryFields.fieldname).label('fields'),
        func.array_agg(CtiDirectoryFields.value).label('values'),
    ).join(
        CtiDirectories,
    ).join(
        CtiDirectoryFields,
        CtiDirectoryFields.dir_id == CtiDirectories.id
    ).filter(
        Directories.dirtype == 'ldapfilter',
    ).group_by(
        Directories.ldapfilter_id,
        CtiDirectories.name,
        CtiDirectories.match_direct,
        CtiDirectories.match_reverse,
    )

    source_configs = []
    for dir in ldap_cti_directories.all():
        try:
            ldap_config = ldap_dao.build_ldapinfo_from_ldapfilter(dir.ldapfilter_id)
        except LookupError:
            logger.warning('Skipping LDAP source %s', dir.name)
            continue

        custom_filter = ldap_config.get('filter') or ''.encode('utf8')
        if custom_filter:
            custom_filter = '({})'.format(custom_filter.decode('utf8')).encode('utf8')

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
        Directories.dirtype,
        Directories.xivo_username,
        Directories.xivo_password,
        Directories.auth_key_file,
        Directories.xivo_verify_certificate,
        Directories.xivo_custom_ca_path,
        Directories.dird_tenant,
        Directories.dird_phonebook,
        Directories.uri,
        Directories.auth_backend,
        Directories.auth_host,
        Directories.auth_port,
        Directories.auth_verify_certificate,
        Directories.auth_custom_ca_path,
        CtiDirectories.delimiter,
        CtiDirectories.match_direct,
        CtiDirectories.match_reverse,
        func.array_agg(CtiDirectoryFields.fieldname).label('fields'),
        func.array_agg(CtiDirectoryFields.value).label('values'),
    ).join(
        Directories,
    ).outerjoin(
        CtiDirectoryFields,
        CtiDirectoryFields.dir_id == CtiDirectories.id
    ).filter(
        Directories.dirtype != 'ldapfilter',
    ).group_by(
        CtiDirectories.name,
        Directories.dirtype,
        Directories.xivo_username,
        Directories.xivo_password,
        Directories.auth_key_file,
        Directories.xivo_verify_certificate,
        Directories.xivo_custom_ca_path,
        Directories.dird_tenant,
        Directories.dird_phonebook,
        Directories.uri,
        Directories.auth_backend,
        Directories.auth_host,
        Directories.auth_port,
        Directories.auth_verify_certificate,
        Directories.auth_custom_ca_path,
        CtiDirectories.delimiter,
        CtiDirectories.match_direct,
        CtiDirectories.match_reverse,
    )

    source_configs = []
    for source in sources.all():
        source_config = {
            'name': source.name,
            'type': source.dirtype,
            'uri': source.uri,
            'delimiter': source.delimiter,
            'searched_columns': json.loads(source.match_direct or '[]'),
            'first_matched_columns': json.loads(source.match_reverse or '[]'),
            'format_columns': _format_columns(source.fields, source.values),
        }
        if source.dirtype == 'wazo':
            source_config['xivo_username'] = source.xivo_username
            source_config['xivo_password'] = source.xivo_password
            source_config['auth_key_file'] = source.auth_key_file
            source_config['xivo_verify_certificate'] = source.xivo_verify_certificate
            source_config['xivo_custom_ca_path'] = source.xivo_custom_ca_path
            source_config['auth_host'] = source.auth_host
            source_config['auth_port'] = source.auth_port
            source_config['auth_backend'] = source.auth_backend
            source_config['auth_verify_certificate'] = source.auth_verify_certificate
            source_config['auth_custom_ca_path'] = source.auth_custom_ca_path
        elif source.dirtype == 'dird_phonebook':
            source_config['dird_tenant'] = source.dird_tenant
            source_config['dird_phonebook'] = source.dird_phonebook
        source_configs.append(source_config)

    return source_configs
