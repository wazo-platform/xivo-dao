# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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

from xivo_dao.alchemy.stat_call_on_queue import StatCallOnQueue
from xivo_dao import stat_queue_dao
from sqlalchemy import func, between, literal
from sqlalchemy.sql.expression import extract, cast
from sqlalchemy.types import Integer
from datetime import timedelta


def _add_call(session, callid, time, queue_name, event, waittime=None):
    queue_id = int(stat_queue_dao.id_from_name(queue_name))
    call_on_queue = StatCallOnQueue()
    call_on_queue.time = time
    call_on_queue.callid = callid
    call_on_queue.queue_id = queue_id
    call_on_queue.status = event
    if waittime:
        call_on_queue.waittime = waittime

    session.add(call_on_queue)
    session.flush()


def add_abandoned_call(dao_sess, callid, time, queue_name, waittime):
    _add_call(dao_sess, callid, time, queue_name, 'abandoned', waittime)


def add_full_call(dao_sess, callid, time, queue_name):
    _add_call(dao_sess, callid, time, queue_name, 'full')


def add_joinempty_call(dao_sess, callid, time, queue_name):
    _add_call(dao_sess, callid, time, queue_name, 'joinempty')


def add_leaveempty_call(dao_sess, callid, time, queue_name, waittime):
    _add_call(dao_sess, callid, time, queue_name, 'leaveempty', waittime)


def add_closed_call(dao_sess, callid, time, queue_name):
    _add_call(dao_sess, callid, time, queue_name, 'closed')


def add_timeout_call(dao_sess, callid, time, queue_name, waittime):
    _add_call(dao_sess, callid, time, queue_name, 'timeout', waittime)


def get_periodic_stats_quarter_hour(session, start, end):
    quarter_hour_step = func.date_trunc(literal('hour'), StatCallOnQueue.time) + \
        (cast(extract('minute', StatCallOnQueue.time), Integer) / 15) * timedelta(minutes=15)
    return _get_periodic_stat_by_step(session, start, end, quarter_hour_step)


def get_periodic_stats_hour(session, start, end):
    one_hour_step = func.date_trunc(literal('hour'), StatCallOnQueue.time)
    return _get_periodic_stat_by_step(session, start, end, one_hour_step)


def _get_periodic_stat_by_step(session, start, end, step):
    stats = {}

    rows = (session
            .query(step.label('the_time'),
                   StatCallOnQueue.queue_id,
                   StatCallOnQueue.status,
                   func.count(StatCallOnQueue.status))
            .group_by('the_time',
                      StatCallOnQueue.queue_id,
                      StatCallOnQueue.status)
            .filter(between(StatCallOnQueue.time, start, end)))

    for period, queue_id, status, number in rows.all():
        if period not in stats:
            stats[period] = {}
        if queue_id not in stats[period]:
            stats[period][queue_id] = {'total': 0}
        stats[period][queue_id][status] = number
        stats[period][queue_id]['total'] += number

    return stats


def clean_table(session):
    session.query(StatCallOnQueue).delete()


def remove_after(session, date):
    session.query(StatCallOnQueue).filter(StatCallOnQueue.time >= date).delete()


def find_all_callid_between_date(session, start_date, end_date):
    rows = (session.query(StatCallOnQueue.callid)
            .filter(StatCallOnQueue.time.between(start_date, end_date))
            .all())

    return [row[0] for row in rows]


def remove_callids(session, callids):
    if not callids:
        return

    session.query(StatCallOnQueue).filter(StatCallOnQueue.callid.in_(callids)).delete(synchronize_session='fetch')
