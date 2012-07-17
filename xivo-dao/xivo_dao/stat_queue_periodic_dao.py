# -*- coding: UTF-8 -*-
from xivo_dao.alchemy import dbconnection
from xivo_dao.alchemy.stat_queue_periodic import StatQueuePeriodic
from sqlalchemy.sql.functions import max


_DB_NAME = 'asterisk'


def _session():
    connection = dbconnection.get_connection(_DB_NAME)
    return connection.get_session()


def insert_stats(stats, period_start):
    for queue_id, queue_stats in stats.iteritems():
        entry = StatQueuePeriodic()
        entry.time = period_start
        if 'abandoned' in queue_stats:
            entry.abandoned = queue_stats['abandoned']
        if 'answered' in queue_stats:
            entry.answered = queue_stats['answered']
        if 'full' in queue_stats:
            entry.full = queue_stats['full']
        if 'joinempty' in queue_stats:
            entry.joinempty = queue_stats['joinempty']
        if 'closed' in queue_stats:
            entry.closed = queue_stats['closed']
        if 'timeout' in queue_stats:
            entry.timeout = queue_stats['timeout']
        entry.total = queue_stats['total']
        entry.queue_id = queue_id

        _session().add(entry)

    _session().commit()


def get_most_recent_time():
    res = _session().query(max(StatQueuePeriodic.time))
    if res[0][0] is None:
        raise LookupError('table empty')
    return res[0][0]


def clean_table():
    _session().query(StatQueuePeriodic).delete()
    _session().commit()
