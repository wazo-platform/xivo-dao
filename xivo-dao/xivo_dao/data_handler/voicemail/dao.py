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
from xivo_dao.data_handler.voicemail.model import Voicemail
from xivo_dao.helpers import sysconfd_connector
from xivo_dao.helpers.sysconfd_connector import SysconfdError
from xivo_dao.data_handler.exception import ElementNotExistsError, \
    ElementCreationError, ElementEditionError, ElementDeletionError


@daosession
def find_all(session):
    res = session.query(VoicemailSchema).all()
    if not res:
        return None

    tmp = []
    for voicemail in res:
        tmp.append(Voicemail.from_data_source(voicemail))

    return tmp


@daosession
def find_voicemail(session, number, context):

    voicemail = (session.query(VoicemailSchema)
                 .filter(VoicemailSchema.mailbox == number)
                 .filter(VoicemailSchema.context == context)
                 .first())
    if not voicemail:
        return None

    return Voicemail.from_data_source(voicemail)


@daosession
def get(session, voicemail_id):
    voicemail = (session.query(VoicemailSchema)
                 .filter(VoicemailSchema.uniqueid == voicemail_id)
                 .first())
    if not voicemail:
        raise ElementNotExistsError('Voicemail', uniqueid=voicemail_id)

    return Voicemail.from_data_source(voicemail)


@daosession
def create(session, voicemail):
    voicemail_row = voicemail.to_data_source(VoicemailSchema)
    session.begin()
    session.add(voicemail_row)

    try:
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise ElementCreationError('voicemail', e)

    return voicemail_row.uniqueid


@daosession
def edit(session, voicemail):
    session.begin()
    nb_row_affected = (session.query(VoicemailSchema)
                       .filter(VoicemailSchema.uniqueid == voicemail.id)
                       .update(voicemail.to_data_dict()))

    try:
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise ElementEditionError('voicemail', e)

    if nb_row_affected == 0:
        raise ElementEditionError('voicemail', 'No now affected, probably voicemail_id %s not exsit' % voicemail.id)

    return nb_row_affected


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
            raise SysconfdError(str(e))
        else:
            session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise ElementDeletionError('voicemail', e)

    if nb_row_affected == 0:
        raise ElementDeletionError('voicemail', 'No now affected, probably voicemail_id %s not exsit' % voicemail.id)


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
