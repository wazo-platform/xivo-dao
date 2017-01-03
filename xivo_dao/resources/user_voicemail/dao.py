# -*- coding: utf-8 -*-

# Copyright 2013-2016 The Wazo Authors  (see the AUTHORS file)
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
    return query.first()


def get_by(**criteria):
    user_voicemail = find_by(**criteria)
    if not user_voicemail:
        raise errors.not_found('UserVoicemail', **criteria)
    return user_voicemail


@daosession
def find_all_by(session, **criteria):
    query = find_query(session, criteria)
    return query.all()


def get_by_user_id(user_id):
    return get_by(user_id=user_id)


def find_by_user_id(user_id):
    return find_by(user_id=user_id)


def find_all_by_voicemail_id(voicemail_id):
    return find_all_by(voicemail_id=voicemail_id)


@daosession
def associate(session, user, voicemail):
    with flush_session(session):
        user.voicemailid = voicemail.id
        user.enablevoicemail = 1
        session.add(user)


@daosession
def dissociate(session, user, voicemail):
    with flush_session(session):
        user.voicemailid = None
        user.enablevoicemail = 0
        session.add(user)
