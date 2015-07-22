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

from itertools import izip
from sqlalchemy import and_, func
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.alchemy import CtiContexts, CtiDirectories, CtiDirectoryFields, CtiDisplays, Directories


logger = logging.getLogger(__name__)


NUMBER_TYPE = 'number'


@daosession
def get_all_sources(session):
    def format_columns(fields, value):
        if fields == value == [None]:
            return {}

        return dict(izip(fields, value))

    sources = session.query(
        CtiDirectories.name,
        CtiDirectories.uri,
        Directories.dirtype,
        CtiDirectories.delimiter,
        CtiDirectories.match_direct,
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
    )

    return [{'name': source.name,
             'type': source.dirtype,
             'uri': source.uri,
             'delimiter': source.delimiter,
             'searched_columns': json.loads(source.match_direct),
             'format_columns': format_columns(source.fields, source.values)}
            for source in sources.all()]


@daosession
def get_directory_headers(session, context):
    attribute_list = _get_attribute_list(session, context)
    header_list = _merge_number_attributes(attribute_list)
    return header_list


def _get_attribute_list(session, context):
    display_filter_json = _get_display_filter_json(session, context)
    if not display_filter_json:
        return []
    display_filter = _display_filter_from_json(display_filter_json)
    attribute_list = _extract_attributes_from_display_filter(display_filter)
    return attribute_list


def _get_display_filter_json(session, context):
    raw_display_data = session.query(
        CtiDisplays.data
    ).filter(
        and_(CtiContexts.name == context,
             CtiContexts.display == CtiDisplays.name)
    ).first()

    if not raw_display_data:
        return ''
    else:
        return raw_display_data.data


def _display_filter_from_json(display_filter_json):
    display_data = json.loads(display_filter_json)
    return display_data


def _extract_attributes_from_display_filter(display_data):
    NAME_INDEX, TYPE_INDEX = 0, 1

    results = []
    indices = sorted(display_data.keys())
    for position in indices:
        entry = display_data[position]
        name = entry[NAME_INDEX]
        field_type = NUMBER_TYPE if entry[TYPE_INDEX].startswith('number_') else entry[TYPE_INDEX]
        pair = name, field_type
        results.append(pair)
    return results


def _merge_number_attributes(attribute_list):
    first_number_type = True
    header_list = []
    for attribute in attribute_list:
        attribute_name, attribute_type = attribute
        if attribute_type == NUMBER_TYPE:
            if first_number_type:
                header_list.append(attribute)
                first_number_type = False
        else:
            header_list.append(attribute)
    return header_list
