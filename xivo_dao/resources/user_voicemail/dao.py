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

from xivo_dao.helpers.db_utils import flush_session
from xivo_dao.helpers.db_manager import daosession


COLUMNS = {'user_id': UserSchema.id,
           'voicemail_id': UserSchema.voicemailid}


def find_query(session, criteria):
    query = (session.query(UserSchema.id.label('user_id'),
                           UserSchema.uuid.label('user_uuid'),
                           UserSchema.voicemailid.label('voicemail_id'),
                           UserSchema.enablevoicemail)
             .filter(UserSchema.voicemailid != None)  # noqa
             .filter(UserSchema.voicemailid != 0))
    for name, value in criteria.iteritems():
        column = COLUMNS.get(name)
        if not column:
            raise errors.unknown(column)
        query = query.filter(column == value)
    return query


@daosession
def find_by(session, **criteria):
    query = find_query(session, criteria)
    row = query.first()
    return db_converter.to_model(row) if row else None


def get_by(**criteria):
    extension = find_by(**criteria)
    if not extension:
        raise errors.not_found('UserVoicemail', **criteria)
    return extension


@daosession
def find_all_by(session, **criteria):
    query = find_query(session, criteria)
    return [db_converter.to_model(row) for row in query]


def get_by_user_id(user_id):
    return get_by(user_id=user_id)


def find_by_user_id(user_id):
    return find_by(user_id=user_id)


def find_all_by_voicemail_id(voicemail_id):
    return find_all_by(voicemail_id=voicemail_id)


@daosession
def associate(session, user_voicemail):
    with flush_session(session):
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
def dissociate(session, user_voicemail):
    with flush_session(session):
        _dissociate_voicemail_from_user(session, user_voicemail.user_id)


def _dissociate_voicemail_from_user(session, user_id):
    user_row = (session.query(UserSchema)
                .filter(UserSchema.id == user_id)
                .first())
    if user_row:
        user_row.voicemailid = None
        user_row.enablevoicemail = 0
        session.add(user_row)
