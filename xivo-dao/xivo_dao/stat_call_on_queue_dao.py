# -*- coding: UTF-8 -*-

from xivo_dao.alchemy.stat_call_on_queue import StatCallOnQueue
from xivo_dao.alchemy import dbconnection
from xivo_dao import stat_queue_dao
from sqlalchemy import func
from sqlalchemy import between
from sqlalchemy import desc

_DB_NAME = 'asterisk'


def _session():
    connection = dbconnection.get_connection(_DB_NAME)
    return connection.get_session()


def add_full_call(callid, time, queue_name):
    queue_id = int(stat_queue_dao.id_from_name(queue_name))
    call_on_queue = StatCallOnQueue()
    call_on_queue.time = time
    call_on_queue.callid = callid
    call_on_queue.queue_id = queue_id
    call_on_queue.status = 'full'

    _session().add(call_on_queue)
    _session().commit()


def get_periodic_stats(start, end):
    stats = {'total': 0,
             'full': 0}

    res = (_session().query(StatCallOnQueue.status, func.count(StatCallOnQueue.status))
           .group_by(StatCallOnQueue.status)
           .filter(between(StatCallOnQueue.time, start, end)))

    for r in res:
        stats[r[0]] = r[1]
        stats['total'] += r[1]

    return stats


def get_most_recent_time():
    res = (_session().query(StatCallOnQueue.time)
           .order_by(desc(StatCallOnQueue.time))
           .limit(1))
    return res[0].time


def clean_table():
    _session().query(StatCallOnQueue).delete()
    _session().commit()
