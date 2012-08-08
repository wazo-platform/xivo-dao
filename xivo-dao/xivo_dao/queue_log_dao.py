# -*- coding: UTF-8 -*-
import datetime
import re

from collections import namedtuple

from sqlalchemy import between, distinct
from sqlalchemy.sql.expression import and_
from sqlalchemy.sql.functions import min
from xivo_dao.alchemy import dbconnection
from xivo_dao.alchemy.queue_log import QueueLog
from sqlalchemy import literal_column, cast, TIMESTAMP


_DB_NAME = 'asterisk'
_STR_TIME_FMT = "%Y-%m-%d %H:%M:%S.%f"
_TIME_STRING_PATTERN = re.compile('(\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+).?(\d+)?')
_MAP_QUEUE_LOG_WAITTIME = {'answered': QueueLog.data1,
                           'abandoned': QueueLog.data3,
                           'timeout': QueueLog.data3}
FIRST_EVENT = ['FULL', 'ENTERQUEUE', 'CLOSED', 'JOINEMPTY']
WAIT_TIME_EVENT = ['CONNECT', 'LEAVEEMPTY', 'EXITWITHTIMEOUT', 'ABANDON']

CallStart = namedtuple('CallStart', ['callid', 'event', 'time', 'queuename'])


def _session():
    connection = dbconnection.get_connection(_DB_NAME)
    return connection.get_session()


def _get_queue_event_call(start, end, event_filter, name):
    start = start.strftime(_STR_TIME_FMT)
    end = end.strftime(_STR_TIME_FMT)

    waittime_column = _MAP_QUEUE_LOG_WAITTIME.get(name, literal_column('0'))

    res = (_session()
           .query(QueueLog.queuename,
                  cast(QueueLog.time, TIMESTAMP).label('time'),
                  QueueLog.callid,
                  waittime_column.label('waittime'))
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
                    .query(QueueLog.callid,
                           cast(QueueLog.time, TIMESTAMP).label('time'))
                    .filter(and_(QueueLog.event == 'ENTERQUEUE',
                                 between(QueueLog.time, start, end))))

    enter_map = {}
    for enter_queue in enter_queues:
        enter_map[enter_queue.callid] = enter_queue.time

    if match == 'CONNECT':
        match = ['CONNECT', 'COMPLETECALLER', 'COMPLETEAGENT', 'TRANSFER']
    else:
        match = [match]

    res = (_session()
           .query(QueueLog.event,
                  QueueLog.queuename,
                  cast(QueueLog.time, TIMESTAMP).label('time'),
                  QueueLog.callid,
                  QueueLog.agent,
                  QueueLog.data1,
                  QueueLog.data2,
                  QueueLog.data3,
                  QueueLog.data4)
           .filter(and_(QueueLog.event.in_(match),
                        QueueLog.callid.in_(enter_map))))

    ret = {}
    for r in res:
        if r.callid not in ret:
            ret[r.callid] = {
                'callid': r.callid,
                'queue_name': r.queuename,
                'time': enter_map[r.callid],
                'event': event,
                'talktime': 0
                }
        if r.agent:
            ret[r.callid]['agent'] = r.agent
        if r.event in WAIT_TIME_EVENT:
            if r.event == 'LEAVEEMPTY':
                waittime = _time_diff(enter_map[r.callid], r.time)
                ret[r.callid]['waittime'] = waittime
            elif r.event == 'CONNECT':
                ret[r.callid]['waittime'] = int(r.data1)
            else:
                ret[r.callid]['waittime'] = int(r.data3)
        elif r.event in ['COMPLETECALLER', 'COMPLETEAGENT']:
            ret[r.callid]['talktime'] = int(r.data2)
        elif r.event == 'TRANSFER':
            ret[r.callid]['talktime'] = int(r.data4)

    return ret.values()


def get_queue_abandoned_call(start, end):
    return _get_event_with_enterqueue(start, end, 'ABANDON', 'abandoned')


