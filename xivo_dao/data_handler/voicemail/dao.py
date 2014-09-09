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

from sqlalchemy.exc import SQLAlchemyError

from xivo_dao.data_handler import errors
from xivo_dao.alchemy.voicemail import Voicemail as VoicemailSchema
from xivo_dao.alchemy.dialaction import Dialaction as DialactionSchema
from xivo_dao.alchemy.userfeatures import UserFeatures as UserSchema
from xivo_dao.helpers.db_utils import commit_or_abort
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.data_handler.voicemail.model import db_converter
from xivo_dao.data_handler.voicemail.search import voicemail_search
from xivo_dao.data_handler.exception import DataError
from xivo_dao.data_handler.utils.search import SearchResult
from xivo_dao.alchemy.staticvoicemail import StaticVoicemail


@daosession
def search(session, **parameters):
    rows, total = voicemail_search.search(session, parameters)
    items = _generate_items(rows)

    return SearchResult(total, items)


def _generate_items(rows):
    if not rows:
        return []

    return [db_converter.to_model(row) for row in rows]


@daosession
def find_all_timezone(session):
    rows = (session.query(StaticVoicemail.var_name)
            .filter(StaticVoicemail.category == 'zonemessages')
            .all())

    return [row.var_name for row in rows]


@daosession
def get_by_number_context(session, number, context):
    row = (session.query(VoicemailSchema)
           .filter(VoicemailSchema.mailbox == number)
           .filter(VoicemailSchema.context == context)
           .first())
    if not row:
        raise errors.not_found('Voicemail', number=number, context=context)

    return db_converter.to_model(row)


@daosession
def get(session, voicemail_id):
    row = _get_voicemail_row(session, voicemail_id)
    return db_converter.to_model(row)


def _get_voicemail_row(session, voicemail_id):
    row = (session.query(VoicemailSchema)
           .filter(VoicemailSchema.uniqueid == voicemail_id)
           .first())

    if not row:
        raise errors.not_found('Voicemail', id=voicemail_id)

    return row


@daosession
def create(session, voicemail):
    voicemail_row = db_converter.to_source(voicemail)
    with commit_or_abort(session, DataError.on_create, 'voicemail'):
        session.add(voicemail_row)

    voicemail.id = voicemail_row.uniqueid

    return voicemail


@daosession
def edit(session, voicemail):
    voicemail_row = _get_voicemail_row(session, voicemail.id)
    db_converter.update_source(voicemail_row, voicemail)

    with commit_or_abort(session, DataError.on_edit, 'voicemail'):
        session.add(voicemail_row)


@daosession
def delete(session, voicemail):
    with commit_or_abort(session, DataError.on_delete, 'voicemail'):
        _delete_voicemail(session, voicemail.id)
        _unlink_dialactions(session, voicemail.id)


def _delete_voicemail(session, voicemail_id):
    return (session.query(VoicemailSchema)
            .filter(VoicemailSchema.uniqueid == voicemail_id)
            .delete())


def _unlink_dialactions(session, voicemail_id):
    (session.query(DialactionSchema)
     .filter(DialactionSchema.action == 'voicemail')
     .filter(DialactionSchema.actionarg1 == str(voicemail_id))
     .update({'linked': 0}))


@daosession
def is_voicemail_linked(session, voicemail):
    user_links = _count_user_links(session, voicemail)
    return user_links > 0


def _count_user_links(session, voicemail):
    count = (session.query(UserSchema)
             .filter(UserSchema.voicemailid == voicemail.id)
             .count())
    return count
