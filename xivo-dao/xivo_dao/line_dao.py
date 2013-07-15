# -*- coding: utf-8 -*-

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

from xivo import caller_id
from xivo_dao.alchemy.extension import Extension as ExtensionSchema
from xivo.asterisk.extension import Extension
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.sccpline import SCCPLine
from xivo_dao.alchemy.usercustom import UserCustom
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.alchemy.useriax import UserIAX
from xivo_dao.alchemy.usersip import UserSIP
from sqlalchemy import and_
from xivo_dao.helpers.db_manager import daosession
from xivo.asterisk import protocol_interface


@daosession
def find_line_id_by_user_id(session, user_id):
    res = session.query(LineFeatures).filter(LineFeatures.iduserfeatures == int(user_id))
    return [line.id for line in res]


@daosession
def find_context_by_user_id(session, user_id):
    res = session.query(LineFeatures).filter(LineFeatures.iduserfeatures == int(user_id))
    context_list = [line.context for line in res]
    return context_list[0] if len(context_list) > 0 else None


@daosession
def get_interface_from_exten_and_context(session, extension, context):
    res = (session.query(LineFeatures.protocol, LineFeatures.name)
           .filter(LineFeatures.number == extension)
           .filter(LineFeatures.context == context)).first()
    if res is None:
        raise LookupError('no line with extension %s and context %s' % (extension, context))
    return _format_interface(res.protocol, res.name)


@daosession
def get_extension_from_protocol_interface(session, protocol, interface):
    line_row = (session.query(LineFeatures.number, LineFeatures.context)
                .filter(LineFeatures.protocol == protocol.lower())
                .filter(LineFeatures.name == interface)
                .first())

    if not line_row:
        message = 'no line with interface %s' % interface
        raise LookupError(message)

    extension = Extension(number=line_row[0], context=line_row[1], is_internal=True)
    return extension


def _format_interface(protocol, name):
    if protocol == 'custom':
        return name
    else:
        return '%s/%s' % (protocol.upper(), name)


@daosession
def number(session, line_id):
    res = session.query(LineFeatures).filter(LineFeatures.id == line_id)
    if res.count() == 0:
        raise LookupError
    else:
        return res[0].number


@daosession
def get_number_by_user_id(session, user_id):
    res = session.query(LineFeatures).filter(LineFeatures.iduserfeatures == user_id)
    if res.count() == 0:
        raise LookupError
    else:
        return res[0].number


@daosession
def is_phone_exten(session, exten):
    return session.query(LineFeatures).filter(LineFeatures.number == exten).count() > 0


@daosession
def get_protocol(session, line_id):
    row = session.query(LineFeatures).filter(LineFeatures.id == line_id).first()
    if not row:
        raise LookupError
    return row.protocol


@daosession
def all_with_protocol(session, protocol):
    protocol = protocol.lower()
    if protocol == 'sip':
        return (
            session.query(
                LineFeatures,
                UserSIP,
                UserFeatures.firstname,
                UserFeatures.lastname
            )
            .filter(LineFeatures.protocolid == UserSIP.id)
            .filter(LineFeatures.protocol == 'sip')
            .filter(LineFeatures.iduserfeatures == UserFeatures.id)
            .all()
        )
    elif protocol == 'iax':
        return (
            session.query(
                LineFeatures,
                UserIAX,
                UserFeatures.firstname,
                UserFeatures.lastname
            )
            .filter(LineFeatures.protocolid == UserIAX.id)
            .filter(LineFeatures.protocol == 'iax')
            .filter(LineFeatures.iduserfeatures == UserFeatures.id)
            .all()
        )
    elif protocol == 'sccp':
        return (
            session.query(
                LineFeatures,
                SCCPLine,
                UserFeatures.firstname,
                UserFeatures.lastname
            )
            .filter(LineFeatures.protocolid == SCCPLine.id)
            .filter(LineFeatures.protocol == 'sccp')
            .filter(LineFeatures.iduserfeatures == UserFeatures.id)
            .all()
        )
    elif protocol == 'custom':
        return (
            session.query(
                LineFeatures,
                UserCustom,
                UserFeatures.firstname,
                UserFeatures.lastname
            )
            .filter(LineFeatures.protocolid == UserCustom.id)
            .filter(LineFeatures.protocol == 'custom')
            .filter(LineFeatures.iduserfeatures == UserFeatures.id)
            .all()
        )


@daosession
def get_with_line_id(session, line_id):
    protocol = get_protocol(line_id)
    protocol = protocol.lower()
    if protocol == 'sip':
        return (
            session.query(
                LineFeatures,
                UserSIP,
                UserFeatures.firstname,
                UserFeatures.lastname
            )
            .filter(LineFeatures.id == int(line_id))
            .filter(LineFeatures.protocolid == UserSIP.id)
            .filter(LineFeatures.iduserfeatures == UserFeatures.id)
            .first()
        )
    elif protocol == 'iax':
        return (
            session.query(
                LineFeatures,
                UserIAX,
                UserFeatures.firstname,
                UserFeatures.lastname
            )
            .filter(LineFeatures.id == int(line_id))
            .filter(LineFeatures.protocolid == UserIAX.id)
            .filter(LineFeatures.iduserfeatures == UserFeatures.id)
            .first()
        )
    elif protocol == 'sccp':
        return (
            session.query(
                LineFeatures,
                SCCPLine,
                UserFeatures.firstname,
                UserFeatures.lastname
            )
            .filter(LineFeatures.id == int(line_id))
            .filter(LineFeatures.protocolid == SCCPLine.id)
            .filter(LineFeatures.iduserfeatures == UserFeatures.id)
            .first()
        )
    elif protocol == 'custom':
        return (
            session.query(
                LineFeatures,
                UserCustom,
                UserFeatures.firstname,
                UserFeatures.lastname
            )
            .filter(LineFeatures.id == int(line_id))
            .filter(LineFeatures.protocolid == UserCustom.id)
            .filter(LineFeatures.iduserfeatures == UserFeatures.id)
            .first()
        )


def get_cid_for_channel(channel):
    protocol = channel.split('/', 1)[0].lower()
    if protocol == 'sip':
        return _get_cid_for_sip_channel(channel)
    elif protocol == 'sccp':
        return _get_cid_for_sccp_channel(channel)
    else:
        raise ValueError('Cannot get the Caller ID for this channel')


@daosession
def get_interface_from_user_id(session, user_id):
    row = (session
           .query(LineFeatures.protocol,
                  LineFeatures.name,
                  LineFeatures.iduserfeatures)
           .filter(LineFeatures.iduserfeatures == user_id)
           .first())

    if not row:
        raise LookupError('No such line')

    if row.protocol.lower() == 'custom':
        return row.name
    else:
        return row.protocol + '/' + row.name


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


@daosession
def create(session, line):
    session.begin()
    try:
        session.add(line)
        session.commit()
    except Exception:
        session.rollback()
        raise


@daosession
def delete(session, lineid):
    session.begin()
    try:
        line = session.query(LineFeatures).filter(LineFeatures.id == lineid).first()
        session.query(UserSIP).filter(UserSIP.id == line.protocolid).delete()
        (session.query(ExtensionSchema).filter(ExtensionSchema.exten == line.number)
                                       .filter(ExtensionSchema.context == line.context)
                                       .delete())
        session.delete(line)
        session.commit()
    except Exception:
        session.rollback()
        raise


@daosession
def get(session, lineid):
    return session.query(LineFeatures).filter(LineFeatures.id == lineid).first()
