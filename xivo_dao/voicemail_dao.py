# -*- coding: utf-8 -*-

# Copyright 2012-2017 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.sql.expression import and_
from xivo_dao.alchemy.contextmember import ContextMember
from xivo_dao.alchemy.voicemail import Voicemail
from xivo_dao.helpers.db_utils import flush_session
from xivo_dao.helpers.db_manager import daosession


@daosession
def all(session):
    return session.query(Voicemail).all()


@daosession
def get(session, voicemail_id):
    return session.query(Voicemail).filter(Voicemail.uniqueid == voicemail_id).first()


@daosession
def add(session, voicemail):
    with flush_session(session):
        session.add(voicemail)
        session.flush()
        contextmember = ContextMember(context=voicemail.context,
                                      type='voicemail',
                                      typeval=str(voicemail.uniqueid),
                                      varname='context')
        session.add(contextmember)


@daosession
def id_from_mailbox(session, mailbox, context):
    result = session.query(Voicemail.uniqueid).filter(and_(Voicemail.mailbox == mailbox,
                                                           Voicemail.context == context)).first()
    if result is None:
        return None
    return result[0]


@daosession
def update(session, voicemailid, data):
    with flush_session(session):
        session.query(Voicemail).filter(Voicemail.uniqueid == voicemailid).update(data)


@daosession
def delete(session, uniqueid):
    with flush_session(session):
        impacted_rows = session.query(Voicemail).filter(Voicemail.uniqueid == uniqueid).delete()
        session.query(ContextMember).filter(and_(ContextMember.type == 'voicemail',
                                                 ContextMember.typeval == str(uniqueid))).delete()
        return impacted_rows


@daosession
def get_contextmember(session, voicemailid):
    return session.query(ContextMember).filter(and_(ContextMember.type == 'voicemail',
                                                    ContextMember.typeval == str(voicemailid))).first()
