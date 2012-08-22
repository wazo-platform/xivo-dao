# -*- coding: UTF-8 -*-

from sqlalchemy import between, distinct
from sqlalchemy.sql.expression import and_
from sqlalchemy.sql.functions import min
from xivo_dao.alchemy import dbconnection
from xivo_dao.alchemy.queue_log import QueueLog
from sqlalchemy import cast, TIMESTAMP, func


_DB_NAME = 'asterisk'
_STR_TIME_FMT = "%Y-%m-%d %H:%M:%S.%f"


def _session():
    connection = dbconnection.get_connection(_DB_NAME)
    return connection.get_session()


def _get_event_with_enterqueue(start, end, match, event):
    start = start.strftime(_STR_TIME_FMT)
    end = end.strftime(_STR_TIME_FMT)

    enter_queues = (_session()
                    .query(QueueLog.callid,
                           cast(QueueLog.time, TIMESTAMP).label('time'))
                    .filter(and_(QueueLog.event == 'ENTERQUEUE',
                                 between(QueueLog.time, start, end))))

    enter_map = {}
    for enter_queue in enter_queues.all():
        enter_map[enter_queue.callid] = enter_queue.time

    if enter_map:
        res = (_session()
               .query(QueueLog.event,
                      QueueLog.queuename,
                      cast(QueueLog.time, TIMESTAMP).label('time'),
                      QueueLog.callid,
                      QueueLog.data3)
               .filter(and_(QueueLog.event == match,
                            QueueLog.callid.in_(enter_map))))

        for r in res.all():
            yield {
                'callid': r.callid,
                'queue_name': r.queuename,
                'time': enter_map[r.callid],
                'event': event,
                'talktime': 0,
                'waittime': int(r.data3)
                }


def get_queue_abandoned_call(start, end):
    return _get_event_with_enterqueue(start, end, 'ABANDON', 'abandoned')


def get_queue_timeout_call(start, end):
    return _get_event_with_enterqueue(start, end, 'EXITWITHTIMEOUT', 'timeout')


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


def delete_event_by_queue_between(event, qname, start, end):
    _session().query(QueueLog).filter(
        and_(QueueLog.event == event,
             QueueLog.queuename == qname,
             between(QueueLog.time, start, end))).delete(synchronize_session=False)
    _session().commit()


def insert_entry(time, callid, queue, agent, event, d1='', d2='', d3='', d4='', d5=''):
    entry = QueueLog(
        time=time,
        callid=callid,
        queuename=queue,
        agent=agent,
        event=event,
        data1=d1,
        data2=d2,
        data3=d3,
        data4=d4,
        data5=d5)
    _session().add(entry)
    _session().commit()


def hours_with_calls(start, end):
    start = start.strftime(_STR_TIME_FMT)
    end = end.strftime(_STR_TIME_FMT)

    hours = (_session()
             .query(distinct(func.date_trunc('hour', cast(QueueLog.time, TIMESTAMP))).label('time'))
             .filter(between(QueueLog.time, start, end)))

    for hour in hours.all():
        yield hour.time
