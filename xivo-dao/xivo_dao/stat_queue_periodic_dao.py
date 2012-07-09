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
        entry.full = queue_stats['full']
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
