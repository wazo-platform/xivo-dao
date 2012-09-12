# -*- coding: utf-8 -*-

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


def get_login_intervals_in_range(start, end):
    qry_string = '''\
SELECT
  stat_agent.id AS agent,
  CAST(time AS TIMESTAMP) AS logout,
  (
    SELECT CAST(time AS TIMESTAMP)
    FROM queue_log
    WHERE event IN ('AGENTCALLBACKLOGIN', 'AGENTLOGIN') AND
          agent = out.agent AND
          data1 = out.data1 AND
          time < out.time
    ORDER BY time DESC
    LIMIT 1
  ) AS login
FROM queue_log AS out,
     stat_agent
WHERE
  agent = stat_agent.name AND
  event IN ('AGENTCALLBACKLOGOFF', 'AGENTLOGOFF') AND
  data1 <> ''
ORDER BY time ASC
'''

    rows = (_get_session()
              .query('agent', 'login', 'logout')
              .from_statement(qry_string))

    results = {}

    for row in rows.all():
        if row[0] not in results:
            results[row[0]] = []
        results[row[0]].append((row[1], row[2]))

    return results
