# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy import and_
from xivo_dao.alchemy.queueinfo import QueueInfo
from xivo_dao.helpers.db_utils import flush_session
from xivo_dao.helpers.db_manager import daosession


@daosession
def add_entry(session, call_time, queue_name, caller_id_num, uniqueid):
    entry = QueueInfo(
        call_time_t=call_time,
        queue_name=queue_name,
        caller=caller_id_num,
        caller_uniqueid=uniqueid,
    )

    with flush_session(session):
        session.add(entry)


def _find_by_uniqueid_calltime(session, uniqueid, calltime):
    return session.query(QueueInfo).filter(and_(QueueInfo.caller_uniqueid == uniqueid,
                                                QueueInfo.call_time_t == calltime)).first()


@daosession
def update_holdtime(session, uniqueid, calltime, holdtime, answerer=None):
    with flush_session(session):
        qi = _find_by_uniqueid_calltime(session, uniqueid, calltime)
        qi.hold_time = holdtime
        if answerer:
            qi.call_picker = answerer


@daosession
def update_talktime(session, uniqueid, calltime, talktime):
    with flush_session(session):
        qi = _find_by_uniqueid_calltime(session, uniqueid, calltime)
        qi.talk_time = talktime
