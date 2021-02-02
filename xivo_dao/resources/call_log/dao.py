# -*- coding: utf-8 -*-
# Copyright 2013-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.call_log import CallLog
from xivo_dao.alchemy.cel import CEL
from xivo_dao.helpers.db_utils import flush_session
from xivo_dao.helpers.db_manager import daosession


@daosession
def find_all(session):
    return session.query(CallLog).all()


@daosession
def create_from_list(session, call_logs):
    with flush_session(session):
        for call_log in call_logs:
            create_call_log(session, call_log)


def create_call_log(session, call_log):
    session.add(call_log)
    session.flush()

    if call_log.cel_ids:
        (session.query(CEL)
         .filter(CEL.id.in_(call_log.cel_ids))
         .update({'call_log_id': call_log.id}, synchronize_session=False))


@daosession
def delete_from_list(session, call_log_ids):
    with flush_session(session):
        for call_log_id in call_log_ids:
            (session
             .query(CallLog)
             .filter(CallLog.id == call_log_id)
             .delete())


@daosession
def delete(session, older=None):
    with flush_session(session):
        # NOTE(fblackburn) returning object on DELETE is specific to postgresql
        query = CallLog.__table__.delete().returning(CallLog.id)
        if older:
            query = query.where(CallLog.date >= older)
        result = [r.id for r in session.execute(query)]
        return result
