# Copyright 2013-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import timedelta

from sqlalchemy import between, func, literal, literal_column
from sqlalchemy.sql import text
from sqlalchemy.sql.expression import cast, extract
from sqlalchemy.types import Integer

from xivo_dao import stat_queue_dao
from xivo_dao.alchemy.stat_call_on_queue import StatCallOnQueue


def _add_call(session, callid, time, queue_name, event, waittime=None):
    queue_id = int(stat_queue_dao.id_from_name(queue_name))
    call_on_queue = StatCallOnQueue()
    call_on_queue.time = time
    call_on_queue.callid = callid
    call_on_queue.stat_queue_id = queue_id
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
    quarter_hour_step = func.date_trunc(literal('hour'), StatCallOnQueue.time) + (
        cast(extract('minute', StatCallOnQueue.time), Integer) / 15
    ) * timedelta(minutes=15)
    return _get_periodic_stat_by_step(session, start, end, quarter_hour_step)


def get_periodic_stats_hour(session, start, end):
    one_hour_step = func.date_trunc(literal('hour'), StatCallOnQueue.time)
    return _get_periodic_stat_by_step(session, start, end, one_hour_step)


def _get_periodic_stat_by_step(session, start, end, step):
    stats = {}

    rows = (
        session.query(
            step.label('the_time'),
            StatCallOnQueue.stat_queue_id,
            StatCallOnQueue.status,
            func.count(StatCallOnQueue.status),
        )
        .group_by('the_time', StatCallOnQueue.stat_queue_id, StatCallOnQueue.status)
        .filter(between(StatCallOnQueue.time, start, end))
    )

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
    sql = '''\
      select foo.callid, foo.end from (
        select callid,
               time::TIMESTAMP + (talktime || ' seconds')::INTERVAL
                               + (ringtime || ' seconds')::INTERVAL
                               + (waittime || ' seconds')::INTERVAL AS end
         from stat_call_on_queue) as foo
       where foo.end between :start_date and :end_date
    '''
    rows = (
        session.query(literal_column('callid'))
        .from_statement(text(sql))
        .params(start_date=start_date, end_date=end_date)
    )

    return [row[0] for row in rows]


def remove_callids(session, callids):
    if not callids:
        return

    session.query(StatCallOnQueue).filter(StatCallOnQueue.callid.in_(callids)).delete(
        synchronize_session='fetch'
    )
