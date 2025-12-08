# Copyright 2013-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import itertools
import pathlib
from collections.abc import Iterator
from datetime import datetime as dt
from typing import Any

from hamcrest import assert_that, equal_to
from pytz import UTC
from sqlalchemy import text
from sqlalchemy.engine import Engine

from xivo_dao import stat_dao
from xivo_dao.alchemy.queue_log import QueueLog
from xivo_dao.alchemy.stat_agent import StatAgent
from xivo_dao.alchemy.stat_call_on_queue import StatCallOnQueue
from xivo_dao.alchemy.stat_queue import StatQueue
from xivo_dao.helpers.db_utils import flush_session
from xivo_dao.tests.test_dao import DAOTestCase


def parse_fields(line):
    return [
        cleaned_field for field in line.split('|') if (cleaned_field := field.strip())
    ]


def parse_table(data: str) -> Iterator[dict[str, Any]]:
    lines = [
        cleaned_line for line in data.split('\n') if (cleaned_line := line.strip())
    ]
    header = parse_fields(lines.pop(0))
    for line in lines:
        fields = parse_fields(line)
        data = dict(zip(header, fields))
        yield data


def group_by(iterable, group_key):
    return (
        (key, list(group))
        for key, group in itertools.groupby(
            sorted(iterable, key=group_key), key=group_key
        )
    )


