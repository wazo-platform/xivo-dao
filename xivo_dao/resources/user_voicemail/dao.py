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

from xivo_dao.alchemy.userfeatures import UserFeatures as UserSchema

from xivo_dao.helpers import errors

from xivo_dao.resources.user_voicemail.model import db_converter

from xivo_dao.helpers.db_utils import commit_or_abort
from xivo_dao.helpers.db_manager import daosession


@daosession
def associate(session, user_voicemail):
    with commit_or_abort(session):
        _associate_voicemail_with_user(session, user_voicemail)


def _associate_voicemail_with_user(session, user_voicemail):
    user_row = (session.query(UserSchema)
                .filter(UserSchema.id == user_voicemail.user_id)
                .first())

    if user_row:
        user_row.voicemailid = user_voicemail.voicemail_id
        user_row.enablevoicemail = int(user_voicemail.enabled)
        session.add(user_row)


def _fetch_by_user_id(session, user_id):
    row = (session.query(UserSchema.id.label('user_id'),
                         UserSchema.voicemailid.label('voicemail_id'),
                         UserSchema.enablevoicemail)
           .filter(UserSchema.id == user_id)
           .first())

    return row


@daosession
def get_by_user_id(session, user_id):
    row = _fetch_by_user_id(session, user_id)

    if not row:
        raise errors.not_found('User', id=user_id)

    if row.voicemail_id is None or row.voicemail_id == 0:
        raise errors.not_found('UserVoicemail', user_id=user_id)

    return db_converter.to_model(row)


@daosession
def find_by_user_id(session, user_id):
    row = _fetch_by_user_id(session, user_id)

    if not row:
        return None

    if row.voicemail_id is None or row.voicemail_id == 0:
        return None

    return db_converter.to_model(row)


@daosession
def find_all_by_voicemail_id(session, voicemail_id):
    query = (session.query(UserSchema.id.label('user_id'),
                           UserSchema.voicemailid.label('voicemail_id'),
                           UserSchema.enablevoicemail)
             .filter(UserSchema.voicemailid == voicemail_id))

    return [db_converter.to_model(row) for row in query]


@daosession
def dissociate(session, user_voicemail):
    with commit_or_abort(session):
        _dissociate_voicemail_from_user(session, user_voicemail.user_id)


def _dissociate_voicemail_from_user(session, user_id):
    user_row = (session.query(UserSchema)
                .filter(UserSchema.id == user_id)
                .first())
    if user_row:
        user_row.voicemailid = None
        user_row.enablevoicemail = 0
        session.add(user_row)
