# -*- coding: utf-8 -*-

from datetime import datetime as dt

from xivo_dao.alchemy.queue_log import QueueLog
from xivo_dao.alchemy.stat_call_on_queue import StatCallOnQueue
from xivo_dao.alchemy.stat_agent import StatAgent
from xivo_dao.alchemy.stat_queue import StatQueue
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao import stat_dao


class TestStatDAO(DAOTestCase):

    tables = [StatAgent, StatQueue, QueueLog, StatCallOnQueue]

    def setUp(self):
        self.empty_tables()

    def test_get_pause_intervals_in_range(self):
        _, agent_id_1 = self._insert_agent('Agent/1')
        start = dt(2012, 07, 01)
        end = dt(2012, 07, 31, 23, 59, 59, 999999)

        queue_log_data = '''\
| time                       | callid | queuename | agent   | event      | data1 | data2 | data3 | data4 | data5 |
| 2012-07-21 09:59:09.999999 | NONE   | NONE      | Agent/1 | PAUSEALL   |       |       |       |       |       |
| 2012-07-21 10:54:09.999999 | NONE   | NONE      | Agent/1 | UNPAUSEALL |       |       |       |       |       |
| 2012-07-21 23:59:19.999999 | NONE   | NONE      | Agent/1 | PAUSEALL   |       |       |       |       |       |
| 2012-07-22 02:02:19.999999 | NONE   | NONE      | Agent/1 | UNPAUSEALL |       |       |       |       |       |
'''

        self._insert_queue_log_data(queue_log_data)

        result = stat_dao.get_pause_intervals_in_range(start, end)
        for agent, logins in result.iteritems():
            result[agent] = sorted(logins, key=lambda login: login[0])

        expected = {
            agent_id_1: [
                (dt(2012, 7, 21, 9, 59, 9, 999999), dt(2012, 7, 21, 10, 54, 9, 999999)),
                (dt(2012, 7, 21, 23, 59, 19, 999999), dt(2012, 7, 22, 2, 2, 19, 999999))
            ]
        }

        self.assertEqual(expected, result)

    def test_get_pause_intervals_in_range_multiple_pauseall(self):
        _, agent_id_1 = self._insert_agent('Agent/1')
        start = dt(2012, 07, 01)
        end = dt(2012, 07, 31, 23, 59, 59, 999999)

        queue_log_data = '''\
| time                       | callid | queuename | agent   | event      | data1 | data2 | data3 | data4 | data5 |
| 2012-07-21 09:54:09.999999 | NONE   | NONE      | Agent/1 | PAUSEALL   |       |       |       |       |       |
| 2012-07-21 09:59:09.999999 | NONE   | NONE      | Agent/1 | PAUSEALL   |       |       |       |       |       |
| 2012-07-21 10:54:09.999999 | NONE   | NONE      | Agent/1 | UNPAUSEALL |       |       |       |       |       |
| 2012-07-21 23:59:19.999999 | NONE   | NONE      | Agent/1 | PAUSEALL   |       |       |       |       |       |
| 2012-07-22 02:02:19.999999 | NONE   | NONE      | Agent/1 | UNPAUSEALL |       |       |       |       |       |
'''

        self._insert_queue_log_data(queue_log_data)

        result = stat_dao.get_pause_intervals_in_range(start, end)
        for agent, logins in result.iteritems():
            result[agent] = sorted(logins, key=lambda login: login[0])

        expected = {
            agent_id_1: [
                (dt(2012, 7, 21, 9, 54, 9, 999999), dt(2012, 7, 21, 10, 54, 9, 999999)),
                (dt(2012, 7, 21, 23, 59, 19, 999999), dt(2012, 7, 22, 2, 2, 19, 999999))
            ]
        }

        self.assertEqual(result, expected)

    def _insert_queue_log_data(self, queue_log_data):
        lines = queue_log_data.split('\n')
        lines.pop()
        header = self._strip_content_list(lines.pop(0).split('|')[1:-1])
        for line in lines:
            tmp = self._strip_content_list(line[1:-1].split('|'))
            data = dict(zip(header, tmp))
            queue_log = QueueLog(
                time=data['time'],
                callid=data['callid'],
                queuename=data['queuename'],
                agent=data['agent'],
                event=data['event'],
                data1=data['data1'],
                data2=data['data2'],
                data3=data['data3'],
                data4=data['data4'],
                data5=data['data5']
                )
            self.session.add(queue_log)

        self.session.commit()

    def _strip_content_list(self, lines):
        return [line.strip() for line in lines]

    def _insert_agent(self, aname):
        a = StatAgent(name=aname)
        self.session.add(a)
        self.session.commit()
        return a.name, a.id

    def _insert_queue(self, qname):
        q = StatQueue(name=qname)
        self.session.add(q)
        self.session.commit()
        return q.name, q.id

    @classmethod
    def _create_functions(cls):
        ### WARNING: These functions should always be the same as the one in baseconfig
        fill_simple_calls_fn = '''\
DROP FUNCTION IF EXISTS "fill_saturated_calls" (text, text);
DROP FUNCTION IF EXISTS "fill_simple_calls" (text, text);
CREATE FUNCTION "fill_simple_calls"(period_start text, period_end text)
  RETURNS void AS
$$
  INSERT INTO "stat_call_on_queue" (callid, "time", queue_id, status)
    SELECT
      callid,
      CAST ("time" AS TIMESTAMP) as "time",
      (SELECT id FROM stat_queue WHERE name=queuename) as queue_id,
      CASE WHEN event = 'FULL' THEN 'full'::call_exit_type
           WHEN event = 'DIVERT_CA_RATIO' THEN 'divert_ca_ratio'
           WHEN event = 'DIVERT_HOLDTIME' THEN 'divert_waittime'
           WHEN event = 'CLOSED' THEN 'closed'
           WHEN event = 'JOINEMPTY' THEN 'joinempty'
      END as status
    FROM queue_log
    WHERE event IN ('FULL', 'DIVERT_CA_RATIO', 'DIVERT_HOLDTIME', 'CLOSED', 'JOINEMPTY') AND
          "time" BETWEEN $1 AND $2;
$$
LANGUAGE SQL;
'''
        cls.session.execute(fill_simple_calls_fn)

        fill_answered_calls_fn = '''\
DROP FUNCTION IF EXISTS "fill_answered_calls" (text, text);
CREATE FUNCTION "fill_answered_calls"(period_start text, period_end text)
  RETURNS void AS
$$
  INSERT INTO stat_call_on_queue (callid, "time", talktime, waittime, queue_id, agent_id, status)
  SELECT
    outer_queue_log.callid,
    CAST ((SELECT "time"
           FROM queue_log
           WHERE callid=outer_queue_log.callid AND
                 queuename=outer_queue_log.queuename AND
                 event='ENTERQUEUE' ORDER BY "time" DESC LIMIT 1) AS TIMESTAMP) AS "time",
    CASE WHEN event IN ('COMPLETEAGENT', 'COMPLETECALLER') THEN CAST (data2 AS INTEGER)
         WHEN event = 'TRANSFER' THEN CAST (data4 AS INTEGER) END as talktime,
    CASE WHEN event IN ('COMPLETEAGENT', 'COMPLETECALLER') THEN CAST (data1 AS INTEGER)
         WHEN event = 'TRANSFER' THEN CAST (data3 AS INTEGER) END as waittime,
    (SELECT id FROM stat_queue WHERE "name"=outer_queue_log.queuename) AS queue_id,
    (SELECT id FROM stat_agent WHERE "name"=outer_queue_log.agent) AS agent_id,
    'answered' AS status
  FROM
    queue_log as outer_queue_log
  WHERE
    callid IN
      (SELECT callid
       FROM queue_log
       WHERE event = 'ENTERQUEUE' AND "time" BETWEEN $1 AND $2)
    AND event IN ('COMPLETEAGENT', 'COMPLETECALLER', 'TRANSFER');
$$
LANGUAGE SQL;
'''
        cls.session.execute(fill_answered_calls_fn)

        fill_leaveempty_calls_fn = '''\
DROP FUNCTION IF EXISTS "fill_leaveempty_calls" (text, text);
CREATE OR REPLACE FUNCTION "fill_leaveempty_calls" (period_start text, period_end text)
  RETURNS void AS
$$
INSERT INTO stat_call_on_queue (callid, time, waittime, queue_id, status)
SELECT
  callid,
  enter_time as time,
  EXTRACT(EPOCH FROM (leave_time - enter_time))::INTEGER as waittime,
  queue_id,
  'leaveempty' AS status
FROM (SELECT
        CAST (time AS TIMESTAMP) AS enter_time,
        (select CAST (time AS TIMESTAMP) from queue_log where callid=main.callid AND event='LEAVEEMPTY') AS leave_time,
        callid,
        (SELECT id FROM stat_queue WHERE name=queuename) AS queue_id
      FROM queue_log AS main
      WHERE callid IN (SELECT callid FROM queue_log WHERE event = 'LEAVEEMPTY')
            AND event = 'ENTERQUEUE'
            AND time BETWEEN $1 AND $2) AS first;
$$
LANGUAGE SQL;
'''
        cls.session.execute(fill_leaveempty_calls_fn)