class TestStatDAO(DAOTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._create_functions(cls.engine)

    def test_fill_leaveempty_calls_fallover(self):
        queue_log_data = '''
        | id      | callid            | event            | queuename | time                          |
        | 4893491 | 1681282818.209622 | ENTERQUEUE       | queue1    | 2023-04-12 07:00:36.992026+00 |
        | 4893492 | 1681282818.209622 | EXITEMPTY        | queue1    | 2023-04-12 07:00:37.008464+00 |
        | 4893493 | 1681282818.209622 | LEAVEEMPTY       | queue1    | 2023-04-12 07:00:37.025775+00 |
        | 4893494 | 1681282818.209622 | ENTERQUEUE       | queue2    | 2023-04-12 07:00:37.206645+00 |
        | 4893495 | 1681282818.209622 | RINGNOANSWER     | queue2    | 2023-04-12 07:00:52.252287+00 |
        | 4893502 | 1681282818.209622 | RINGNOANSWER     | queue2    | 2023-04-12 07:01:08.287469+00 |
        | 4893505 | 1681282818.209622 | RINGNOANSWER     | queue2    | 2023-04-12 07:01:24.31699+00  |
        | 4893509 | 1681282818.209622 | CONNECT          | queue2    | 2023-04-12 07:01:29.36803+00  |
        | 4893701 | 1681282818.209622 | COMPLETEAGENT    | queue2    | 2023-04-12 07:06:48.84232+00  |
        | 4893702 | 1681282818.209622 | WRAPUPSTART      | queue2    | 2023-04-12 07:06:48.856337+00 |
        '''
        queue_logs = self._insert_queue_log_data(queue_log_data)
        assert_that(self.session.query(QueueLog).count(), equal_to(10))

        queues = {log.queuename for log in queue_logs}
        for queue in queues:
            self._insert_queue(queue)

        start = min(log.time for log in queue_logs)
        end = max(log.time for log in queue_logs)

        stat_dao.fill_leaveempty_calls(self.session, start, end)

        result = (
            self.session.query(StatCallOnQueue)
            .filter(StatCallOnQueue.time >= start, StatCallOnQueue.time <= end)
            .all()
        )
        stat_coq_by_queue = group_by(
            result, group_key=lambda call: call.stat_queue.name
        )
        logs_by_queue = dict(group_by(queue_logs, group_key=lambda log: log.queuename))
        for queuename, stat_calls in stat_coq_by_queue:
            with self.subTest(queue=queuename):
                logs = logs_by_queue[queuename]
                leaveempty_queuelogs_count = sum(
                    1 for log in logs if log.event == 'LEAVEEMPTY'
                )
                calls_on_queue_leaveempty_count = sum(
                    1 for call in stat_calls if call.status == 'leaveempty'
                )
                assert_that(
                    calls_on_queue_leaveempty_count,
                    equal_to(leaveempty_queuelogs_count),
                )

    def test_fill_leaveempty_calls_reenter_same_queue(self):
        queue_log_data = '''
        | id      | callid            | event          | queuename | time                          |
        | 4902659 | 1681302917.231273 | ENTERQUEUE     | queue1    | 2023-04-12 12:35:36.686525+00 |
        | 4902660 | 1681302917.231273 | EXITEMPTY      | queue1    | 2023-04-12 12:35:36.716105+00 |
        | 4902661 | 1681302917.231273 | LEAVEEMPTY     | queue1    | 2023-04-12 12:35:36.745441+00 |
        | 4902662 | 1681302917.231273 | ENTERQUEUE     | queue2    | 2023-04-12 12:35:37.060998+00 |
        | 4902740 | 1681302917.231273 | RINGNOANSWER   | queue2    | 2023-04-12 12:36:59.165529+00 |
        | 4902761 | 1681302917.231273 | CONNECT        | queue2    | 2023-04-12 12:37:25.938767+00 |
        | 4902834 | 1681302917.231273 | BLINDTRANSFER  | queue2    | 2023-04-12 12:39:02.737237+00 |
        | 4902835 | 1681302917.231273 | WRAPUPSTART    | queue2    | 2023-04-12 12:39:02.822856+00 |
        | 4902851 | 1681302917.231273 | ENTERQUEUE     | queue1    | 2023-04-12 12:39:33.717291+00 |
        | 4902852 | 1681302917.231273 | EXITEMPTY      | queue1    | 2023-04-12 12:39:33.764423+00 |
        | 4902853 | 1681302917.231273 | LEAVEEMPTY     | queue1    | 2023-04-12 12:39:33.799041+00 |
        | 4902854 | 1681302917.231273 | ENTERQUEUE     | queue2    | 2023-04-12 12:39:34.163929+00 |
        | 4902973 | 1681302917.231273 | CONNECT        | queue2    | 2023-04-12 12:41:57.877111+00 |
        | 4903307 | 1681302917.231273 | COMPLETECALLER | queue2    | 2023-04-12 12:48:53.708396+00 |
        | 4903308 | 1681302917.231273 | WRAPUPSTART    | queue2    | 2023-04-12 12:48:53.718011+00 |
        '''
        queue_logs = self._insert_queue_log_data(queue_log_data)
        assert_that(self.session.query(QueueLog).count(), equal_to(15))

        queues = {log.queuename for log in queue_logs}
        for queue in queues:
            self._insert_queue(queue)

        start = min(log.time for log in queue_logs)
        end = max(log.time for log in queue_logs)

        stat_dao.fill_leaveempty_calls(self.session, start, end)

        result = (
            self.session.query(StatCallOnQueue)
            .filter(StatCallOnQueue.time >= start, StatCallOnQueue.time <= end)
            .all()
        )
        stat_coq_by_queue = group_by(
            result, group_key=lambda call: call.stat_queue.name
        )
        logs_by_queue = dict(group_by(queue_logs, group_key=lambda log: log.queuename))
        for queuename, stat_calls in stat_coq_by_queue:
            with self.subTest(queue=queuename):
                logs = logs_by_queue[queuename]
                leaveempty_queuelogs_count = sum(
                    1 for log in logs if log.event == 'LEAVEEMPTY'
                )
                calls_on_queue_leaveempty_count = sum(
                    1 for call in stat_calls if call.status == 'leaveempty'
                )
                assert_that(
                    calls_on_queue_leaveempty_count,
                    equal_to(leaveempty_queuelogs_count),
                )

    def test_get_completed_logins(self):
        self.add_context(name='default')
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
| 2012-06-01 06:40:00.000000+00 | login_3  | NONE      | Agent/1 | AGENTCALLBACKLOGIN  | 1001@default |       |               |       |       |
| 2012-06-01 06:45:00.000000+00 | login_3  | NONE      | Agent/1 | AGENTCALLBACKLOGOFF | 1001@default |   300 | CommandLogoff |       |       |
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
                (
                    dt(2012, 6, 1, 0, 0, 0, 1, tzinfo=UTC),
                    dt(2012, 6, 1, 6, 30, 0, 1, tzinfo=UTC),
                ),
            ],
        }

        assert result == expected

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
| 2012-06-01 06:40:00.000000+00 | login_3  | NONE      | Agent/1 | AGENTCALLBACKLOGIN  | 1001@default |       |               |       |       |
| 2012-06-01 06:45:00.000000+00 | login_3  | NONE      | Agent/1 | AGENTCALLBACKLOGOFF | 1001@default |   300 | CommandLogoff |       |       |
'''

        self._insert_queue_log_data(queue_log_data)

        _, result = stat_dao._get_last_logins_and_logouts(self.session, start, end)

        expected = {
            agent_id_1: dt(2012, 6, 1, 6, 45, tzinfo=UTC),
            agent_id_2: dt(2012, 6, 1, 6, 30, 0, 1, tzinfo=UTC),
        }

        assert result == expected

    def test_get_last_logins(self):
        _, agent_id_1 = self._insert_agent('Agent/1')
        _, agent_id_2 = self._insert_agent('Agent/2')
        _, agent_id_3 = self._insert_agent('Agent/3')
        start = dt(2012, 6, 1, tzinfo=UTC)
        end = dt(2012, 6, 1, 23, 59, 59, 999999, tzinfo=UTC)

        queue_log_data = '''\
