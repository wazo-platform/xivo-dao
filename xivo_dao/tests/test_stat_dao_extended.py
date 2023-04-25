# Copyright 2013-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import pathlib
from datetime import datetime as dt
from pytz import UTC
from sqlalchemy import text

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
        start = dt(2012, 6, 1, tzinfo=UTC)
        end = dt(2012, 6, 1, 23, 59, 59, 999999, tzinfo=UTC)

        queue_log_data = '''\
| time                          | callid   | queuename | agent   | event               | data1        | data2 | data3         | data4 | data5 |
| 2012-05-31 22:00:00.000000+00 | logout_0 | NONE      | Agent/1 | AGENTCALLBACKLOGOFF | 1001@default | 25200 | CommandLogoff |       |       |
| 2012-05-31 23:00:00.000000+00 | login_1  | NONE      | Agent/1 | AGENTCALLBACKLOGIN  | 1001@default |       |               |       |       |
| 2012-06-01 00:00:00.000000+00 | agent_2  | NONE      | Agent/2 | AGENTCALLBACKLOGIN  | 1002@default |       |               |       |       |
| 2012-06-01 06:00:00.000000+00 | logout_1 | NONE      | Agent/1 | AGENTCALLBACKLOGOFF | 1001@default | 25200 | CommandLogoff |       |       |
| 2012-06-01 06:05:00.000000+00 | NONE     | NONE      | Agent/1 | AGENTCALLBACKLOGIN  | 1001@default |       |               |       |       |
| 2012-06-01 06:30:00.000000+00 | NONE     | NONE      | Agent/1 | AGENTCALLBACKLOGOFF | 1001@default |  1500 | CommandLogoff |       |       |
| 2012-06-01 06:30:00.000001+00 | agent_2  | NONE      | Agent/2 | AGENTCALLBACKLOGOFF | 1002@default | 23400 | CommandLogoff |       |       |
| 2012-06-01 06:40:00.000000+00 | login_3  | NONE      | Agent/1 | AGENTLOGIN          | SIP/abc-1234 |       |               |       |       |
| 2012-06-01 06:45:00.000000+00 | login_3  | NONE      | Agent/1 | AGENTCALLBACKLOGOFF | SIP/abc-1234 |   300 | CommandLogoff |       |       |
'''

        self._insert_queue_log_data(queue_log_data)

        result = stat_dao._get_completed_logins(self.session, start, end)

        expected = {
            agent_id_1: [
                (start, dt(2012, 6, 1, 6, tzinfo=UTC)),
                (dt(2012, 6, 1, 6, 5, tzinfo=UTC), dt(2012, 6, 1, 6, 30, tzinfo=UTC)),
                (dt(2012, 6, 1, 6, 40, tzinfo=UTC), dt(2012, 6, 1, 6, 45, tzinfo=UTC)),
            ],
            agent_id_2: [
                (dt(2012, 6, 1, 0, 0, 0, 1, tzinfo=UTC), dt(2012, 6, 1, 6, 30, 0, 1, tzinfo=UTC)),
            ],
        }

        self.assertEqual(result, expected)

    def test_get_last_logouts(self):
        _, agent_id_1 = self._insert_agent('Agent/1')
        _, agent_id_2 = self._insert_agent('Agent/2')
        _, agent_id_3 = self._insert_agent('Agent/3')
        start = dt(2012, 5, 31, tzinfo=UTC)
        end = dt(2012, 6, 1, 23, 59, 59, 999999, tzinfo=UTC)

        queue_log_data = '''\
| time                          | callid   | queuename | agent   | event               | data1        | data2 | data3         | data4 | data5 |
| 2012-05-31 22:00:00.000000+00 | logout_0 | NONE      | Agent/1 | AGENTCALLBACKLOGOFF | 1001@default | 25200 | CommandLogoff |       |       |
| 2012-05-31 23:00:00.000000+00 | login_1  | NONE      | Agent/1 | AGENTCALLBACKLOGIN  | 1001@default |       |               |       |       |
| 2012-06-01 00:00:00.000000+00 | agent_2  | NONE      | Agent/2 | AGENTCALLBACKLOGIN  | 1002@default |       |               |       |       |
| 2012-06-01 06:00:00.000000+00 | logout_1 | NONE      | Agent/1 | AGENTCALLBACKLOGOFF | 1001@default | 25200 | CommandLogoff |       |       |
| 2012-06-01 06:05:00.000000+00 | NONE     | NONE      | Agent/1 | AGENTCALLBACKLOGIN  | 1001@default |       |               |       |       |
| 2012-06-01 06:30:00.000000+00 | NONE     | NONE      | Agent/1 | AGENTCALLBACKLOGOFF | 1001@default |  1500 | CommandLogoff |       |       |
| 2012-06-01 06:30:00.000001+00 | agent_2  | NONE      | Agent/2 | AGENTCALLBACKLOGOFF | 1002@default | 23400 | CommandLogoff |       |       |
| 2012-06-01 06:40:00.000000+00 | login_3  | NONE      | Agent/1 | AGENTLOGIN          | SIP/abc-1234 |       |               |       |       |
| 2012-06-01 06:45:00.000000+00 | login_3  | NONE      | Agent/1 | AGENTCALLBACKLOGOFF | SIP/abc-1234 |   300 | CommandLogoff |       |       |
'''

        self._insert_queue_log_data(queue_log_data)

        _, result = stat_dao._get_last_logins_and_logouts(self.session, start, end)

        expected = {
            agent_id_1: dt(2012, 6, 1, 6, 45, tzinfo=UTC),
            agent_id_2: dt(2012, 6, 1, 6, 30, 0, 1, tzinfo=UTC),
        }

        self.assertEqual(result, expected)

    def test_get_last_logins(self):
        _, agent_id_1 = self._insert_agent('Agent/1')
        _, agent_id_2 = self._insert_agent('Agent/2')
        _, agent_id_3 = self._insert_agent('Agent/3')
        start = dt(2012, 6, 1, tzinfo=UTC)
        end = dt(2012, 6, 1, 23, 59, 59, 999999, tzinfo=UTC)

        queue_log_data = '''\
| time                          | callid     | queuename | agent   | event               | data1        | data2 | data3         | data4 | data5 |
| 2012-01-01 10:00:00.000000+00 | agent_3    | NONE      | Agent/3 | AGENTCALLBACKLOGIN  | 1003@default |       |               |       |       |
| 2012-05-31 20:00:00.000000+00 | not_logged | NONE      | Agent/1 | AGENTLOGIN          | SIP/abc-1234 |       |               |       |       |
| 2012-05-31 22:00:00.000000+00 | logout_0   | NONE      | Agent/1 | AGENTCALLBACKLOGOFF | 1001@default | 25200 | CommandLogoff |       |       |
| 2012-05-31 23:00:00.000000+00 | login_1    | NONE      | Agent/1 | AGENTCALLBACKLOGIN  | 1001@default |       |               |       |       |
| 2012-06-01 00:00:00.000000+00 | agent_2    | NONE      | Agent/2 | AGENTCALLBACKLOGIN  | 1002@default |       |               |       |       |
| 2012-06-01 06:00:00.000000+00 | logout_1   | NONE      | Agent/1 | AGENTCALLBACKLOGOFF | 1001@default | 25200 | CommandLogoff |       |       |
| 2012-06-01 06:05:00.000000+00 | NONE       | NONE      | Agent/1 | AGENTCALLBACKLOGIN  | 1001@default |       |               |       |       |
| 2012-06-01 06:30:00.000000+00 | NONE       | NONE      | Agent/1 | AGENTCALLBACKLOGOFF | 1001@default |  1500 | CommandLogoff |       |       |
| 2012-06-01 06:30:00.000001+00 | agent_2    | NONE      | Agent/2 | AGENTCALLBACKLOGOFF | 1002@default | 23400 | CommandLogoff |       |       |
| 2012-06-01 06:40:00.000000+00 | login_3    | NONE      | Agent/1 | AGENTLOGIN          | SIP/abc-1234 |       |               |       |       |
| 2012-06-01 06:45:00.000000+00 | login_3    | NONE      | Agent/1 | AGENTCALLBACKLOGOFF | SIP/abc-1234 |   300 | CommandLogoff |       |       |
| 2012-06-01 09:00:00.000000+00 | agent_4    | NONE      | Agent/2 | AGENTCALLBACKLOGIN  | 1002@default |       |               |       |       |
'''

        self._insert_queue_log_data(queue_log_data)

        result, _ = stat_dao._get_last_logins_and_logouts(self.session, start, end)

        expected = {
            agent_id_1: dt(2012, 6, 1, 6, 40, tzinfo=UTC),
            agent_id_2: dt(2012, 6, 1, 9, tzinfo=UTC),
            agent_id_3: dt(2012, 1, 1, 10, tzinfo=UTC),
        }

        self.assertEqual(result, expected)

    def test_get_ongoing_logins(self):
        _, agent_id_1 = self._insert_agent('Agent/1')
        _, agent_id_2 = self._insert_agent('Agent/2')
        _, agent_id_3 = self._insert_agent('Agent/3')
        _, agent_id_4 = self._insert_agent('Agent/4')
        start = dt(2012, 6, 1, tzinfo=UTC)
        end = dt(2012, 6, 1, 23, 59, 59, 999999, tzinfo=UTC)

        queue_log_data = '''\
| time                          | callid     | queuename | agent   | event               | data1        | data2 | data3         | data4 | data5 |
| 2012-05-31 20:00:00.000000+00 | not_logged | NONE      | Agent/1 | AGENTLOGIN          | SIP/abc-1234 |       |               |       |       |
| 2012-05-31 22:00:00.000000+00 | logout_0   | NONE      | Agent/1 | AGENTCALLBACKLOGOFF | 1001@default | 25200 | CommandLogoff |       |       |
| 2012-05-31 23:00:00.000000+00 | login_1    | NONE      | Agent/1 | AGENTCALLBACKLOGIN  | 1001@default |       |               |       |       |
| 2012-06-01 00:00:00.000000+00 | agent_2    | NONE      | Agent/2 | AGENTCALLBACKLOGIN  | 1002@default |       |               |       |       |
| 2012-06-01 06:00:00.000000+00 | logout_1   | NONE      | Agent/1 | AGENTCALLBACKLOGOFF | 1001@default | 25200 | CommandLogoff |       |       |
| 2012-06-01 06:05:00.000000+00 | NONE       | NONE      | Agent/1 | AGENTCALLBACKLOGIN  | 1001@default |       |               |       |       |
| 2012-06-01 06:30:00.000000+00 | NONE       | NONE      | Agent/1 | AGENTCALLBACKLOGOFF | 1001@default |  1500 | CommandLogoff |       |       |
| 2012-06-01 06:30:00.000001+00 | agent_2    | NONE      | Agent/2 | AGENTCALLBACKLOGOFF | 1002@default | 23400 | CommandLogoff |       |       |
| 2012-06-01 06:40:00.000000+00 | login_3    | NONE      | Agent/1 | AGENTLOGIN          | SIP/abc-1234 |       |               |       |       |
| 2012-06-01 06:45:00.000000+00 | login_3    | NONE      | Agent/1 | AGENTCALLBACKLOGOFF | SIP/abc-1234 |   300 | CommandLogoff |       |       |
| 2012-06-01 09:00:00.000000+00 | agent_4    | NONE      | Agent/2 | AGENTCALLBACKLOGIN  | 1002@default |       |               |       |       |
| 2012-06-01 10:00:00.000000+00 | agent_5    | NONE      | Agent/4 | AGENTCALLBACKLOGOFF | 1004@default |   300 |               |       |       |
| 2012-01-01 10:00:00.000000+00 | agent_3    | NONE      | Agent/3 | AGENTCALLBACKLOGIN  | 1003@default |       |               |       |       |
'''

        self._insert_queue_log_data(queue_log_data)

        result = stat_dao._get_ongoing_logins(self.session, start, end)

        expected = {
            agent_id_2: [
                (dt(2012, 6, 1, 9, tzinfo=UTC), end),
            ],
            agent_id_3: [
                (start, end),
            ],
        }

        self.assertEqual(result, expected)

    def test_get_pause_intervals_in_range(self):
        _, agent_id_1 = self._insert_agent('Agent/1')
        start = dt(2012, 7, 1, tzinfo=UTC)
        end = dt(2012, 7, 31, 23, 59, 59, 999999, tzinfo=UTC)

        queue_log_data = '''\
| time                          | callid | queuename | agent   | event      | data1 | data2 | data3 | data4 | data5 |
| 2012-07-21 09:59:09.999999+00 | NONE   | NONE      | Agent/1 | PAUSEALL   |       |       |       |       |       |
| 2012-07-21 10:54:09.999999+00 | NONE   | NONE      | Agent/1 | UNPAUSEALL |       |       |       |       |       |
| 2012-07-21 23:59:19.999999+00 | NONE   | NONE      | Agent/1 | PAUSEALL   |       |       |       |       |       |
| 2012-07-22 02:02:19.999999+00 | NONE   | NONE      | Agent/1 | UNPAUSEALL |       |       |       |       |       |
'''

        self._insert_queue_log_data(queue_log_data)

        result = stat_dao.get_pause_intervals_in_range(self.session, start, end)
        for agent, logins in result.items():
            result[agent] = sorted(logins, key=lambda login: login[0])

        expected = {
            agent_id_1: [
                (
                    dt(2012, 7, 21, 9, 59, 9, 999999, tzinfo=UTC),
                    dt(2012, 7, 21, 10, 54, 9, 999999, tzinfo=UTC),
                ),
                (
                    dt(2012, 7, 21, 23, 59, 19, 999999, tzinfo=UTC),
                    dt(2012, 7, 22, 2, 2, 19, 999999, tzinfo=UTC),
                )
            ]
        }

        self.assertEqual(expected, result)

    def test_get_pause_intervals_in_range_multiple_pauseall(self):
        _, agent_id_1 = self._insert_agent('Agent/1')
        start = dt(2012, 7, 1, tzinfo=UTC)
        end = dt(2012, 7, 31, 23, 59, 59, 999999, tzinfo=UTC)

        queue_log_data = '''\
| time                          | callid | queuename | agent   | event      | data1 | data2 | data3 | data4 | data5 |
| 2012-07-21 09:54:09.999999+00 | NONE   | NONE      | Agent/1 | PAUSEALL   |       |       |       |       |       |
| 2012-07-21 09:59:09.999999+00 | NONE   | NONE      | Agent/1 | PAUSEALL   |       |       |       |       |       |
| 2012-07-21 10:54:09.999999+00 | NONE   | NONE      | Agent/1 | UNPAUSEALL |       |       |       |       |       |
| 2012-07-21 23:59:19.999999+00 | NONE   | NONE      | Agent/1 | PAUSEALL   |       |       |       |       |       |
| 2012-07-22 02:02:19.999999+00 | NONE   | NONE      | Agent/1 | UNPAUSEALL |       |       |       |       |       |
'''

        self._insert_queue_log_data(queue_log_data)

        result = stat_dao.get_pause_intervals_in_range(self.session, start, end)
        for agent, logins in result.items():
            result[agent] = sorted(logins, key=lambda login: login[0])

        expected = {
            agent_id_1: [
                (
                    dt(2012, 7, 21, 9, 54, 9, 999999, tzinfo=UTC),
                    dt(2012, 7, 21, 10, 54, 9, 999999, tzinfo=UTC),
                ),
                (
                    dt(2012, 7, 21, 23, 59, 19, 999999, tzinfo=UTC),
                    dt(2012, 7, 22, 2, 2, 19, 999999, tzinfo=UTC),
                )
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

    def _insert_agent(self, aname, tenant_uuid=None):
        tenant_uuid = tenant_uuid or self.default_tenant.uuid
        a = StatAgent(name=aname, tenant_uuid=tenant_uuid)

        self.add_me(a)

        return a.name, a.id

    def _insert_queue(self, qname, tenant_uuid=None):
        tenant_uuid = tenant_uuid or self.default_tenant.uuid
        q = StatQueue(name=qname, tenant_uuid=tenant_uuid)

        self.add_me(q)

        return q.name, q.id

    @classmethod
    def _create_functions(cls, con):
        # ## WARNING: These functions should always be the same as the one in baseconfig
        fill_simple_calls_fn = pathlib.Path(__file__).parent.joinpath('helpers/fill_simple_calls.sql').read_text()
        con.execute(fill_simple_calls_fn)

        fill_leaveempty_calls_fn = pathlib.Path(__file__).parent.joinpath('helpers/fill_leaveempty_calls.sql').read_text()
        con.execute(fill_leaveempty_calls_fn)
