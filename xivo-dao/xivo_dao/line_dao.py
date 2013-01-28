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
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.sccpline import SCCPLine
from xivo_dao.alchemy.usersip import UserSIP
from xivo_dao.alchemy.useriax import UserIAX
from xivo_dao.alchemy.usercustom import UserCustom
from sqlalchemy import and_
from xivo_dao.helpers.db_manager import DbSession


def find_line_id_by_user_id(user_id):
    res = DbSession().query(LineFeatures).filter(LineFeatures.iduserfeatures == int(user_id))
    return [line.id for line in res]


def find_context_by_user_id(user_id):
    res = DbSession().query(LineFeatures).filter(LineFeatures.iduserfeatures == int(user_id))
    context_list = [line.context for line in res]
    return context_list[0] if len(context_list) > 0 else None


def get_interface_from_exten_and_context(extension, context):
    res = (DbSession().query(LineFeatures.protocol, LineFeatures.name)
           .filter(LineFeatures.number == extension)
           .filter(LineFeatures.context == context)).first()
    if res is None:
        raise LookupError('no line with extension %s and context %s' % (extension, context))
    return _format_interface(res.protocol, res.name)


def _format_interface(protocol, name):
    if protocol == 'custom':
        return name
    else:
        return '%s/%s' % (protocol.upper(), name)


def number(line_id):
    res = DbSession().query(LineFeatures).filter(LineFeatures.id == line_id)
    if res.count() == 0:
        raise LookupError
    else:
        return res[0].number


def is_phone_exten(exten):
    return DbSession().query(LineFeatures).filter(LineFeatures.number == exten).count() > 0


def get_protocol(line_id):
    row = DbSession().query(LineFeatures).filter(LineFeatures.id == line_id).first()
    if not row:
        raise LookupError
    return row.protocol


def all_with_protocol(protocol):
    if protocol.lower() == 'sip':
        return DbSession().query(LineFeatures, UserSIP).filter(LineFeatures.protocolid == UserSIP.id).all()
    elif protocol.lower() == 'iax':
        return DbSession().query(LineFeatures, UserIAX).filter(LineFeatures.protocolid == UserIAX.id).all()
    elif protocol.lower() == 'sccp':
        return DbSession().query(LineFeatures, SCCPLine).filter(LineFeatures.protocolid == SCCPLine.id).all()
    elif protocol.lower() == 'custom':
        return DbSession().query(LineFeatures, UserCustom).filter(LineFeatures.protocolid == UserCustom.id).all()


def get_with_line_id(line_id):
    protocol = get_protocol(line_id)
    if protocol.lower() == 'sip':
        return (DbSession().query(LineFeatures, UserSIP)
                .filter(LineFeatures.id == int(line_id))
                .filter(LineFeatures.protocolid == UserSIP.id)
                .first())
    elif protocol.lower() == 'iax':
        return (DbSession().query(LineFeatures, UserIAX)
                .filter(LineFeatures.id == int(line_id))
                .filter(LineFeatures.protocolid == UserIAX.id)
                .first())
    elif protocol.lower() == 'sccp':
        return (DbSession().query(LineFeatures, SCCPLine)
                .filter(LineFeatures.id == int(line_id))
                .filter(LineFeatures.protocolid == SCCPLine.id)
                .first())
    elif protocol.lower() == 'custom':
        return (DbSession().query(LineFeatures, UserCustom)
                .filter(LineFeatures.id == int(line_id))
                .filter(LineFeatures.protocolid == UserCustom.id)
                .first())


def get_cid_for_channel(channel):
    protocol = channel.split('/', 1)[0].lower()
    if protocol == 'sip':
        return _get_cid_for_sip_channel(channel)
    elif protocol == 'sccp':
        return _get_cid_for_sccp_channel(channel)
    else:
        raise ValueError('Cannot get the Caller ID for this channel')


def get_interface_from_user_id(user_id):
    row = (DbSession()
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


def _get_cid_for_sccp_channel(channel):
    try:
        interesting_part = channel.split('@', 1)[0]
        protocol, line_name = interesting_part.split('/', 1)
        assert(protocol == 'sccp')
    except (IndexError, AssertionError):
        raise ValueError('Not an SCCP channel')

    line = DbSession().query(SCCPLine.cid_name, SCCPLine.cid_num).filter(SCCPLine.name == line_name)[0]

    cid_name, cid_num = line.cid_name, line.cid_num

    return caller_id.build_caller_id('', cid_name, cid_num)


def _get_cid_for_sip_channel(channel):
    protocol, name = channel.split('-', 1)[0].split('/', 1)
    if protocol.lower() != 'sip':
        raise ValueError('Not a SIP channel')

    cid_all = (DbSession().query(UserSIP.callerid)
               .filter(and_(UserSIP.name == name, UserSIP.protocol == protocol.lower()))[0].callerid)

    return caller_id.build_caller_id(cid_all, None, None)
