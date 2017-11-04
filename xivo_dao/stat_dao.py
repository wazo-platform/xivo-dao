# -*- coding: utf-8 -*-

# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+

import six

from sqlalchemy.sql import text

_STR_TIME_FMT = "%Y-%m-%d %H:%M:%S.%f"

FILL_ANSWERED_CALL_ON_QUEUE_QUERY = text('''\n
INSERT INTO stat_call_on_queue (callid, "time", talktime, waittime, queue_id, agent_id, status)
(
    WITH
    call_entries AS (
        SELECT
            callid, queuename, agent, time, event, data1, data2, data3, data4, data5
        FROM
            queue_log
        WHERE
            time BETWEEN :start AND :end
    ),
    call_start AS (
        SELECT
            callid, queuename, time
        FROM
            call_entries
        WHERE
            event = 'ENTERQUEUE'
    ),
    call_end AS (
        SELECT
            callid, queuename, agent, time,
            CASE
                WHEN event IN ('COMPLETEAGENT', 'COMPLETECALLER')
                    THEN CAST (data2 AS INTEGER)
                WHEN event IN ('BLINDTRANSFER', 'TRANSFER')
                    THEN CAST (data4 AS INTEGER)
                WHEN event = 'ATTENDEDTRANSFER' and data1 IN ('BRIDGE', 'APP')
                    THEN CAST (data4 AS INTEGER)
                WHEN event = 'ATTENDEDTRANSFER' and data1 = 'LINK'
                    THEN CAST (split_part(data5, '|', 1) AS INTEGER)
            END as talktime,
            CASE
                WHEN event IN ('COMPLETEAGENT', 'COMPLETECALLER')
                    THEN CAST (data1 AS INTEGER)
                WHEN event IN ('BLINDTRANSFER', 'TRANSFER')
                    THEN CAST (data3 AS INTEGER)
                WHEN event = 'ATTENDEDTRANSFER' and data1 IN ('BRIDGE', 'APP')
                    THEN CAST (data3 AS INTEGER)
                WHEN event = 'ATTENDEDTRANSFER' and data1 = 'LINK'
                    THEN CAST (data4 AS INTEGER)
            END as waittime
        FROM
            call_entries
        WHERE
            event IN ('COMPLETEAGENT', 'COMPLETECALLER', 'ATTENDEDTRANSFER', 'BLINDTRANSFER', 'TRANSFER')
    ),
    completed_calls AS (
        SELECT
            call_end.callid,
            call_end.queuename,
            call_end.agent,
            call_start.time::TIMESTAMP,
            call_end.talktime,
            call_end.waittime
        FROM
            call_end
            INNER JOIN call_start
                ON call_end.callid = call_start.callid
                AND call_end.queuename = call_start.queuename
    ),
    partial_calls AS (
        SELECT
            call_end.callid,
            call_end.queuename,
            call_end.agent,
            call_end.time::TIMESTAMP
                - (call_end.talktime || ' seconds')::INTERVAL
                - (call_end.waittime || ' seconds')::INTERVAL
            AS time,
            call_end.talktime,
            call_end.waittime
        FROM
            call_end
            LEFT OUTER JOIN call_start
                ON call_end.callid = call_start.callid
                AND call_end.queuename = call_start.queuename
        WHERE
            call_start.callid IS NULL
    ),
    all_calls AS (
        SELECT * FROM completed_calls
        UNION
        SELECT * FROM partial_calls
    )

    SELECT
        all_calls.callid,
        all_calls.time,
        all_calls.talktime,
        all_calls.waittime,
        stat_queue.id as queue_id,
        stat_agent.id as agent_id,
        'answered' AS status
    FROM
        all_calls
    LEFT JOIN
        stat_agent ON all_calls.agent = stat_agent.name
    LEFT JOIN
        stat_queue ON all_calls.queuename = stat_queue.name
    ORDER BY
        all_calls.time
)
''')


def fill_simple_calls(session, start, end):
    _run_sql_function_returning_void(
        session,
        start, end,
        'SELECT 1 AS place_holder FROM fill_simple_calls(:start, :end)'
    )


def fill_answered_calls(session, start, end):
    params = {
        'start': start.strftime(_STR_TIME_FMT),
        'end': end.strftime(_STR_TIME_FMT),
    }

    session.execute(FILL_ANSWERED_CALL_ON_QUEUE_QUERY, params)


def fill_leaveempty_calls(session, start, end):
    _run_sql_function_returning_void(
        session,
        start, end,
        'SELECT 1 AS place_holder FROM fill_leaveempty_calls(:start, :end)'
    )


def _run_sql_function_returning_void(session, start, end, function):
    start = start.strftime(_STR_TIME_FMT)
    end = end.strftime(_STR_TIME_FMT)

    (session
     .query('place_holder')
     .from_statement(function)
     .params(start=start, end=end)
     .first())


def get_pause_intervals_in_range(session, start, end):
    pause_in_range = '''\
SELECT stat_agent.id AS agent,
       CAST(MIN(pauseall) AS TIMESTAMP) AS pauseall,
       CAST(unpauseall AS TIMESTAMP)
  FROM (
    SELECT agent, time AS pauseall,
      (
        SELECT time
        FROM queue_log
        WHERE event = 'UNPAUSEALL' AND
          agent = pause_all.agent AND
          time > pause_all.time
        ORDER BY time ASC limit 1
      ) AS unpauseall
    FROM queue_log AS pause_all
    WHERE event = 'PAUSEALL'
    AND time >= :start
    ORDER BY agent, time DESC
  ) AS pauseall, stat_agent
  WHERE stat_agent.name = agent
  GROUP BY stat_agent.id, unpauseall
'''

    start = start.strftime(_STR_TIME_FMT)
    end = end.strftime(_STR_TIME_FMT)

    rows = (session
            .query('agent', 'pauseall', 'unpauseall')
            .from_statement(pause_in_range)
            .params(start=start, end=end))

    results = {}

    for row in rows.all():
        agent_id = row.agent
        if agent_id not in results:
            results[agent_id] = []

        results[agent_id].append((row.pauseall, row.unpauseall))

    return results


