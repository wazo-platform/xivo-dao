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

from xivo_dao.alchemy.extension import Extension as ExtensionSchema
from xivo.asterisk.extension import Extension
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.alchemy.usersip import UserSIP


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


@daosession
def get_peer_name(session, device_id):
    row = (session
           .query(LineFeatures.name, LineFeatures.protocol)
           .filter(LineFeatures.device == str(device_id))).first()

    if not row:
        raise LookupError('No such device')

    return '/'.join([row.protocol, row.name])


@daosession
def get_protocol(session, line_id):
    row = session.query(LineFeatures).filter(LineFeatures.id == line_id).first()
    if not row:
        raise LookupError
    return row.protocol


def _format_interface(protocol, name):
    if protocol == 'custom':
        return name
    else:
        return '%s/%s' % (protocol.upper(), name)


@daosession
def create(session, line):
    session.begin()
    try:
        session.add(line)
        session.commit()
    except Exception:
        session.rollback()
        raise

    return line.id


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
