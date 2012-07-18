# -*- coding: UTF-8 -*-
import datetime
import re

from sqlalchemy import between, distinct
from sqlalchemy.sql.expression import and_, or_
from sqlalchemy.sql.functions import min
from xivo_dao.alchemy import dbconnection
from xivo_dao.alchemy.queue_log import QueueLog
from sqlalchemy import literal_column


_DB_NAME = 'asterisk'
_STR_TIME_FMT = "%Y-%m-%d %H:%M:%S.%f"
_TIME_STRING_PATTERN = r'(\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+).?(\d+)?'
_MAP_QUEUE_LOG_WAITTIME = {'answered': QueueLog.data1,
                           'abandoned': QueueLog.data3,
                           'timeout': QueueLog.data3}


def _session():
    connection = dbconnection.get_connection(_DB_NAME)
    return connection.get_session()


def _get_queue_event_call(start, end, event_filter, name):
    start = start.strftime(_STR_TIME_FMT)
    end = end.strftime(_STR_TIME_FMT)

    waittime_column = _MAP_QUEUE_LOG_WAITTIME.get(name, literal_column('0'))

    res = (_session()
           .query(QueueLog.queuename, QueueLog.time, QueueLog.callid, waittime_column.label('waittime'))
           .filter(and_(QueueLog.event == event_filter,
                        between(QueueLog.time, start, end))))

    return [{'queue_name': r.queuename,
             'event': name,
             'time': r.time,
             'callid': r.callid,
             'waittime': int(r.waittime) if r.waittime else 0} for r in res]


def get_queue_full_call(start, end):
    return _get_queue_event_call(start, end, 'FULL', 'full')


def get_queue_closed_call(start, end):
    return _get_queue_event_call(start, end, 'CLOSED', 'closed')


def get_queue_abandoned_call(start, end):
    return _get_queue_event_call(start, end, 'ABANDON', 'abandoned')


def get_queue_answered_call(start, end):
    return _get_queue_event_call(start, end, 'CONNECT', 'answered')


def get_queue_joinempty_call(start, end):
    return _get_queue_event_call(start, end, 'JOINEMPTY', 'joinempty')


def get_queue_leaveempty_call(start, end):
    start = start.strftime(_STR_TIME_FMT)
    end = end.strftime(_STR_TIME_FMT)

    res = (_session()
           .query(QueueLog.event, QueueLog.queuename, QueueLog.time, QueueLog.callid)
           .filter(and_
                   (or_(QueueLog.event == 'LEAVEEMPTY',
                        QueueLog.event == 'ENTERQUEUE'),
                    between(QueueLog.time, start, end))))

    time_map = get_enterqueue_time([r.callid for r in res])

    ret = list()
    for r in res:
        if r.event == 'LEAVEEMPTY':
            try:
                waittime = _time_diff(time_map[r.callid], _time_str_to_datetime(r.time))
            except KeyError:
                waittime = 0
            ret.append({'queue_name': r.queuename,
                        'event': 'leaveempty',
                        'time': r.time,
                        'callid': r.callid,
                        'waittime': waittime})

    return ret


def _time_diff(start, end):
    delta = end - start
    return delta.seconds + int(round(delta.microseconds / 1000000.0))


def get_enterqueue_time(callids):
    return dict([(r.callid, _time_str_to_datetime(r.time))
                 for r in (_session().query(QueueLog.callid, QueueLog.time)
                           .filter(and_(QueueLog.event == 'ENTERQUEUE',
                                        QueueLog.callid.in_(callids))))])


def get_queue_timeout_call(start, end):
    return _get_queue_event_call(start, end, 'EXITWITHTIMEOUT', 'timeout')


def _time_str_to_datetime(s):
    m = re.match(_TIME_STRING_PATTERN, s)
    return datetime.datetime(int(m.group(1)),
                             int(m.group(2)),
                             int(m.group(3)),
                             int(m.group(4)),
                             int(m.group(5)),
                             int(m.group(6)),
                             int(m.group(7)) if m.group(7) else 0)


def get_first_time():
    return _time_str_to_datetime(_session().query(min(QueueLog.time))[0][0])


def get_queue_names_in_range(start, end):
    start = start.strftime(_STR_TIME_FMT)
    end = end.strftime(_STR_TIME_FMT)

    return [r[0] for r in (_session().query(distinct(QueueLog.queuename))
                                  .filter(between(QueueLog.time, start, end)))]
