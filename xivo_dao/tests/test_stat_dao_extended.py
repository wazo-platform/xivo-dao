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

import six

from datetime import datetime as dt

from xivo_dao import stat_dao
from xivo_dao.alchemy.queue_log import QueueLog
from xivo_dao.alchemy.stat_agent import StatAgent
from xivo_dao.alchemy.stat_queue import StatQueue
from xivo_dao.helpers.db_utils import flush_session
from xivo_dao.tests.test_dao import DAOTestCase


class TestStatDAO(DAOTestCase):

    def test_get_completed_logins(self):
        _, agent_id_1 = self._insert_agent('Agent/1')
        _, agent_id_2 = self._insert_agent('Agent/2')
        start = dt(2012, 6, 1)
        end = dt(2012, 6, 1, 23, 59, 59, 999999)

        queue_log_data = '''\
| time                       | callid   | queuename | agent   | event               | data1        | data2 | data3         | data4 | data5 |
| 2012-05-31 22:00:00.000000 | logout_0 | NONE      | Agent/1 | AGENTCALLBACKLOGOFF | 1001@default | 25200 | CommandLogoff |       |       |
| 2012-05-31 23:00:00.000000 | login_1  | NONE      | Agent/1 | AGENTCALLBACKLOGIN  | 1001@default |       |               |       |       |
| 2012-06-01 00:00:00.000000 | agent_2  | NONE      | Agent/2 | AGENTCALLBACKLOGIN  | 1002@default |       |               |       |       |
| 2012-06-01 06:00:00.000000 | logout_1 | NONE      | Agent/1 | AGENTCALLBACKLOGOFF | 1001@default | 25200 | CommandLogoff |       |       |
| 2012-06-01 06:05:00.000000 | NONE     | NONE      | Agent/1 | AGENTCALLBACKLOGIN  | 1001@default |       |               |       |       |
| 2012-06-01 06:30:00.000000 | NONE     | NONE      | Agent/1 | AGENTCALLBACKLOGOFF | 1001@default |  1500 | CommandLogoff |       |       |
| 2012-06-01 06:30:00.000001 | agent_2  | NONE      | Agent/2 | AGENTCALLBACKLOGOFF | 1002@default | 23400 | CommandLogoff |       |       |
| 2012-06-01 06:40:00.000000 | login_3  | NONE      | Agent/1 | AGENTLOGIN          | SIP/abc-1234 |       |               |       |       |
| 2012-06-01 06:45:00.000000 | login_3  | NONE      | Agent/1 | AGENTCALLBACKLOGOFF | SIP/abc-1234 |   300 | CommandLogoff |       |       |
'''

        self._insert_queue_log_data(queue_log_data)

        result = stat_dao._get_completed_logins(self.session, start, end)

        expected = {
            agent_id_1: [
                (start, dt(2012, 6, 1, 6)),
                (dt(2012, 6, 1, 6, 5), dt(2012, 6, 1, 6, 30)),
                (dt(2012, 6, 1, 6, 40), dt(2012, 6, 1, 6, 45)),
            ],
            agent_id_2: [
                (dt(2012, 6, 1, 0, 0, 0, 1), dt(2012, 6, 1, 6, 30, 0, 1)),
            ],
        }

        self.assertEqual(result, expected)

    def test_get_last_logouts(self):
        _, agent_id_1 = self._insert_agent('Agent/1')
        _, agent_id_2 = self._insert_agent('Agent/2')
        _, agent_id_3 = self._insert_agent('Agent/3')
        start = dt(2012, 6, 1)
        end = dt(2012, 6, 1, 23, 59, 59, 999999)

        start = dt(2012, 5, 31)
        end = dt(2012, 6, 1, 23, 59, 59, 999999)

        queue_log_data = '''\
| time                       | callid   | queuename | agent   | event               | data1        | data2 | data3         | data4 | data5 |
| 2012-05-31 22:00:00.000000 | logout_0 | NONE      | Agent/1 | AGENTCALLBACKLOGOFF | 1001@default | 25200 | CommandLogoff |       |       |
| 2012-05-31 23:00:00.000000 | login_1  | NONE      | Agent/1 | AGENTCALLBACKLOGIN  | 1001@default |       |               |       |       |
| 2012-06-01 00:00:00.000000 | agent_2  | NONE      | Agent/2 | AGENTCALLBACKLOGIN  | 1002@default |       |               |       |       |
| 2012-06-01 06:00:00.000000 | logout_1 | NONE      | Agent/1 | AGENTCALLBACKLOGOFF | 1001@default | 25200 | CommandLogoff |       |       |
| 2012-06-01 06:05:00.000000 | NONE     | NONE      | Agent/1 | AGENTCALLBACKLOGIN  | 1001@default |       |               |       |       |
| 2012-06-01 06:30:00.000000 | NONE     | NONE      | Agent/1 | AGENTCALLBACKLOGOFF | 1001@default |  1500 | CommandLogoff |       |       |
| 2012-06-01 06:30:00.000001 | agent_2  | NONE      | Agent/2 | AGENTCALLBACKLOGOFF | 1002@default | 23400 | CommandLogoff |       |       |
| 2012-06-01 06:40:00.000000 | login_3  | NONE      | Agent/1 | AGENTLOGIN          | SIP/abc-1234 |       |               |       |       |
| 2012-06-01 06:45:00.000000 | login_3  | NONE      | Agent/1 | AGENTCALLBACKLOGOFF | SIP/abc-1234 |   300 | CommandLogoff |       |       |
'''

        self._insert_queue_log_data(queue_log_data)

        _, result = stat_dao._get_last_logins_and_logouts(self.session, start, end)

        expected = {
            agent_id_1: dt(2012, 6, 1, 6, 45),
            agent_id_2: dt(2012, 6, 1, 6, 30, 0, 1),
        }

        self.assertEqual(result, expected)

    def test_get_last_logins(self):
        _, agent_id_1 = self._insert_agent('Agent/1')
        _, agent_id_2 = self._insert_agent('Agent/2')
        _, agent_id_3 = self._insert_agent('Agent/3')
        start = dt(2012, 6, 1)
        end = dt(2012, 6, 1, 23, 59, 59, 999999)

        queue_log_data = '''\
| time                       | callid     | queuename | agent   | event               | data1        | data2 | data3         | data4 | data5 |
| 2012-01-01 10:00:00.000000 | agent_3    | NONE      | Agent/3 | AGENTCALLBACKLOGIN  | 1003@default |       |               |       |       |
| 2012-05-31 20:00:00.000000 | not_logged | NONE      | Agent/1 | AGENTLOGIN          | SIP/abc-1234 |       |               |       |       |
| 2012-05-31 22:00:00.000000 | logout_0   | NONE      | Agent/1 | AGENTCALLBACKLOGOFF | 1001@default | 25200 | CommandLogoff |       |       |
| 2012-05-31 23:00:00.000000 | login_1    | NONE      | Agent/1 | AGENTCALLBACKLOGIN  | 1001@default |       |               |       |       |
| 2012-06-01 00:00:00.000000 | agent_2    | NONE      | Agent/2 | AGENTCALLBACKLOGIN  | 1002@default |       |               |       |       |
| 2012-06-01 06:00:00.000000 | logout_1   | NONE      | Agent/1 | AGENTCALLBACKLOGOFF | 1001@default | 25200 | CommandLogoff |       |       |
| 2012-06-01 06:05:00.000000 | NONE       | NONE      | Agent/1 | AGENTCALLBACKLOGIN  | 1001@default |       |               |       |       |
| 2012-06-01 06:30:00.000000 | NONE       | NONE      | Agent/1 | AGENTCALLBACKLOGOFF | 1001@default |  1500 | CommandLogoff |       |       |
| 2012-06-01 06:30:00.000001 | agent_2    | NONE      | Agent/2 | AGENTCALLBACKLOGOFF | 1002@default | 23400 | CommandLogoff |       |       |
| 2012-06-01 06:40:00.000000 | login_3    | NONE      | Agent/1 | AGENTLOGIN          | SIP/abc-1234 |       |               |       |       |
| 2012-06-01 06:45:00.000000 | login_3    | NONE      | Agent/1 | AGENTCALLBACKLOGOFF | SIP/abc-1234 |   300 | CommandLogoff |       |       |
| 2012-06-01 09:00:00.000000 | agent_4    | NONE      | Agent/2 | AGENTCALLBACKLOGIN  | 1002@default |       |               |       |       |
'''

        self._insert_queue_log_data(queue_log_data)

        result, _ = stat_dao._get_last_logins_and_logouts(self.session, start, end)

        expected = {
            agent_id_1: dt(2012, 6, 1, 6, 40),
            agent_id_2: dt(2012, 6, 1, 9),
            agent_id_3: dt(2012, 1, 1, 10),
        }

        self.assertEqual(result, expected)

    def test_get_ongoing_logins(self):
        _, agent_id_1 = self._insert_agent('Agent/1')
        _, agent_id_2 = self._insert_agent('Agent/2')
        _, agent_id_3 = self._insert_agent('Agent/3')
        _, agent_id_4 = self._insert_agent('Agent/4')
        start = dt(2012, 6, 1)
        end = dt(2012, 6, 1, 23, 59, 59, 999999)

        queue_log_data = '''\
| time                       | callid     | queuename | agent   | event               | data1        | data2 | data3         | data4 | data5 |
| 2012-05-31 20:00:00.000000 | not_logged | NONE      | Agent/1 | AGENTLOGIN          | SIP/abc-1234 |       |               |       |       |
| 2012-05-31 22:00:00.000000 | logout_0   | NONE      | Agent/1 | AGENTCALLBACKLOGOFF | 1001@default | 25200 | CommandLogoff |       |       |
| 2012-05-31 23:00:00.000000 | login_1    | NONE      | Agent/1 | AGENTCALLBACKLOGIN  | 1001@default |       |               |       |       |
| 2012-06-01 00:00:00.000000 | agent_2    | NONE      | Agent/2 | AGENTCALLBACKLOGIN  | 1002@default |       |               |       |       |
| 2012-06-01 06:00:00.000000 | logout_1   | NONE      | Agent/1 | AGENTCALLBACKLOGOFF | 1001@default | 25200 | CommandLogoff |       |       |
| 2012-06-01 06:05:00.000000 | NONE       | NONE      | Agent/1 | AGENTCALLBACKLOGIN  | 1001@default |       |               |       |       |
| 2012-06-01 06:30:00.000000 | NONE       | NONE      | Agent/1 | AGENTCALLBACKLOGOFF | 1001@default |  1500 | CommandLogoff |       |       |
| 2012-06-01 06:30:00.000001 | agent_2    | NONE      | Agent/2 | AGENTCALLBACKLOGOFF | 1002@default | 23400 | CommandLogoff |       |       |
| 2012-06-01 06:40:00.000000 | login_3    | NONE      | Agent/1 | AGENTLOGIN          | SIP/abc-1234 |       |               |       |       |
| 2012-06-01 06:45:00.000000 | login_3    | NONE      | Agent/1 | AGENTCALLBACKLOGOFF | SIP/abc-1234 |   300 | CommandLogoff |       |       |
| 2012-06-01 09:00:00.000000 | agent_4    | NONE      | Agent/2 | AGENTCALLBACKLOGIN  | 1002@default |       |               |       |       |
| 2012-06-01 10:00:00.000000 | agent_5    | NONE      | Agent/4 | AGENTCALLBACKLOGOFF | 1004@default |   300 |               |       |       |
| 2012-01-01 10:00:00.000000 | agent_3    | NONE      | Agent/3 | AGENTCALLBACKLOGIN  | 1003@default |       |               |       |       |
'''

        self._insert_queue_log_data(queue_log_data)

        result = stat_dao._get_ongoing_logins(self.session, start, end)

        expected = {
            agent_id_2: [
                (dt(2012, 6, 1, 9), end),
            ],
            agent_id_3: [
                (start, end),
            ],
        }

        self.assertEqual(result, expected)

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

        result = stat_dao.get_pause_intervals_in_range(self.session, start, end)
        for agent, logins in six.iteritems(result):
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

        result = stat_dao.get_pause_intervals_in_range(self.session, start, end)
        for agent, logins in six.iteritems(result):
            result[agent] = sorted(logins, key=lambda login: login[0])

        expected = {
            agent_id_1: [
                (dt(2012, 7, 21, 9, 54, 9, 999999), dt(2012, 7, 21, 10, 54, 9, 999999)),
                (dt(2012, 7, 21, 23, 59, 19, 999999), dt(2012, 7, 22, 2, 2, 19, 999999))
            ]
        }

        self.assertEqual(result, expected)

    def _insert_queue_log_data(self, queue_log_data):
        with flush_session(self.session):
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

    def _strip_content_list(self, lines):
        return [line.strip() for line in lines]

    def _insert_agent(self, aname):
        a = StatAgent(name=aname)

        self.add_me(a)

        return a.name, a.id

    def _insert_queue(self, qname):
        q = StatQueue(name=qname)

        self.add_me(q)

        return q.name, q.id

    @classmethod
    def _create_functions(cls):
        # ## WARNING: These functions should always be the same as the one in baseconfig
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
