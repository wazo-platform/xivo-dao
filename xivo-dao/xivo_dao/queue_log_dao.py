# -*- coding: UTF-8 -*-
import datetime

from sqlalchemy import between, asc
from sqlalchemy.sql.expression import and_
from xivo_dao.alchemy import dbconnection
from xivo_dao.alchemy.queue_log import QueueLog

_DB_NAME = 'asterisk'
_STR_TIME_FMT = "%Y-%m-%d %H:%M:%S.%f"


def _session():
    connection = dbconnection.get_connection(_DB_NAME)
    return connection.get_session()


def get_queue_full_call(start, end):
    start = start.strftime(_STR_TIME_FMT)
    end = end.strftime(_STR_TIME_FMT)
    res = (_session()
           .query(QueueLog.queuename, QueueLog.time, QueueLog.callid)
           .filter(and_(QueueLog.event == 'FULL',
                        between(QueueLog.time, start, end))))
    return [{'queue_name': r.queuename,
             'event': 'full',
             'time': r.time,
             'callid': r.callid} for r in res]


def get_first_time():
    return datetime.datetime.strptime(
        _session().query(QueueLog.time).order_by(asc(QueueLog.time)).limit(1)[0].time,
        '%Y-%m-%d %H:%M:%S.%f')
