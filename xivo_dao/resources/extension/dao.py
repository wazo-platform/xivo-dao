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

from sqlalchemy.sql.expression import or_

from xivo_dao.alchemy.extension import Extension as ExtensionSchema
from xivo_dao.helpers.db_utils import commit_or_abort
from xivo_dao.helpers.db_manager import daosession

from xivo_dao.helpers import errors
from xivo_dao.helpers.exception import DataError
from xivo_dao.resources.extension.database import db_converter, \
    fwd_converter, service_converter, agent_action_converter
from xivo_dao.resources.extension.search import extension_search
from xivo_dao.resources.utils.search import SearchResult

DEFAULT_ORDER = ExtensionSchema.exten


@daosession
def get(session, extension_id):
    row = _fetch_extension_row(session, extension_id)
    return db_converter.to_model(row)


def _fetch_extension_row(session, extension_id):
    row = session.query(ExtensionSchema).get(extension_id)
    if not row:
        raise errors.not_found('Extension', id=extension_id)
    return row


@daosession
def get_by_exten_context(session, exten, context):
    res = (session.query(ExtensionSchema)
           .filter(ExtensionSchema.exten == exten)
           .filter(ExtensionSchema.context == context)
           ).first()

    if not res:
        raise errors.not_found('Extension', exten=exten, context=context)

    return db_converter.to_model(res)


@daosession
def find(session, extension_id):
    extension_row = (session.query(ExtensionSchema)
                     .filter(ExtensionSchema.id == extension_id)
                     .first())

    if not extension_row:
        return None

    return db_converter.to_model(extension_row)


@daosession
def search(session, **parameters):
    rows, total = extension_search.search(session, parameters)

    extensions = _rows_to_extension_model(rows)
    return SearchResult(total, extensions)


@daosession
def find_by_exten(session, exten, order=None):
    search = '%%%s%%' % exten.lower()
    return _find_all_by_search(session, search, order)


@daosession
def find_by_context(session, context, order=None):
    search = '%%%s%%' % context.lower()
    return _find_all_by_search(session, search, order)


@daosession
def find_by_exten_context(session, exten, context):
    extension_row = (session.query(ExtensionSchema)
                     .filter(ExtensionSchema.exten == exten)
                     .filter(ExtensionSchema.context == context)
                     .first())

    if not extension_row:
        return None

    return db_converter.to_model(extension_row)


def get_by_group_id(group_id):
    return get_by_type('group', str(group_id))


def get_by_queue_id(queue_id):
    return get_by_type('queue', str(queue_id))


def get_by_conference_id(queue_id):
    return get_by_type('meetme', str(queue_id))


@daosession
def get_by_type(session, type_, typeval):
    extension_row = (session.query(ExtensionSchema)
                     .filter(ExtensionSchema.type == type_)
                     .filter(ExtensionSchema.typeval == typeval)
                     .first())

    if not extension_row:
        raise errors.not_found('Extension', type=type_, typeval=typeval)

    return db_converter.to_model(extension_row)


def _find_all_by_search(session, search, order):
    line_rows = (_new_query(session, order)
                 .filter(or_(ExtensionSchema.exten.ilike(search),
                             ExtensionSchema.context.ilike(search)))
                 .all())

    return _rows_to_extension_model(line_rows)


def _rows_to_extension_model(extension_rows):
    if not extension_rows:
        return []

    extensions = []
    for extension_row in extension_rows:
        extensions.append(db_converter.to_model(extension_row))

    return extensions


@daosession
def create(session, extension):
    extension_row = db_converter.to_source(extension)
    extension_row.type = 'user'
    extension_row.typeval = '0'

    with commit_or_abort(session, DataError.on_create, 'Extension'):
        session.add(extension_row)

    extension.id = extension_row.id

    return extension


@daosession
def edit(session, extension):
    extension_row = _fetch_extension_row(session, extension.id)
    db_converter.update_source(extension_row, extension)

    with commit_or_abort(session, DataError.on_edit, 'Extension'):
        session.add(extension_row)


@daosession
def delete(session, extension):
    with commit_or_abort(session, DataError.on_delete, 'Extension'):
        session.query(ExtensionSchema).filter(ExtensionSchema.id == extension.id).delete()


def _new_query(session, order=None):
    order = order or DEFAULT_ORDER
    return session.query(ExtensionSchema).order_by(order)


@daosession
def associate_destination(session, extension_id, destination, destination_id):
    with commit_or_abort(session, DataError.on_edit, 'Extension'):
        updated_row = {'type': destination, 'typeval': str(destination_id)}
        (session.query(ExtensionSchema)
         .filter(ExtensionSchema.id == extension_id)
         .update(updated_row))


@daosession
def dissociate_extension(session, extension_id):
    with commit_or_abort(session, DataError.on_edit, 'Extension'):
        (session.query(ExtensionSchema)
         .filter(ExtensionSchema.id == extension_id)
         .update({'type': 'user',
                  'typeval': '0'}))


@daosession
def get_type_typeval(session, extension_id):
    row = (session.query(ExtensionSchema.type, ExtensionSchema.typeval)
           .filter(ExtensionSchema.id == extension_id)
           .first())

    if not row:
        raise errors.not_found('Extension', id=extension_id)

    return (row.type, row.typeval)


@daosession
def find_all_service_extensions(session):
    typevals = service_converter.typevals()
    query = (session.query(ExtensionSchema.id,
                           ExtensionSchema.exten,
                           ExtensionSchema.typeval)
             .filter(ExtensionSchema.type == 'extenfeatures')
             .filter(ExtensionSchema.typeval.in_(typevals))
             )

    return [service_converter.to_model(row) for row in query]


@daosession
def find_all_forward_extensions(session):
    typevals = fwd_converter.typevals()
    query = (session.query(ExtensionSchema.id,
                           ExtensionSchema.exten,
                           ExtensionSchema.typeval)
             .filter(ExtensionSchema.type == 'extenfeatures')
             .filter(ExtensionSchema.typeval.in_(typevals))
             )

    return [fwd_converter.to_model(row) for row in query]


@daosession
def find_all_agent_action_extensions(session):
    typevals = agent_action_converter.typevals()
    query = (session.query(ExtensionSchema.id,
                           ExtensionSchema.exten,
                           ExtensionSchema.typeval)
             .filter(ExtensionSchema.type == 'extenfeatures')
             .filter(ExtensionSchema.typeval.in_(typevals))
             )

    return [agent_action_converter.to_model(row) for row in query]