def get_queue_answered_call(start, end):
    start = start.strftime(_STR_TIME_FMT)
    end = end.strftime(_STR_TIME_FMT)

    entered_in_range = (_session()
                        .query(QueueLog.callid)
                        .filter(and_(QueueLog.callid != 'NONE',
                                     QueueLog.event == 'ENTERQUEUE',
                                     between(QueueLog.time, start, end)))).subquery()

    call_ids_answered_in_range = (_session()
                         .query(QueueLog.callid)
                         .filter(and_(QueueLog.callid.in_(entered_in_range),
                                      QueueLog.event == 'CONNECT'))).subquery()

    answered_calls = (_session()
                      .query(QueueLog.callid,
                             QueueLog.queuename,
                             QueueLog.event,
                             cast(QueueLog.time, TIMESTAMP).label('time'),
                             QueueLog.agent,
                             QueueLog.data1,
                             QueueLog.data2,
                             QueueLog.data3,
                             QueueLog.data4)
                      .filter(QueueLog.callid.in_(call_ids_answered_in_range))).yield_per(100)

    res = {}
    for c in answered_calls:
        if c.callid not in res:
            res[c.callid] = {
                'callid': c.callid,
                'queue_name': c.queuename,
                'event': 'answered',
                'talktime': 0,
                }
        if c.agent:
            res[c.callid]['agent'] = c.agent
        if c.event == 'ENTERQUEUE':
            res[c.callid]['time'] = c.time
        if c.event in WAIT_TIME_EVENT:
            if c.event == 'CONNECT':
                res[c.callid]['waittime'] = int(c.data1) if c.data1 else 0
            else:
                res[c.callid]['waittime'] = int(c.data3) if c.data3 else 0
        elif c.event in ['COMPLETEAGENT', 'COMPLETECALLER']:
            res[c.callid]['talktime'] = int(c.data2) if c.data2 else 0
        elif c.event == 'TRANSFER':
            res[c.callid]['talktime'] = int(c.data4) if c.data2 else 0

    return res.values()


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
    return dict([(r.callid, r.time)
                 for r in (_session()
                           .query(QueueLog.callid,
                                  cast(QueueLog.time, TIMESTAMP).label('time'))
                           .filter(and_(QueueLog.event == 'ENTERQUEUE',
                                        QueueLog.callid.in_(callids))))])


def _time_str_to_datetime(s):
    if not s:
        raise LookupError
    m = _TIME_STRING_PATTERN.match(s)
    return datetime.datetime(int(m.group(1)),
                             int(m.group(2)),
                             int(m.group(3)),
                             int(m.group(4)),
                             int(m.group(5)),
                             int(m.group(6)),
                             int(m.group(7)) if m.group(7) else 0)


def get_first_time():
    return _session().query(cast(min(QueueLog.time), TIMESTAMP))[0][0]


def get_queue_names_in_range(start, end):
    start = start.strftime(_STR_TIME_FMT)
    end = end.strftime(_STR_TIME_FMT)

    return [r[0] for r in (_session().query(distinct(QueueLog.queuename))
                                  .filter(between(QueueLog.time, start, end)))]


def get_agents_after(start):
    s = start.strftime(_STR_TIME_FMT)

    return [r.agent for r in (_session()
                              .query(distinct(QueueLog.agent).label('agent'))
                              .filter(QueueLog.time >= s))]


def get_started_calls(start, end):
    start = start.strftime(_STR_TIME_FMT)
    end = end.strftime(_STR_TIME_FMT)

    rows = (_session().query(QueueLog.callid,
                             QueueLog.event,
                             cast(QueueLog.time, TIMESTAMP).label('time'),
                             QueueLog.queuename)
            .filter(and_(between(QueueLog.time, start, end),
                         QueueLog.event.in_(FIRST_EVENT))))

    return [CallStart(*row) for row in rows]
