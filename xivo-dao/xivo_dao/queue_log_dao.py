# -*- coding: UTF-8 -*-

from sqlalchemy import between, distinct
from sqlalchemy.sql.expression import and_
from sqlalchemy.sql.functions import min
from xivo_dao.alchemy import dbconnection
from xivo_dao.alchemy.queue_log import QueueLog
from sqlalchemy import cast, TIMESTAMP, func
from datetime import timedelta


_DB_NAME = 'asterisk'
_STR_TIME_FMT = "%Y-%m-%d %H:%M:%S.%f"


def _session():
    connection = dbconnection.get_connection(_DB_NAME)
    return connection.get_session()


def get_wrapup_times(start, end, interval):
    before_start = start - timedelta(minutes=2)
    wrapup_times_query = '''\
SELECT
  CAST(queue_log.time AS TIMESTAMP) AS start,
  (CAST(queue_log.time AS TIMESTAMP) + (queue_log.data1 || ' seconds')::INTERVAL) AS end,
  stat_agent.id AS agent_id
FROM
  queue_log,
  stat_agent
WHERE
  stat_agent.name = queue_log.agent
AND
  queue_log.event = 'WRAPUPSTART'
AND
  queue_log.time::TIMESTAMP BETWEEN :start AND :end
'''

    periods = [t for t in _enumerate_periods(start, end, interval)]

    rows = _session().query(
        'start',
        'end',
        'agent_id'
    ).from_statement(wrapup_times_query).params(start=before_start,
                                                end=end)

    results = {}
    for row in rows.all():
        agent_id, wstart, wend = row.agent_id, row.start, row.end

        starting_period = _find_including_period(periods, wstart)
        ending_period = _find_including_period(periods, wend)

        if starting_period and starting_period not in results:
            results[starting_period] = {}
        if ending_period and ending_period not in results:
            results[ending_period] = {}

        if starting_period is not None:
            range_end = starting_period + interval
            wend_in_start = wend if wend < range_end else range_end
            time_in_period = wend_in_start - wstart
            if agent_id not in results[starting_period]:
                results[starting_period][agent_id] = {
                    'wrapup_time': timedelta(seconds=0)
                }
            results[starting_period][agent_id]['wrapup_time'] += time_in_period

        if ending_period == starting_period:
            continue

        time_in_period = wend - ending_period
        if agent_id not in results[ending_period]:
            results[ending_period][agent_id] = {
                'wrapup_time': timedelta(seconds=0)
            }
        results[ending_period][agent_id]['wrapup_time'] += time_in_period

    return results


def _find_including_period(periods, t):
    match = None
    for period in periods:
        if t > period:
            match = period
    return match


def _enumerate_periods(start, end, interval):
    tmp = start
    while tmp <= end:
        yield tmp
        tmp += interval


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
                'waittime': int(r.data3) if r.data3 else 0
            }


def get_queue_abandoned_call(start, end):
    return _get_event_with_enterqueue(start, end, 'ABANDON', 'abandoned')


def get_queue_timeout_call(start, end):
    return _get_event_with_enterqueue(start, end, 'EXITWITHTIMEOUT', 'timeout')


def get_first_time():
    res = _session().query(cast(min(QueueLog.time), TIMESTAMP)).first()[0]
    if res is None:
        raise LookupError('Table is empty')
    return res


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


def delete_event_between(start, end):
    _session().query(QueueLog).filter(
        and_(between(QueueLog.time, start, end))).delete(synchronize_session=False)
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


def get_last_callid_with_event_for_agent(event, agent):
    row = _session().query(QueueLog.callid).filter(
        and_(QueueLog.agent == agent,
             QueueLog.event == event)).order_by(QueueLog.time.desc()).first()

    return row.callid
