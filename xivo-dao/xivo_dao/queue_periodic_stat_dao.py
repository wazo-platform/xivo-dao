# -*- coding: UTF-8 -*-
from xivo_dao.alchemy import dbconnection
from xivo_dao.alchemy.queue_periodic_stat import QueuePeriodicStat


_DB_NAME = 'asterisk'


def _session():
    connection = dbconnection.get_connection(_DB_NAME)
    return connection.get_session()


def insert_stats(stats, period_start):
    entry = QueuePeriodicStat()
    entry.time = period_start
    entry.full = stats['full']
    entry.total = stats['total']

    _session().add(entry)
    _session().commit()
