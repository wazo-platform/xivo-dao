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

import string
import random

from sqlalchemy.sql import and_
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from xivo_dao.alchemy.linefeatures import LineFeatures as LineSchema
from xivo_dao.alchemy.usersip import UserSIP as UserSIPSchema, UserSIP
from xivo_dao.alchemy.useriax import UserIAX as UserIAXSchema, UserIAX
from xivo_dao.alchemy.usercustom import UserCustom as UserCustomSchema, \
    UserCustom
from xivo_dao.alchemy.sccpline import SCCPLine as SCCPLineSchema, SCCPLine
from xivo_dao.alchemy.user_line import UserLine as UserLineSchema
from xivo_dao.alchemy.extension import Extension
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.data_handler.exception import ElementNotExistsError, \
    ElementDeletionError, ElementCreationError
from model import LineSIP, LineIAX, LineSCCP, LineCUSTOM
from xivo_dao.data_handler.line.model import LineOrdering


DEFAULT_ORDER = [LineOrdering.name, LineOrdering.context]


@daosession
def get(session, line_id):
    line = _new_query(session).filter(LineSchema.id == line_id).first()

    if not line:
        raise ElementNotExistsError('Line', line_id=line_id)

    return _join_line_protocol(line)


@daosession
def get_by_user_id(session, user_id):
    line = (
        _new_query(session)
        .join(UserLineSchema, and_(UserLineSchema.user_id == user_id,
                                   UserLineSchema.line_id == LineSchema.id,
                                   UserLineSchema.main_line == True,
                                   UserLineSchema.main_user == True))
        .first())

    if not line:
        raise ElementNotExistsError('Line', user_id=user_id)

    return _join_line_protocol(line)


@daosession
def get_by_number_context(session, number, context):
    line = (
        _new_query(session)
        .join(Extension, and_(Extension.exten == number,
                              Extension.context == context))
        .join(UserLineSchema, and_(UserLineSchema.extension_id == Extension.id,
                                   LineSchema.id == UserLineSchema.line_id,
                                   UserLineSchema.main_line == True,
                                   UserLineSchema.main_user == True))
    ).first()

    if not line:
        raise ElementNotExistsError('Line', number=number, context=context)

    return _join_line_protocol(line)


@daosession
def find_all(session, order=None):
    line_rows = _new_query(session, order).all()

    return _rows_to_line_model(line_rows)


@daosession
def find_all_by_protocol(session, protocol, order=None):
    line_rows = (_new_query(session, order)
                 .filter(LineSchema.protocol == protocol.lower())
                 .all())

    return _rows_to_line_model(line_rows)


@daosession
def find_all_by_name(session, name, order=None):
    search = '%%%s%%' % name.lower()

    line_rows = (_new_query(session, order)
                 .filter(LineSchema.name.ilike(search))
                 .all())

    return _rows_to_line_model(line_rows)


@daosession
def find_all_by_device_id(session, device_id, order=None):
    line_rows = (_new_query(session, order)
                 .filter(LineSchema.device == str(device_id))
                 .all())

    return _rows_to_line_model(line_rows)


def _rows_to_line_model(line_rows):
    if not line_rows:
        return []

    lines = []
    for line_row in line_rows:
        lines.append(_join_line_protocol(line_row))

    return lines


def _join_line_protocol(line):
    protocol = line.protocol.lower()
    protocol_row = _get_protocol_row(line)

    if protocol == 'sip':
        line_protocol = LineSIP.from_data_source(line)
        line_protocol.update_from_data_source(protocol_row)
    elif protocol == 'iax':
        line_protocol = LineIAX.from_data_source(line)
        line_protocol.update_from_data_source(protocol_row)
    elif protocol == 'sccp':
        line_protocol = LineSCCP.from_data_source(line)
        line_protocol.update_from_data_source(protocol_row)
    elif protocol == 'custom':
        line_protocol = LineCUSTOM.from_data_source(line)
        line_protocol.update_from_data_source(protocol_row)
        line_protocol.name = protocol_row.interface

    return line_protocol


@daosession
def _get_protocol_row(session, line):
    protocol = line.protocol.lower()
    if protocol == 'sip':
        row = session.query(UserSIP).filter(line.protocolid == UserSIP.id).first()
    elif protocol == 'iax':
        row = session.query(UserIAX).filter(line.protocolid == UserIAX.id).first()
    elif protocol == 'sccp':
        row = session.query(SCCPLine).filter(line.protocolid == SCCPLine.id).first()
    elif protocol == 'custom':
        row = session.query(UserCustom).filter(line.protocolid == UserCustom.id).first()

    if not row:
        raise ElementNotExistsError('Line %s' % protocol, id=line.protocolid)

    return row


