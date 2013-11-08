# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from xivo_dao.alchemy.linefeatures import LineFeatures as LineSchema
from xivo_dao.alchemy.sccpdevice import SCCPDevice as SCCPDeviceSchema
from xivo_dao.alchemy.userfeatures import UserFeatures as UserSchema
from xivo_dao.alchemy.usersip import UserSIP as UserSIPSchema

from xivo_dao.data_handler.exception import ElementNotExistsError
from xivo_dao.data_handler.user_line_extension import dao as user_line_dao
from xivo_dao.data_handler.user_voicemail.model import db_converter
from xivo_dao.data_handler.user_voicemail.exception import UserVoicemailNotExistsError
from xivo_dao.data_handler.voicemail import dao as voicemail_dao

from xivo_dao.helpers.db_manager import daosession


@daosession
def associate(session, user_voicemail):
    session.begin()
    _associate_voicemail_with_user(session, user_voicemail)
    _associate_voicemail_with_line(session, user_voicemail)
    session.commit()


def _associate_voicemail_with_user(session, user_voicemail):
    user_row = (session.query(UserSchema)
                .filter(UserSchema.id == user_voicemail.user_id)
                .first())

    if user_row:
        user_row.voicemailid = user_voicemail.voicemail_id
        user_row.voicemailtype = 'asterisk'
        user_row.enablevoicemail = int(user_voicemail.enabled)
        session.add(user_row)


def _associate_voicemail_with_line(session, user_voicemail):
    voicemail = voicemail_dao.get(user_voicemail.voicemail_id)
    user_lines = _find_main_user_lines(user_voicemail.user_id)

    for user_line in user_lines:
        _associate_voicemail_with_protocol(session, voicemail, user_line.line_id)


def _find_main_user_lines(user_id):
    user_lines = user_line_dao.find_all_by_user_id(user_id)
    return [user_line for user_line in user_lines if user_line.main_user]


def _associate_voicemail_with_protocol(session, voicemail, line_id):
    line_row = (session.query(LineSchema.protocol, LineSchema.protocolid)
                .filter(LineSchema.id == line_id)
                .first())

    if line_row.protocol == 'sip':
        (session
         .query(UserSIPSchema)
         .filter(UserSIPSchema.id == line_row.protocolid)
         .update({'mailbox': voicemail.number_at_context}))
    elif line_row.protocol == 'sccp':
        (session
         .query(SCCPDeviceSchema)
         .filter(SCCPDeviceSchema.id == line_row.protocolid)
         .update({'voicemail': voicemail.number}))


@daosession
def get_by_user_id(session, user_id):
    row = (session.query(UserSchema.id.label('user_id'),
                         UserSchema.voicemailid.label('voicemail_id'),
                         UserSchema.enablevoicemail)
           .filter(UserSchema.id == user_id)
           .first())

    if not row:
        raise ElementNotExistsError('User', id=user_id)

    if row.voicemail_id is None or row.voicemail_id == 0:
        raise UserVoicemailNotExistsError.from_user_id(user_id)

    return db_converter.to_model(row)

@daosession
def dissociate(session, user_id):
    _dissociate_voicemail_from_user(session, user_id)
    _dissociate_voicemail_from_line(session, user_id)

def _dissociate_voicemail_from_user(session, user_id):
    user_row = (session.query(UserSchema)
                .filter(UserSchema.id == user_id)
                .first())
    if user_row:
        user_row.voicemailid = None
        user_row.voicemailtype = None
        user_row.enablevoicemail = 0
        session.add(user_row)

def _dissociate_voicemail_from_line(session, user_id):
    user_lines = _find_main_user_lines(user_id)
    for user_line in user_lines:
        _dissociate_voicemail_from_protocol(session, user_line.line_id)

def _dissociate_voicemail_from_protocol(session, line_id):
    line_row = (session.query(LineSchema.protocol, LineSchema.protocolid)
                .filter(LineSchema.id == line_id)
                .first())

    if line_row.protocol == 'sip':
        (session
         .query(UserSIPSchema)
         .filter(UserSIPSchema.id == line_row.protocolid)
         .update({'mailbox': None}))
    elif line_row.protocol == 'sccp':
        (session
         .query(SCCPDeviceSchema)
         .filter(SCCPDeviceSchema.id == line_row.protocolid)
         .update({'voicemail': ''}))