| time                          | callid     | queuename | agent   | event               | data1        | data2 | data3         | data4 | data5 |
| 2012-01-01 10:00:00.000000+00 | agent_3    | NONE      | Agent/3 | AGENTCALLBACKLOGIN  | 1003@default |       |               |       |       |
| 2012-05-31 20:00:00.000000+00 | not_logged | NONE      | Agent/1 | AGENTCALLBACKLOGIN  | 1001@default |       |               |       |       |
| 2012-05-31 22:00:00.000000+00 | logout_0   | NONE      | Agent/1 | AGENTCALLBACKLOGOFF | 1001@default | 25200 | CommandLogoff |       |       |
| 2012-05-31 23:00:00.000000+00 | login_1    | NONE      | Agent/1 | AGENTCALLBACKLOGIN  | 1001@default |       |               |       |       |
| 2012-06-01 00:00:00.000000+00 | agent_2    | NONE      | Agent/2 | AGENTCALLBACKLOGIN  | 1002@default |       |               |       |       |
| 2012-06-01 06:00:00.000000+00 | logout_1   | NONE      | Agent/1 | AGENTCALLBACKLOGOFF | 1001@default | 25200 | CommandLogoff |       |       |
| 2012-06-01 06:05:00.000000+00 | NONE       | NONE      | Agent/1 | AGENTCALLBACKLOGIN  | 1001@default |       |               |       |       |
| 2012-06-01 06:30:00.000000+00 | NONE       | NONE      | Agent/1 | AGENTCALLBACKLOGOFF | 1001@default |  1500 | CommandLogoff |       |       |
| 2012-06-01 06:30:00.000001+00 | agent_2    | NONE      | Agent/2 | AGENTCALLBACKLOGOFF | 1002@default | 23400 | CommandLogoff |       |       |
| 2012-06-01 06:40:00.000000+00 | login_3    | NONE      | Agent/1 | AGENTCALLBACKLOGIN  | 1001@default |       |               |       |       |
| 2012-06-01 06:45:00.000000+00 | login_3    | NONE      | Agent/1 | AGENTCALLBACKLOGOFF | 1001@default |   300 | CommandLogoff |       |       |
| 2012-06-01 09:00:00.000000+00 | agent_4    | NONE      | Agent/2 | AGENTCALLBACKLOGIN  | 1002@default |       |               |       |       |
'''

        self._insert_queue_log_data(queue_log_data)

        result, _ = stat_dao._get_last_logins_and_logouts(self.session, start, end)

        expected = {
            agent_id_1: dt(2012, 6, 1, 6, 40, tzinfo=UTC),
            agent_id_2: dt(2012, 6, 1, 9, tzinfo=UTC),
            agent_id_3: dt(2012, 1, 1, 10, tzinfo=UTC),
        }

        assert result == expected

    def test_get_ongoing_logins(self):
        _, agent_id_1 = self._insert_agent('Agent/1')
        _, agent_id_2 = self._insert_agent('Agent/2')
        _, agent_id_3 = self._insert_agent('Agent/3')
        _, agent_id_4 = self._insert_agent('Agent/4')
        start = dt(2012, 6, 1, tzinfo=UTC)
        end = dt(2012, 6, 1, 23, 59, 59, 999999, tzinfo=UTC)

        queue_log_data = '''\
