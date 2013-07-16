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


import uuid

from sqlalchemy import Integer
from sqlalchemy.sql import and_, cast
from sqlalchemy.exc import SQLAlchemyError
from xivo_dao.alchemy.linefeatures import LineFeatures as LineSchema
from xivo_dao.alchemy.usersip import UserSIP as UserSIPSchema
from xivo_dao.alchemy.useriax import UserIAX as UserIAXSchema
from xivo_dao.alchemy.usercustom import UserCustom as UserCustomSchema
from xivo_dao.alchemy.sccpline import SCCPLine as SCCPLineSchema
from xivo_dao.alchemy.user_line import UserLine as UserLineSchema
from xivo_dao.alchemy.extension import Extension
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.data_handler.exception import ElementNotExistsError, \
    ElementDeletionError, ElementCreationError

from model import LineSIP, LineIAX, LineSCCP, LineCUSTOM


@daosession
def get(session, line_id):
    line = session.query(LineSchema).filter(LineSchema.id == line_id).first()

    if not line:
        raise ElementNotExistsError('Line', line_id=line_id)

    return _get_protocol_line(line)


@daosession
def get_by_user_id(session, user_id):
    line = (
        _new_query(session)
        .filter(UserLineSchema.user_id == user_id)
        .filter(UserLineSchema.line_id == LineSchema.id)
    ).first()

    if not line:
        raise ElementNotExistsError('Line', user_id=user_id)

    return _get_protocol_line(line)


@daosession
def get_by_number_context(session, number, context):
    line = (
        _new_query(session)
        .join((Extension,
               and_(Extension.type == 'user',
                    LineSchema.id == cast(Extension.typeval, Integer))))
        .filter(Extension.exten == number)
        .filter(Extension.context == context)
    ).first()

    if not line:
        raise ElementNotExistsError('Line', number=number, context=context)

    return _get_protocol_line(line)


def _get_protocol_line(line):
    protocol = line.protocol.lower()
    if protocol == 'sip':
        return LineSIP.from_data_source(line)
    elif protocol == 'iax':
        return LineIAX.from_data_source(line)
    elif protocol == 'sccp':
        return LineSCCP.from_data_source(line)
    elif protocol == 'custom':
        return LineCUSTOM.from_data_source(line)


@daosession
def is_exist_provisioning_id(session, provd_id):
    line = session.query(LineSchema.id).filter(LineSchema.provisioningid == provd_id).count()
    if line > 0:
        return True
    return False


@daosession
def create(session, line):
    session.begin()
    protocol = line.protocol.lower()
    if protocol == 'sip':
        proto = _create_sip_line(session, line)
    elif protocol == 'iax':
        proto = _create_iax_line(session, line)
    elif protocol == 'sccp':
        proto = _create_sccp_line(session, line)
    elif protocol == 'custom':
        proto = _create_custom_line(session, line)

    try:
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise ElementCreationError('Line', e)

    session.begin()
    line.protocolid = proto.id
    line_row = line.to_data_source(LineSchema)
    session.add(line_row)

    _create_extension(session, line)

    try:
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise ElementCreationError('Line', e)

    line.id = line_row.id

    return line


def _create_extension(session, line):
    exten = Extension()
    exten.exten = line.number
    exten.context = line.context
    exten.type = 'user'
    session.add(exten)


def _create_sip_line(session, line):
    if not hasattr(line, 'username'):
        uid = uuid.uuid4()
        line.username = uid.hex

    if not hasattr(line, 'secret'):
        uid = uuid.uuid4()
        line.secret = uid.hex

    line.name = line.username

    line_row = line.to_data_source(UserSIPSchema)

    line_row.name = line.username
    line_row.type = 'friend'

    session.add(line_row)

    return line_row


def _create_iax_line(session, line):
    raise NotImplementedError


def _create_sccp_line(session, line):
    raise NotImplementedError


def _create_custom_line(session, line):
    raise NotImplementedError


@daosession
def delete(session, line):
    session.begin()
    try:
        nb_row_affected = session.query(LineSchema).filter(LineSchema.id == line.id).delete()
        _delete_line(session, line)
        _delete_extension(session, line.number, line.context)
        session.commit()
    except SQLAlchemyError, e:
        session.rollback()
        raise ElementDeletionError('Line', e)

    if nb_row_affected == 0:
        raise ElementDeletionError('Line', 'line_id %s not exsit' % line.id)

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


def _delete_extension(session, exten, context):
    (session.query(Extension).filter(and_(Extension.exten == exten,
                                          Extension.context == context))
                             .delete())


def _delete_sip_line(session, protocolid):
    session.query(UserSIPSchema).filter(UserSIPSchema.id == protocolid).delete()


def _delete_iax_line(session, protocolid):
    session.query(UserIAXSchema).filter(UserIAXSchema.id == protocolid).delete()


def _delete_sccp_line(session, protocolid):
    session.query(SCCPLineSchema).filter(SCCPLineSchema.id == protocolid).delete()


def _delete_custom_line(session, protocolid):
    session.query(UserCustomSchema).filter(UserCustomSchema.id == protocolid).delete()


def _new_query(session):
    return session.query(LineSchema).filter(LineSchema.commented == 0)
