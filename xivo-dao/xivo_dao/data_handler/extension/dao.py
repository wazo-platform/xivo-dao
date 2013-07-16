# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Avencall
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

from xivo_dao.alchemy.extension import Extension as ExtensionSchema
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.data_handler.exception import ElementNotExistsError, \
    ElementCreationError, ElementDeletionError
from xivo_dao.data_handler.extension.model import Extension
from sqlalchemy.exc import SQLAlchemyError


@daosession
def get(session, extension_id):
    res = (session.query(ExtensionSchema).filter(ExtensionSchema.id == extension_id)).first()

    if not res:
        raise ElementNotExistsError('Extension', id=extension_id)

    return Extension.from_data_source(res)


@daosession
def get_by_exten_context(session, exten, context):
    res = (_new_query(session)
           .filter(ExtensionSchema.exten == exten)
           .filter(ExtensionSchema.context == context)
    ).first()

    if not res:
        raise ElementNotExistsError('Extension', exten=exten, context=context)

    return Extension.from_data_source(res)


@daosession
def get_by_type_typeval(session, type, typeval):
    res = (_new_query(session)
           .filter(ExtensionSchema.type == type)
           .filter(ExtensionSchema.typeval == typeval)
    ).first()

    if not res:
        raise ElementNotExistsError('Extension', type=type, typeval=typeval)

    return Extension.from_data_source(res)


@daosession
def create(session, extension):
    extension_row = extension.to_data_source(ExtensionSchema)
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
def delete(session, extension):
    session.begin()
    try:
        nb_row_affected = session.query(ExtensionSchema).filter(ExtensionSchema.id == extension.id).delete()
        session.commit()
    except SQLAlchemyError, e:
        session.rollback()
        raise ElementDeletionError('Extension', e)

    if nb_row_affected == 0:
        raise ElementDeletionError('Extension', 'extension_id %s not exsit' % extension.id)

    return nb_row_affected


def _new_query(session):
    return session.query(ExtensionSchema).filter(ExtensionSchema.commented == 0)
