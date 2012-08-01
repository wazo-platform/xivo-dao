# -*- coding: UTF-8 -*-

from xivo_dao.alchemy.stat_call_on_queue import StatCallOnQueue
from xivo_dao.alchemy import dbconnection
from xivo_dao import stat_queue_dao
from sqlalchemy import func, between, literal

_DB_NAME = 'asterisk'


def _session():
    connection = dbconnection.get_connection(_DB_NAME)
    return connection.get_session()


def _add_call(callid, time, queue_name, event, waittime=None):
    queue_id = int(stat_queue_dao.id_from_name(queue_name))
    call_on_queue = StatCallOnQueue()
    call_on_queue.time = time
    call_on_queue.callid = callid
    call_on_queue.queue_id = queue_id
    call_on_queue.status = event
    if waittime:
        call_on_queue.waittime = waittime

    _session().add(call_on_queue)
    _session().commit()


def add_abandoned_call(callid, time, queue_name, waittime):
    _add_call(callid, time, queue_name, 'abandoned', waittime)


def add_answered_call(callid, time, queue_name, waittime):
    _add_call(callid, time, queue_name, 'answered', waittime)


def add_full_call(callid, time, queue_name):
    _add_call(callid, time, queue_name, 'full')


def add_joinempty_call(callid, time, queue_name):
    _add_call(callid, time, queue_name, 'joinempty')


def add_leaveempty_call(callid, time, queue_name, waittime):
    _add_call(callid, time, queue_name, 'leaveempty', waittime)


def add_closed_call(callid, time, queue_name):
    _add_call(callid, time, queue_name, 'closed')


def add_timeout_call(callid, time, queue_name, waittime):
    _add_call(callid, time, queue_name, 'timeout', waittime)


def get_periodic_stats(start, end):
    stats = {}

    rows = (_session()
           .query(func.date_trunc(literal('hour'), StatCallOnQueue.time),
                  StatCallOnQueue.queue_id,
                  StatCallOnQueue.status,
                  func.count(StatCallOnQueue.status))
           .group_by(func.date_trunc(literal('hour'), StatCallOnQueue.time),
                     StatCallOnQueue.queue_id,
                     StatCallOnQueue.status)
           .filter(between(StatCallOnQueue.time, start, end)))

    for period, queue_id, status, number in rows:
        if period not in stats:
            stats[period] = {}
        if queue_id not in stats[period]:
            stats[period][queue_id] = {'total': 0}
        stats[period][queue_id][status] = number
        stats[period][queue_id]['total'] += number

    return stats


def clean_table():
    _session().query(StatCallOnQueue).delete()
    _session().commit()
