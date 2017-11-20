# -*- coding: utf-8 -*-
# Copyright (C) 2013-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy import between, distinct
from sqlalchemy.sql.expression import and_, or_
from sqlalchemy.sql.functions import min
from xivo_dao.alchemy.queue_log import QueueLog
from sqlalchemy import cast, TIMESTAMP, func
from datetime import timedelta
from xivo_dao.helpers.db_manager import daosession


_STR_TIME_FMT = "%Y-%m-%d %H:%M:%S.%f"


def get_wrapup_times(session, start, end, interval):
    before_start = start - timedelta(minutes=2)
    wrapup_times_query = '''\
SELECT
    CAST(queue_log.time AS TIMESTAMP) AS start,
    (CAST(queue_log.time AS TIMESTAMP) + (queue_log.data1 || ' seconds')::INTERVAL) AS end,
    stat_agent.id AS agent_id
FROM
    queue_log
INNER JOIN
    stat_agent ON stat_agent.name = queue_log.agent
WHERE
  queue_log.event = 'WRAPUPSTART'
AND
  queue_log.time BETWEEN :start AND :end
'''

    periods = [t for t in _enumerate_periods(start, end, interval)]
    formatted_start = before_start.strftime('%Y-%m-%d %H:%M:%S')
    formatted_end = end.strftime('%Y-%m-%d %H:%M:%S')

    rows = session.query(
        'start',
        'end',
        'agent_id'
    ).from_statement(wrapup_times_query).params(start=formatted_start,
                                                end=formatted_end)

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


def _get_ended_call(session, start_str, end, queue_log_event, stat_event):
    pairs = []
    enter_queue_event = None

    higher_boundary = end + timedelta(days=1)
    end_str = higher_boundary.strftime(_STR_TIME_FMT)

    queue_logs = (session
                  .query(QueueLog.event,
                         QueueLog.callid,
                         QueueLog.queuename,
                         QueueLog.data3,
                         cast(QueueLog.time, TIMESTAMP).label('time'))
                  .filter(and_(QueueLog.time >= start_str,
                               QueueLog.time < end_str,
                               or_(QueueLog.event == 'ENTERQUEUE',
                                   QueueLog.event == queue_log_event)))
                  .order_by(QueueLog.callid, QueueLog.time))

    to_skip = None
    for queue_log in queue_logs.all():
        # The first matched entry of a pair should be an ENTERQUEUE
        if enter_queue_event is None and queue_log.event != 'ENTERQUEUE':
            continue

        # When a callid reaches the end of the range, skip all other queue_log for this callid
        if to_skip and queue_log.callid == to_skip:
            continue

        if queue_log.event == 'ENTERQUEUE':
            # The ENTERQUEUE happenned after the range, skip this callid
            if queue_log.time > end:
                to_skip = queue_log.callid
                continue

            # Found a ENTERQUEUE
            enter_queue_event = queue_log
            continue

        # Only ended calls can reach this line
        end_event = queue_log

        # Does it have a matching ENTERQUEUE?
        if end_event.callid != enter_queue_event.callid:
            continue

        pairs.append((enter_queue_event, end_event))

    for enter_queue, end_event in pairs:
        yield {
            'callid': enter_queue.callid,
            'queue_name': enter_queue.queuename,
            'time': enter_queue.time,
            'event': stat_event,
            'talktime': 0,
            'waittime': int(end_event.data3),
        }


def get_queue_abandoned_call(session, start, end):
    start_str = start.strftime(_STR_TIME_FMT)
    return _get_ended_call(session, start_str, end, 'ABANDON', 'abandoned')


def get_queue_timeout_call(session, start, end):
    start_str = start.strftime(_STR_TIME_FMT)
    return _get_ended_call(session, start_str, end, 'EXITWITHTIMEOUT', 'timeout')


def get_first_time(session):
    res = session.query(cast(min(QueueLog.time), TIMESTAMP)).first()[0]
    if res is None:
        raise LookupError('Table is empty')
    return res


def get_queue_names_in_range(session, start, end):
    start = start.strftime(_STR_TIME_FMT)
    end = end.strftime(_STR_TIME_FMT)

    return [r[0] for r in (session.query(distinct(QueueLog.queuename))
                           .filter(between(QueueLog.time, start, end)))]


@daosession
def delete_event_by_queue_between(session, event, qname, start, end):
    session.query(QueueLog).filter(
        and_(QueueLog.event == event,
             QueueLog.queuename == qname,
             between(QueueLog.time, start, end))).delete(synchronize_session='fetch')


@daosession
def delete_event_between(session, start, end):
    session.query(QueueLog).filter(
        and_(between(QueueLog.time, start, end))).delete(synchronize_session='fetch')


@daosession
def insert_entry(session, time, callid, queue, agent, event, d1='', d2='', d3='', d4='', d5=''):
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
    session.add(entry)


def hours_with_calls(session, start, end):
    start = start.strftime(_STR_TIME_FMT)
    end = end.strftime(_STR_TIME_FMT)

    hours = (session
             .query(distinct(func.date_trunc('hour', cast(QueueLog.time, TIMESTAMP))).label('time'))
             .filter(between(QueueLog.time, start, end)))

    for hour in hours.all():
        yield hour.time


@daosession
def get_last_callid_with_event_for_agent(session, event, agent):
    row = session.query(QueueLog.callid).filter(
        and_(QueueLog.agent == agent,
             QueueLog.event == event)).order_by(QueueLog.time.desc()).first()

    return row.callid
