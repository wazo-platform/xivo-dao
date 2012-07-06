# -*- coding: UTF-8 -*-

from xivo_dao.alchemy.queue_log import QueueLog
from xivo_dao.alchemy import dbconnection
from sqlalchemy import between
from sqlalchemy.sql.expression import and_

_DB_NAME = 'asterisk'


def _session():
    connection = dbconnection.get_connection(_DB_NAME)
    return connection.get_session()


def get_queue_full_call(start, end):
    res = (_session()
           .query(QueueLog.queuename, QueueLog.time, QueueLog.callid)
           .filter(and_(QueueLog.event == 'FULL', between(QueueLog.time, start, end))))
    return [{'queue_name': r.queuename,
             'event': 'full',
             'time': r.time,
             'callid': r.callid} for r in res]