| time                          | callid     | queuename | agent   | event               | data1        | data2 | data3         | data4 | data5 |
| 2012-05-31 20:00:00.000000+00 | not_logged | NONE      | Agent/1 | AGENTCALLBACKLOGIN  | 1001@default |       |               |       |       |
| 2012-05-31 22:00:00.000000+00 | logout_0   | NONE      | Agent/1 | AGENTCALLBACKLOGOFF | 1001@default | 25200 | CommandLogoff |       |       |
| 2012-05-31 23:00:00.000000+00 | login_1    | NONE      | Agent/1 | AGENTCALLBACKLOGIN  | 1001@default |       |               |       |       |
| 2012-06-01 00:00:00.000000+00 | agent_2    | NONE      | Agent/2 | AGENTCALLBACKLOGIN  | 1002@default |       |               |       |       |
| 2012-06-01 06:00:00.000000+00 | logout_1   | NONE      | Agent/1 | AGENTCALLBACKLOGOFF | 1001@default | 25200 | CommandLogoff |       |       |
| 2012-06-01 06:05:00.000000+00 | NONE       | NONE      | Agent/1 | AGENTCALLBACKLOGIN  | 1001@default |       |               |       |       |
| 2012-06-01 06:30:00.000000+00 | NONE       | NONE      | Agent/1 | AGENTCALLBACKLOGOFF | 1001@default |  1500 | CommandLogoff |       |       |
| 2012-06-01 06:30:00.000001+00 | agent_2    | NONE      | Agent/2 | AGENTCALLBACKLOGOFF | 1002@default | 23400 | CommandLogoff |       |       |
| 2012-06-01 06:40:00.000000+00 | login_3    | NONE      | Agent/1 | AGENTCALLBACKLOGIN  | 1001@default |       |               |       |       |
| 2012-06-01 06:45:00.000000+00 | login_3    | NONE      | Agent/1 | AGENTCALLBACKLOGOFF | 1001@default |   300 | CommandLogoff |       |       |
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

        assert result == expected

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
                ),
            ]
        }

        assert expected == result

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
                ),
            ]
        }

        assert result == expected

    def _insert_queue_log_data(self, queue_log_data):
        with flush_session(self.session):
            logs = parse_table(queue_log_data)
            queue_logs = [QueueLog(**data) for data in logs]
            self.session.add_all(queue_logs)
        self.session.expire_all()
        return queue_logs

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
    def _create_functions(cls, con: Engine):
        # ## WARNING: These functions should always be the same as the one in baseconfig
        fill_simple_calls_fn = (
            pathlib.Path(__file__)
            .parent.joinpath('helpers/fill_simple_calls.sql')
            .read_text()
        )
        with con.begin() as connection:
            connection.execute(text(fill_simple_calls_fn))

        fill_leaveempty_calls_fn = (
            pathlib.Path(__file__)
            .parent.joinpath('helpers/fill_leaveempty_calls.sql')
            .read_text()
        )
        with con.begin() as connection:
            connection.execute(text(fill_leaveempty_calls_fn))
