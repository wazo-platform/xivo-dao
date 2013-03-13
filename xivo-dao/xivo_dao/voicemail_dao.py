# -*- coding: utf-8 -*-

# Copyright (C) 2012-2013 Avencall
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

from sqlalchemy.sql.expression import and_
from xivo_dao.alchemy.voicemail import Voicemail
from xivo_dao.helpers.db_manager import daosession


@daosession
def all(session):
    return session.query(Voicemail).all()


@daosession
def get(session, voicemail_id):
    return session.query(Voicemail).filter(Voicemail.uniqueid == voicemail_id).first()


@daosession
def delete_all(session):
    session.begin()
    try:
        session.query(Voicemail).delete()
        session.commit()
    except Exception as e:
        session.rollback()
        raise e


@daosession
def add(session, voicemail):
    session.begin()
    try:
        session.add(voicemail)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e


@daosession
def id_from_mailbox(session, mailbox, context):
    result = session.query(Voicemail.uniqueid).filter(and_(Voicemail.mailbox == mailbox,
                                                         Voicemail.context == context)).first()
    return result[0]


@daosession
def update(session, voicemailid, data):
    session.begin()
    try:
        session.query(Voicemail).filter(Voicemail.uniqueid == voicemailid).update(data)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
