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

from xivo_dao.alchemy.context import Context as ContextSchema
from xivo_dao.alchemy.extension import Extension as ExtensionSchema
from xivo_dao.alchemy.contextnumbers import ContextNumbers as ContextNumberSchema
from xivo_dao.resources.context.converters import context_converter
from xivo_dao.resources.context.converters import range_converter
from xivo_dao.resources.entity import dao as entity_dao
from xivo_dao.helpers.db_utils import flush_session
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.helpers import errors


@daosession
def find(session, context_name):
    row = (session.query(ContextSchema)
           .filter(ContextSchema.name == context_name)
           .first())

    return context_converter.to_model(row) if row else None


def get(context_name):
    context = find(context_name)

    if not context:
        raise errors.not_found('Context', name=context_name)

    return context


@daosession
def find_by_extension_id(session, extension_id):
    context_row = (session.query(ContextSchema)
                   .join(ExtensionSchema, ExtensionSchema.context == ContextSchema.name)
                   .filter(ExtensionSchema.id == extension_id)
                   .first())

    if not context_row:
        return None

    return context_converter.to_model(context_row)


def get_by_extension_id(extension_id):
    context = find_by_extension_id(extension_id)

    if not context:
        raise errors.not_found('Context', extension_id=extension_id)

    return context


@daosession
def create(session, context):
    context_row = context_converter.to_source(context)
    context_row.entity = entity_dao.default_entity_name()

    with flush_session(session):
        session.add(context_row)

    return context


@daosession
def find_all_context_ranges(session, context_name):
    rows = (session.query(
        ContextNumberSchema.numberbeg,
        ContextNumberSchema.numberend,
        ContextNumberSchema.didlength)
        .filter(ContextNumberSchema.context == context_name)
        .all())

    return [range_converter.to_model(row) for row in rows]


@daosession
def find_all_specific_context_ranges(session, context_name, context_range):
    rows = (session.query(
        ContextNumberSchema.numberbeg,
        ContextNumberSchema.numberend,
        ContextNumberSchema.didlength)
        .filter(ContextNumberSchema.context == context_name)
        .filter(ContextNumberSchema.type == context_range)
        .all())

    return [range_converter.to_model(row) for row in rows]
