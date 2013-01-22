# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

from xivo_dao.alchemy.dbconnection import get_connection

_STR_TIME_FMT = "%Y-%m-%d %H:%M:%S.%f"


def _get_session():
    return get_connection('asterisk').get_session()


def fill_simple_calls(start, end):
    _run_sql_function_returning_void(
        start, end,
        'SELECT 1 AS place_holder FROM fill_simple_calls(:start, :end)'
    )


def fill_answered_calls(start, end):
    _run_sql_function_returning_void(
        start, end,
        'SELECT 1 AS place_holder FROM fill_answered_calls(:start, :end)'
    )


def fill_leaveempty_calls(start, end):
    _run_sql_function_returning_void(
        start, end,
        'SELECT 1 AS place_holder FROM fill_leaveempty_calls(:start, :end)'
    )


def _run_sql_function_returning_void(start, end, function):
    start = start.strftime(_STR_TIME_FMT)
    end = end.strftime(_STR_TIME_FMT)

    (_get_session()
     .query('place_holder')
     .from_statement(function)
     .params(start=start, end=end)
     .first())


def get_pause_intervals_in_range(start, end):
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

    rows = (_get_session()
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


def get_login_intervals_in_range(start, end):
    completed_logins = get_completed_logins(start, end)
    ongoing_logins = get_ongoing_logins(start, end)

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


def get_completed_logins(start, end):
    completed_logins_query = '''\
SELECT
  logout_timestamp - login_delay AS login_timestamp,
  logout_timestamp,
  stat_agent.id AS agent
FROM
  stat_agent,
(SELECT
  CAST(time AS TIMESTAMP) as logout_timestamp,
  agent,
  (data2 || ' seconds')::INTERVAL AS login_delay
 FROM queue_log
  WHERE event like 'AGENT%LOGOFF' AND
  data1 <> '' AND
  data2::INTEGER > 0 AND
  time::TIMESTAMP >= :start) AS logouts
WHERE stat_agent.name = agent
ORDER BY agent, logout_timestamp
'''

    rows = _get_session().query(
        'agent',
        'login_timestamp',
        'logout_timestamp'
    ).from_statement(completed_logins_query).params(start=start)

    results = {}

    for row in rows.all():
        if row.agent not in results:
            results[row.agent] = []
        login = row.login_timestamp if row.login_timestamp > start else start
        logout = row.logout_timestamp if row.logout_timestamp < end else end
        results[row.agent].append((login, logout))

    return results


def _get_last_logouts():
    last_agent_logout_query = '''\
select
  stat_agent.id AS agent,
  (
   SELECT CAST(MAX(time) AS TIMESTAMP) as last_logout
   FROM queue_log
   WHERE queue_log.agent = stat_agent.name AND event LIKE 'AGENT%LOGOFF'
  ) AS logout
from stat_agent
'''

    rows = _get_session().query(
        'agent',
        'logout',
    ).from_statement(last_agent_logout_query)

    agents_last_logouts = {}

    for row in rows.all():
        agents_last_logouts[row.agent] = row.logout

    return agents_last_logouts


def _get_last_logins():
    last_agent_logout_query = '''\
SELECT
  stat_agent.id AS agent,
  CAST(MAX(time) AS TIMESTAMP) as login
FROM queue_log, stat_agent
WHERE agent = stat_agent.name AND
  event LIKE 'AGENT%LOGIN'
GROUP BY stat_agent.id
'''

    rows = _get_session().query(
        'agent',
        'login',
    ).from_statement(last_agent_logout_query)

    agents_last_logins = {}

    for row in rows.all():
        agents_last_logins[row.agent] = row.login

    return agents_last_logins


def get_ongoing_logins(start, end):
    last_logins = _get_last_logins()
    last_logouts = _get_last_logouts()

    def filter_ended_logins(logins, logouts):
        filtered_logins = {}
        for agent, login in logins.iteritems():
            if not logouts[agent] or logouts[agent] < login:
                filtered_logins[agent] = login if login > start else start

        return filtered_logins

    filtered_logins = filter_ended_logins(last_logins, last_logouts)

    results = {}

    for agent, login in filtered_logins.iteritems():
        if agent not in results:
            results[agent] = []
        results[agent].append((login, end))

    return results
