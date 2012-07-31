# -*- coding: UTF-8 -*-
import datetime
import re

from sqlalchemy import between, distinct
from sqlalchemy.sql.expression import and_
from sqlalchemy.sql.functions import min
from xivo_dao.alchemy import dbconnection
from xivo_dao.alchemy.queue_log import QueueLog
from sqlalchemy import literal_column


_DB_NAME = 'asterisk'
_STR_TIME_FMT = "%Y-%m-%d %H:%M:%S.%f"
_TIME_STRING_PATTERN = re.compile('(\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+).?(\d+)?')
_MAP_QUEUE_LOG_WAITTIME = {'answered': QueueLog.data1,
                           'abandoned': QueueLog.data3,
                           'timeout': QueueLog.data3}
FIRST_EVENT = ['FULL', 'ENTERQUEUE', 'CLOSED', 'JOINEMPTY']


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


def _get_event_with_enterqueue(start, end, match, event):
    start = start.strftime(_STR_TIME_FMT)
    end = end.strftime(_STR_TIME_FMT)

    enter_queues = (_session()
                    .query(QueueLog.callid, QueueLog.time)
                    .filter(and_(QueueLog.event == 'ENTERQUEUE',
                                 between(QueueLog.time, start, end))))

    enter_map = {}
    for enter_queue in enter_queues:
        enter_map[enter_queue.callid] = _time_str_to_datetime(enter_queue.time)

    res = (_session()
           .query(QueueLog.event, QueueLog.queuename, QueueLog.time, QueueLog.callid)
           .filter(and_(QueueLog.event == match,
                        QueueLog.callid.in_(enter_map))))

    ret = list()
    for r in res:
        t = _time_str_to_datetime(r.time)
        waittime = _time_diff(enter_map[r.callid], t)
        ret.append({'queue_name': r.queuename,
                    'event': event,
                    'time': enter_map[r.callid],
                    'callid': r.callid,
                    'waittime': waittime})

    return ret


def get_queue_abandoned_call(start, end):
    return _get_event_with_enterqueue(start, end, 'ABANDON', 'abandoned')


def get_queue_answered_call(start, end):
    return _get_event_with_enterqueue(start, end, 'CONNECT', 'answered')


def get_queue_timeout_call(start, end):
    return _get_event_with_enterqueue(start, end, 'EXITWITHTIMEOUT', 'timeout')


def get_queue_joinempty_call(start, end):
    return _get_queue_event_call(start, end, 'JOINEMPTY', 'joinempty')


def get_queue_leaveempty_call(start, end):
    return _get_event_with_enterqueue(start, end, 'LEAVEEMPTY', 'leaveempty')


def _time_diff(start, end):
    delta = end - start
    return delta.seconds + int(round(delta.microseconds / 1000000.0))


def get_enterqueue_time(callids):
    return dict([(r.callid, _time_str_to_datetime(r.time))
                 for r in (_session().query(QueueLog.callid, QueueLog.time)
                           .filter(and_(QueueLog.event == 'ENTERQUEUE',
                                        QueueLog.callid.in_(callids))))])


def _time_str_to_datetime(s):
    m = _TIME_STRING_PATTERN.match(s)
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


def get_started_calls(start, end):
    start = start.strftime(_STR_TIME_FMT)
    end = end.strftime(_STR_TIME_FMT)

    rows = (_session().query(QueueLog.callid,
                             QueueLog.event,
                             QueueLog.time,
                             QueueLog.queuename)
            .filter(between(QueueLog.time, start, end))
            .filter(QueueLog.event.in_(FIRST_EVENT)))

    return [(r.callid, r.event,
             _time_str_to_datetime(r.time), r.queuename) for r in rows]
