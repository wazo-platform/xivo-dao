# -*- coding: utf-8 -*-
# Copyright (C) 2013-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy import and_

from xivo import caller_id
from xivo.asterisk import protocol_interface

from xivo_dao.alchemy.extension import Extension as ExtensionSchema
from xivo_dao.alchemy.line_extension import LineExtension
from xivo_dao.alchemy.linefeatures import LineFeatures as LineSchema
from xivo_dao.alchemy.sccpline import SCCPLine
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.usercustom import UserCustom
from xivo_dao.alchemy.userfeatures import UserFeatures as UserSchema
from xivo_dao.alchemy.useriax import UserIAX
from xivo_dao.alchemy.usersip import UserSIP

from xivo_dao.helpers.db_manager import daosession
from xivo_dao.line_dao import get_protocol


@daosession
def find_line_id_by_user_id(session, user_id):
    res = (session.query(LineSchema)
           .join(UserLine, and_(UserLine.user_id == int(user_id),
                                UserLine.line_id == LineSchema.id)))
    return [line.id for line in res]


@daosession
def get_main_exten_by_line_id(session, line_id):
    res = (session.query(ExtensionSchema.exten)
           .join(LineExtension, and_(LineExtension.extension_id == ExtensionSchema.id,
                                     LineExtension.line_id == int(line_id),
                                     LineExtension.main_extension == True))  # noqa
           .first())
    if res is None:
        raise LookupError('Could not get a extension for line %s', line_id)
    else:
        return res.exten


@daosession
def get_main_exten_by_user_id(session, user_id):
    res = (session.query(ExtensionSchema.exten)
           .join(UserLine, and_(UserLine.user_id == int(user_id),
                                UserLine.main_line == True))  # noqa
           .join(LineExtension, and_(LineExtension.extension_id == ExtensionSchema.id,
                                     LineExtension.line_id == UserLine.line_id,
                                     LineExtension.main_extension == True))
           .first())
    if res is None:
        raise LookupError('Could not get a extension for user %s', user_id)
    else:
        return res.exten


@daosession
def get_line_identity_by_user_id(session, user_id):
    row = (session.query(LineSchema.protocol,
                         LineSchema.name)
           .join(UserLine, and_(UserLine.line_id == LineSchema.id,
                                UserLine.user_id == int(user_id),
                                UserLine.main_user == True,  # noqa
                                UserLine.main_line == True))
           .first())
    if not row:
        raise LookupError('Could not find a line for user %s', user_id)
    elif row.protocol.lower() == 'custom':
        return row.name
    else:
        return '%s/%s' % (row.protocol, row.name)


@daosession
def is_phone_exten(session, exten):
    res = (session.query(ExtensionSchema.exten)
           .filter(and_(ExtensionSchema.exten == str(exten),
                        ExtensionSchema.type == 'user')))
    if not res:
        return False
    return res.count() > 0


@daosession
def all_with_protocol(session, protocol):
    protocol = protocol.lower()
    if protocol == 'sip':
        return (
            session.query(
                LineSchema,
                UserSIP,
                UserSchema
            )
            .join(UserLine, UserLine.line_id == LineSchema.id)
            .join(UserSchema, UserLine.user_id == UserSchema.id)
            .join(LineExtension, UserLine.line_id == LineExtension.line_id)
            .filter(LineSchema.protocolid == UserSIP.id)
            .filter(LineSchema.protocol == 'sip')
            .all()
        )
    elif protocol == 'iax':
        return (
            session.query(
                LineSchema,
                UserIAX,
                UserSchema
            )
            .join(UserLine, UserLine.line_id == LineSchema.id)
            .join(UserSchema, UserLine.user_id == UserSchema.id)
            .join(LineExtension, UserLine.line_id == LineExtension.line_id)
            .filter(LineSchema.protocolid == UserIAX.id)
            .filter(LineSchema.protocol == 'iax')
            .all()
        )
    elif protocol == 'sccp':
        return (
            session.query(
                LineSchema,
                SCCPLine,
                UserSchema
            )
            .join(UserLine, UserLine.line_id == LineSchema.id)
            .join(UserSchema, UserLine.user_id == UserSchema.id)
            .join(LineExtension, UserLine.line_id == LineExtension.line_id)
            .filter(LineSchema.protocolid == SCCPLine.id)
            .filter(LineSchema.protocol == 'sccp')
            .all()
        )
    elif protocol == 'custom':
        return (
            session.query(
                LineSchema,
                UserCustom,
                UserSchema
            )
            .join(UserLine, UserLine.line_id == LineSchema.id)
            .join(UserSchema, UserLine.user_id == UserSchema.id)
            .join(LineExtension, UserLine.line_id == LineExtension.line_id)
            .filter(LineSchema.protocolid == UserCustom.id)
            .filter(LineSchema.protocol == 'custom')
            .all()
        )


