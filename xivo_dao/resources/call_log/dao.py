# -*- coding: utf-8 -*-

# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
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

from sqlalchemy import or_

from xivo_dao.alchemy.call_log import CallLog
from xivo_dao.alchemy.cel import CEL
from xivo_dao.helpers.db_utils import flush_session
from xivo_dao.helpers.db_manager import daosession


@daosession
def find_all(session):
    return session.query(CallLog).all()


@daosession
def find_all_in_period(session, start=None, end=None, order=None, direction=None, limit=None, offset=None):
    query = session.query(CallLog)

    if start:
        query = query.filter(CallLog.date >= start)
    if end:
        query = query.filter(CallLog.date < end)

    order_field = None
    if order:
        order_field = getattr(CallLog, order)
    if direction == 'desc':
        order_field = order_field.desc()
    if order_field is not None:
        query = query.order_by(order_field)

    if limit:
        query = query.limit(limit)
    if offset:
        query = query.offset(offset)

    return query.all()


@daosession
def find_all_history_for_phones(session, identifiers, limit):
    call_logs = (session
                 .query(CallLog)
                 .filter(or_(CallLog.destination_line_identity.in_(identifiers),
                             CallLog.source_line_identity.in_(identifiers)))
                 .order_by(CallLog.date.desc())
                 .limit(limit)
                 .all())

    return call_logs


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