@daosession
def provisioning_id_exists(session, provd_id):
    line = session.query(LineSchema.id).filter(LineSchema.provisioningid == provd_id).count()
    if line > 0:
        return True
    return False


@daosession
def create(session, line):
    derived_line = _build_derived_line(session, line)

    session.begin()
    session.add(derived_line)

    try:
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise ElementCreationError('Line', e)
    except IntegrityError as e:
        session.rollback()
        raise ElementCreationError('Line', e)

    session.begin()
    line_row = _build_line_row(line, derived_line)
    session.add(line_row)

    try:
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise ElementCreationError('Line', e)

    line.id = line_row.id

    return line


def _build_derived_line(session, line):
    protocol = line.protocol.lower()

    if protocol == 'sip':
        derived_line = _create_sip_line(session, line)
    elif protocol == 'iax':
        derived_line = _create_iax_line(line)
    elif protocol == 'sccp':
        derived_line = _create_sccp_line(line)
    elif protocol == 'custom':
        derived_line = _create_custom_line(line)

    return derived_line


def _build_line_row(line, derived_line):
    line.protocolid = derived_line.id
    line_row = line.to_data_source(LineSchema)
    if line_row.configregistrar is None:
        line_row.configregistrar = 'default'
    return line_row


def _create_sip_line(session, line):
    if not hasattr(line, 'username'):
        line.username = generate_random_hash(session, UserSIPSchema.name)

    if not hasattr(line, 'secret'):
        line.secret = generate_random_hash(session, UserSIPSchema.secret)

    line.name = line.username
    line_row = line.to_data_source(UserSIPSchema)

    line_row.name = line.username
    line_row.username = ''
    line_row.type = 'friend'
    if line_row.category is None:
        line_row.category = 'user'  # enum: (user,trunk)

    return line_row


def generate_random_hash(session, column):
    token = _random_hash()
    query = session.query(column)

    count = query.filter(column == token).count()
    while count > 0:
        token = _random_hash()
        count = query.filter(column == token).count()

    return token


def _random_hash(length=8):
    pool = string.ascii_letters + string.digits
    return ''.join(random.choice(pool) for _ in range(length))


def _create_iax_line(line):
    raise NotImplementedError


def _create_sccp_line(line):
    raise NotImplementedError


def _create_custom_line(line):
    raise NotImplementedError


@daosession
def delete(session, line):
    session.begin()
    try:
        nb_row_affected = session.query(LineSchema).filter(LineSchema.id == line.id).delete()
        _delete_line(session, line)
        session.commit()
    except SQLAlchemyError, e:
        session.rollback()
        raise ElementDeletionError('Line', e)

    if nb_row_affected == 0:
        raise ElementDeletionError('Line', 'line_id %s not exist' % line.id)

    return nb_row_affected


def _delete_line(session, line):
    protocolid = int(line.protocolid)
    protocol = line.protocol.lower()
    if protocol == 'sip':
        _delete_sip_line(session, protocolid)
    elif protocol == 'iax':
        _delete_iax_line(session, protocolid)
    elif protocol == 'sccp':
        _delete_sccp_line(session, protocolid)
    elif protocol == 'custom':
        _delete_custom_line(session, protocolid)


def _delete_sip_line(session, protocolid):
    session.query(UserSIPSchema).filter(UserSIPSchema.id == protocolid).delete()


def _delete_iax_line(session, protocolid):
    session.query(UserIAXSchema).filter(UserIAXSchema.id == protocolid).delete()


def _delete_sccp_line(session, protocolid):
    session.query(SCCPLineSchema).filter(SCCPLineSchema.id == protocolid).delete()


def _delete_custom_line(session, protocolid):
    session.query(UserCustomSchema).filter(UserCustomSchema.id == protocolid).delete()


def _new_query(session, order=None):
    order = order or DEFAULT_ORDER
    return session.query(LineSchema).filter(LineSchema.commented == 0).order_by(*order)


@daosession
def associate_extension(session, extension, line_id):
    line_row = (session.query(LineSchema)
                .filter(LineSchema.id == line_id)
                .first())

    if line_row:
        line_row.number = extension.exten
        line_row.context = extension.context

        session.begin()
        session.add(line_row)
        session.commit()


@daosession
def unassociate_extension(session, extension):
    line_row = (session.query(LineSchema)
                .filter(LineSchema.number == extension.exten)
                .filter(LineSchema.context == extension.context)
                .first())

    if line_row:
        line_row.number = ''
        line_row.context = ''
        line_row.provisioningid = 0

        session.begin()
        session.add(line_row)
        session.commit()