@daosession
def get_with_line_id(session, line_id):
    protocol = get_protocol(line_id)
    protocol = protocol.lower()
    if protocol == 'sip':
        result = (
            session.query(
                LineSchema,
                UserSIP,
                UserSchema
            )
            .join(UserLine, UserLine.line_id == LineSchema.id)
            .join(UserSchema, UserLine.user_id == UserSchema.id)
            .join(LineExtension, UserLine.line_id == LineExtension.line_id)
            .filter(LineSchema.id == int(line_id))
            .filter(LineSchema.protocolid == UserSIP.id)
            .first()
        )
    elif protocol == 'iax':
        result = (
            session.query(
                LineSchema,
                UserIAX,
                UserSchema
            )
            .join(UserLine, UserLine.line_id == LineSchema.id)
            .join(UserSchema, UserLine.user_id == UserSchema.id)
            .join(LineExtension, UserLine.line_id == LineExtension.line_id)
            .filter(LineSchema.id == int(line_id))
            .filter(LineSchema.protocolid == UserIAX.id)
            .first()
        )
    elif protocol == 'sccp':
        result = (
            session.query(
                LineSchema,
                SCCPLine,
                UserSchema
            )
            .join(UserLine, UserLine.line_id == LineSchema.id)
            .join(UserSchema, UserLine.user_id == UserSchema.id)
            .join(LineExtension, UserLine.line_id == LineExtension.line_id)
            .filter(LineSchema.id == int(line_id))
            .filter(LineSchema.protocolid == SCCPLine.id)
            .first()
        )
    elif protocol == 'custom':
        result = (
            session.query(
                LineSchema,
                UserCustom,
                UserSchema
            )
            .join(UserLine, UserLine.line_id == LineSchema.id)
            .join(UserSchema, UserLine.user_id == UserSchema.id)
            .join(LineExtension, UserLine.line_id == LineExtension.line_id)
            .filter(LineSchema.id == int(line_id))
            .filter(LineSchema.protocolid == UserCustom.id)
            .first()
        )
    else:
        raise ValueError('invalid protocol %s' % protocol)

    if not result:
        raise LookupError('No line with ID %s or no user associated to line' % line_id)
    return result


def get_cid_for_channel(channel):
    protocol = channel.split('/', 1)[0].lower()
    if protocol == 'sip':
        return _get_cid_for_sip_channel(channel)
    elif protocol == 'sccp':
        return _get_cid_for_sccp_channel(channel)
    else:
        raise ValueError('Cannot get the Caller ID for this channel')


@daosession
def _get_cid_for_sccp_channel(session, channel):
    _, name = _get_proto_name(channel, 'sccp')

    line = session.query(SCCPLine.cid_name, SCCPLine.cid_num).filter(SCCPLine.name == name)[0]

    cid_name, cid_num = line.cid_name, line.cid_num

    return caller_id.build_caller_id('', cid_name, cid_num)


@daosession
def _get_cid_for_sip_channel(session, channel):
    proto, name = _get_proto_name(channel, 'sip')

    cid_all = (session.query(UserSIP.callerid)
               .filter(and_(UserSIP.name == name, UserSIP.protocol == proto.lower()))[0].callerid)

    return caller_id.build_caller_id(cid_all, None, None)


def _get_proto_name(channel, expected_proto):
    proto_iface = protocol_interface.protocol_interface_from_channel(channel)
    if proto_iface.protocol.lower() != expected_proto.lower():
        raise ValueError('Not a %s channel' % expected_proto.upper())

    return proto_iface.protocol, proto_iface.interface
