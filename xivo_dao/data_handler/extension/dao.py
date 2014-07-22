# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql.expression import or_

from xivo_dao.alchemy.extension import Extension as ExtensionSchema
from xivo_dao.data_handler.exception import ElementCreationError
from xivo_dao.data_handler.exception import ElementDeletionError
from xivo_dao.data_handler.exception import ElementEditionError
from xivo_dao.data_handler.exception import ElementNotExistsError
from xivo_dao.data_handler.extension.model import db_converter
from xivo_dao.data_handler.extension.search import extension_search
from xivo_dao.data_handler.utils.search import SearchResult
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.helpers.db_utils import commit_or_abort

DEFAULT_ORDER = ExtensionSchema.exten


@daosession
def get(session, extension_id):
    row = _fetch_extension_row(session, extension_id)
    return db_converter.to_model(row)


def _fetch_extension_row(session, extension_id):
    row = session.query(ExtensionSchema).get(extension_id)
    if not row:
        raise ElementNotExistsError('Extension', id=extension_id)
    return row


@daosession
def get_by_exten_context(session, exten, context):
    res = (session.query(ExtensionSchema)
           .filter(ExtensionSchema.exten == exten)
           .filter(ExtensionSchema.context == context)
           ).first()

    if not res:
        raise ElementNotExistsError('Extension', exten=exten, context=context)

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

    session.begin()
    session.add(extension_row)

    try:
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise ElementCreationError('Extension', e)

    extension.id = extension_row.id

    return extension


@daosession
def edit(session, extension):
    extension_row = _fetch_extension_row(session, extension.id)
    db_converter.update_source(extension_row, extension)

    session.begin()
    session.add(extension_row)

    try:
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise ElementEditionError('Extension', e)


@daosession
def delete(session, extension):
    session.begin()
    try:
        session.query(ExtensionSchema).filter(ExtensionSchema.id == extension.id).delete()
        session.commit()
    except SQLAlchemyError, e:
        session.rollback()
        raise ElementDeletionError('Extension', e)


def _new_query(session, order=None):
    order = order or DEFAULT_ORDER
    return session.query(ExtensionSchema).order_by(order)


@daosession
def associate_destination(session, extension_id, destination, destination_id):
    updated_row = {'type': destination, 'typeval': str(destination_id)}

    with commit_or_abort(session, ElementEditionError, 'Extension'):
        (session.query(ExtensionSchema)
         .filter(ExtensionSchema.id == extension_id)
         .update(updated_row))


@daosession
def dissociate_extension(session, extension_id):
    session.begin()
    (session.query(ExtensionSchema)
     .filter(ExtensionSchema.id == extension_id)
     .update({'type': 'user',
              'typeval': '0'}))

    try:
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise ElementEditionError('Extension', 'error while dissociating extension %d: %s' % (extension_id, e))


@daosession
def get_type_typeval(session, extension_id):
    row = (session.query(ExtensionSchema.type, ExtensionSchema.typeval)
           .filter(ExtensionSchema.id == extension_id)
           .first())

    if not row:
        raise ElementNotExistsError('Extension', id=1)

    return (row.type, row.typeval)
