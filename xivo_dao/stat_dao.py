# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

_STR_TIME_FMT = "%Y-%m-%d %H:%M:%S.%f"


def fill_simple_calls(session, start, end):
    _run_sql_function_returning_void(
        session,
        start, end,
        'SELECT 1 AS place_holder FROM fill_simple_calls(:start, :end)'
    )


def fill_answered_calls(session, start, end):
    _run_sql_function_returning_void(
        session,
        start, end,
        'SELECT 1 AS place_holder FROM fill_answered_calls(:start, :end)'
    )


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
    AND time::TIMESTAMP >= :start
    ORDER BY agent, time DESC
  ) AS pauseall, stat_agent
  WHERE stat_agent.name = agent
  GROUP BY stat_agent.id, unpauseall
'''

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

    for agent, logins in results.iteritems():
        logins = _pick_longest_with_same_end(logins)
        unique_result[agent] = sorted(list(set(logins)))

    return unique_result


def _merge_agent_statistics(*args):
    result = {}

    for stat in args:
        for agent, logins in stat.iteritems():
            if agent not in result:
                result[agent] = logins
            else:
                result[agent].extend(logins)

    for agent, logins in result.iteritems():
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
    for end, starts in end_time_map.iteritems():
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
    event like 'AGENT%LOGOFF' AND
    data1 <> '' AND
    data2::INTEGER > 0
)

SELECT
    agent_logins.login_timestamp,
    agent_logins.logout_timestamp,
    stat_agent.id AS agent
FROM
    stat_agent
    INNER JOIN agent_logins
        ON agent_logins.agent = stat_agent.name
WHERE
    agent_logins.logout_timestamp > :start
    AND agent_logins.logout_timestamp <= :end
ORDER BY
    agent_logins.agent, agent_logins.logout_timestamp
'''

    rows = session.query(
        'agent',
        'login_timestamp',
        'logout_timestamp'
    ).from_statement(completed_logins_query).params(start=start, end=end)

    results = {}

    for row in rows.all():
        if row.agent not in results:
            results[row.agent] = []
        login = row.login_timestamp if row.login_timestamp > start else start
        logout = row.logout_timestamp if row.logout_timestamp < end else end
        results[row.agent].append((login, logout))

    return results


def _get_ongoing_logins(session, start, end):
    last_logins, last_logouts = _get_last_logins_and_logouts(session)

    def filter_ended_logins(logins, logouts):
        filtered_logins = {}
        for agent, login in logins.iteritems():
            if not login:
                continue

            logout = logouts[agent]
            if not logout or logout < login:
                filtered_logins[agent] = login if login > start else start

        return filtered_logins

    filtered_logins = filter_ended_logins(last_logins, last_logouts)

    results = {}

    for agent, login in filtered_logins.iteritems():
        if agent not in results:
            results[agent] = []
        results[agent].append((login, end))

    return results


def _get_last_logins_and_logouts(session):
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
'''
    rows = session.query(
        'agent',
        'login',
        'logout',
    ).from_statement(query)

    agent_last_logins = {}
    agent_last_logouts = {}

    for row in rows:
        agent = row.agent
        agent_last_logins[agent] = row.login
        agent_last_logouts[agent] = row.logout

    return agent_last_logins, agent_last_logouts