def get_login_intervals_in_range(session, start, end):
    completed_logins = _get_completed_logins(session, start, end)
    ongoing_logins = _get_ongoing_logins(session, start, end)

    results = _merge_agent_statistics(
        completed_logins,
        ongoing_logins,
    )

    unique_result = {}

    for agent, logins in six.iteritems(results):
        logins = _pick_longest_with_same_end(logins)
        unique_result[agent] = sorted(list(set(logins)))

    return unique_result


def _merge_agent_statistics(*args):
    result = {}

    for stat in args:
        for agent, logins in six.iteritems(stat):
            if agent not in result:
                result[agent] = logins
            else:
                result[agent].extend(logins)

    for agent, logins in six.iteritems(result):
        filtered_logins = _filter_overlap(logins)
        result[agent] = filtered_logins

    return result


def _filter_overlap(items):
    starts = []
    ends = []
    result = []
    stack = []

    for item in items:
        starts.append(item[0])
        ends.append(item[1])

    starts = sorted(starts)
    ends = sorted(ends)

    starts.reverse()
    ends.reverse()

    while starts or ends:
        if starts and ends and starts[-1] < ends[-1]:
            start = starts.pop()
            stack.append(start)
        else:
            end = ends.pop()
            start = stack.pop()
            if not stack:
                result.append((start, end))

    return result


def _pick_longest_with_same_end(logins):
    """
    Workaround a bug in chan_agent.so where an agent could log multiple times
    Fixed in XiVO 12.18
    """
    end_time_map = {}
    for start, end in logins:
        if end not in end_time_map:
            end_time_map[end] = []
        end_time_map[end].append(start)

    res = []
    for end, starts in six.iteritems(end_time_map):
        res.append((min(starts), end))

    return res


def _get_completed_logins(session, start, end):
    completed_logins_query = '''\
WITH agent_logins AS (
SELECT
    agent,
    CAST(time AS TIMESTAMP) AS logout_timestamp,
    CAST(time as TIMESTAMP) - (data2 || ' seconds')::INTERVAL AS login_timestamp
FROM
    queue_log
WHERE
    event like 'AGENT%LOGOFF'
    AND data1 <> ''
    AND data2::INTEGER > 0
    AND time > :start
    AND time <= :end
)

SELECT
    agent_logins.login_timestamp,
    agent_logins.logout_timestamp,
    stat_agent.id AS agent
FROM
    stat_agent
    INNER JOIN agent_logins
        ON agent_logins.agent = stat_agent.name
ORDER BY
    agent_logins.agent, agent_logins.logout_timestamp
'''

    formatted_start = start.strftime(_STR_TIME_FMT)
    formatted_end = end.strftime(_STR_TIME_FMT)

    rows = (session.query('agent', 'login_timestamp', 'logout_timestamp')
            .from_statement(completed_logins_query)
            .params(start=formatted_start, end=formatted_end))

    results = {}

    for row in rows.all():
        if row.agent not in results:
            results[row.agent] = []
        login = row.login_timestamp if row.login_timestamp > start else start
        logout = row.logout_timestamp if row.logout_timestamp < end else end
        results[row.agent].append((login, logout))

    return results


def _get_ongoing_logins(session, start, end):
    last_logins, last_logouts = _get_last_logins_and_logouts(session, start, end)

    def filter_ended_logins(logins, logouts):
        filtered_logins = {}
        for agent, login in six.iteritems(logins):
            if not login:
                continue

            logout = logouts[agent]
            if not logout or logout < login:
                filtered_logins[agent] = login if login > start else start

        return filtered_logins

    filtered_logins = filter_ended_logins(last_logins, last_logouts)

    results = {}

    for agent, login in six.iteritems(filtered_logins):
        if agent not in results:
            results[agent] = []
        results[agent].append((login, end))

    return results


def _get_last_logins_and_logouts(session, start, end):
    query = '''\
SELECT
  stat_agent.id AS agent,
  CAST(MAX(case when event like '%LOGIN' then time end) AS TIMESTAMP) AS login,
  CAST(MAX(case when event like '%LOGOFF' then time end) AS TIMESTAMP) AS logout
FROM
  stat_agent
JOIN
  queue_log ON queue_log.agent = stat_agent.name
WHERE
  event LIKE 'AGENT%'
GROUP BY
  stat_agent.id
HAVING
  MAX(case when event like '%LOGIN' then time end) < :end
'''

    start = start.strftime(_STR_TIME_FMT)
    end = end.strftime(_STR_TIME_FMT)

    rows = session.query(
        'agent',
        'login',
        'logout',
    ).from_statement(query).params(start=start, end=end)

    agent_last_logins = {}
    agent_last_logouts = {}

    for row in rows:
        agent = row.agent
        agent_last_logins[agent] = row.login
        agent_last_logouts[agent] = row.logout

    return agent_last_logins, agent_last_logouts
