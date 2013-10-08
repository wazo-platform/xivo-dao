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

from sqlalchemy.exc import SQLAlchemyError
from xivo_dao.alchemy.voicemail import Voicemail as VoicemailSchema
from xivo_dao.alchemy.usersip import UserSIP as UserSIPSchema
from xivo_dao.alchemy.userfeatures import UserFeatures as UserSchema
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.data_handler.voicemail.model import db_converter
from xivo_dao.helpers import sysconfd_connector
from xivo_dao.helpers.sysconfd_connector import SysconfdError
from xivo_dao.data_handler.exception import ElementNotExistsError, \
    ElementCreationError, ElementEditionError, ElementDeletionError


@daosession
def find_all(session):
    rows = session.query(VoicemailSchema).all()
    if not rows:
        return []

    voicemails = []
    for row in rows:
        voicemail = db_converter.to_model(row)
        voicemails.append(voicemail)

    return voicemails


@daosession
def get_by_number_context(session, number, context):
    row = (session.query(VoicemailSchema)
           .filter(VoicemailSchema.mailbox == number)
           .filter(VoicemailSchema.context == context)
           .first())
    if not row:
        raise ElementNotExistsError('Voicemail', number=number, context=context)

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
        raise ElementNotExistsError('Voicemail', uniqueid=voicemail_id)

    return row


@daosession
def create(session, voicemail):
    voicemail_row = db_converter.to_source(voicemail)
    session.begin()
    session.add(voicemail_row)

    try:
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise ElementCreationError('voicemail', e)

    voicemail.id = voicemail_row.uniqueid

    return voicemail


@daosession
def edit(session, voicemail):
    session.begin()

    voicemail_row = _get_voicemail_row(voicemail.id)
    db_converter.update_source(voicemail_row, voicemail)

    session.begin()
    session.add(voicemail_row)

    try:
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise ElementEditionError('voicemail', e)


@daosession
def delete(session, voicemail):
    session.begin()
    try:
        _unlink_user_sip(session, voicemail.number_at_context)
        _unlink_user(session, voicemail.id)
        nb_row_affected = _delete_voicemail(session, voicemail.id)
        try:
            sysconfd_connector.delete_voicemail_storage(voicemail.context, voicemail.number)
        except Exception as e:
            session.rollback()
            raise SysconfdError(str(e))
        else:
            session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise ElementDeletionError('voicemail', e)

    if nb_row_affected == 0:
        raise ElementDeletionError('voicemail', 'voicemail_id %s not exist' % voicemail.id)


def _unlink_user_sip(session, number_at_context):
    (session.query(UserSIPSchema)
     .filter(UserSIPSchema.mailbox == number_at_context)
     .update({'mailbox': None}))


def _unlink_user(session, voicemail_id):
    (session.query(UserSchema)
     .filter(UserSchema.voicemailid == voicemail_id)
     .update({'voicemailid': None}))


def _delete_voicemail(session, voicemail_id):
    return (session.query(VoicemailSchema)
            .filter(VoicemailSchema.uniqueid == voicemail_id)
            .delete())
