# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
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
