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

import datetime
from datetime import datetime as t

from xivo_dao import stat_dao
from xivo_dao.alchemy.queue_log import QueueLog
from xivo_dao.alchemy.stat_agent import StatAgent
from xivo_dao.alchemy.stat_queue import StatQueue
from xivo_dao.tests.test_dao import DAOTestCase

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S.%f"


class TestStatDAO(DAOTestCase):

    @classmethod
    def setUpClass(cls):
        super(TestStatDAO, cls).setUpClass()
        cls._create_functions()

    def setUp(self):
        DAOTestCase.setUp(self)
        self.start = t(2012, 07, 01)
        self.end = t(2012, 07, 31, 23, 59, 59, 999999)
        self.qname1, self.qid1 = self._insert_queue('q1')
        self.qname2, self.qid2 = self._insert_queue('q2')
        self.aname1, self.aid1 = self._insert_agent('a1')
        self.aname2, self.aid2 = self._insert_agent('a2')

    @staticmethod
    def _get_expected_call(call_list, callid):
        return [c for c in call_list if c[1] == callid][0]

    def test_fill_simple_calls_empty(self):
        try:
            stat_dao.fill_simple_calls(self.session, self.start, self.end)
        except:
            self.assertTrue(False, 'Should not happen')

    def test_get_login_intervals_in_range_calls_empty(self):
        result = stat_dao.get_login_intervals_in_range(self.session, self.start, self.end)

        self.assertEqual(len(result), 0)

    def test_get_login_intervals_when_login_same_as_start_no_logoff(self):
        logins = [
            {'time': self.start,
             'callid': 'login_1',
             'agent': self.aname1,
             'chan_name': 'SIP/1234-00001'}
        ]

        self._insert_agent_callback_logins_logoffs(logins, [])
        self._insert_agent_logins_logoffs(logins, [])

        result = stat_dao.get_login_intervals_in_range(self.session, self.start, self.end)

        expected = {
            self.aid1: sorted([(logins[0]['time'], self.end)])
        }

        self.assertEqual(expected, result)

    def test_get_login_intervals_when_logoff_same_as_start_no_login(self):
        talktime = datetime.timedelta(minutes=1)

        logoffs = [
            {'time': self.start,
             'callid': 'login_1',
             'agent': self.aname1,
             'chan_name': 'SIP/1234-00001',
             'talktime': talktime}
        ]

        self._insert_agent_callback_logins_logoffs([], logoffs)
        self._insert_agent_logins_logoffs([], logoffs)

        result = stat_dao.get_login_intervals_in_range(self.session, self.start, self.end)

        self.assertEqual(len(result), 0)

    def test_get_login_intervals_when_logoff_after_end_no_login(self):
        talktime = datetime.timedelta(minutes=1)
        logintime = self.end + datetime.timedelta(minutes=1)
        logouttime = logintime + talktime

        logoffs = [
            {'time': logouttime,
             'callid': 'login_1',
             'agent': self.aname1,
             'chan_name': 'SIP/1234-00001',
             'talktime': talktime}
        ]

        self._insert_agent_callback_logins_logoffs([], logoffs)
        self._insert_agent_logins_logoffs([], logoffs)

        result = stat_dao.get_login_intervals_in_range(self.session, self.start, self.end)

        self.assertEqual(len(result), 0)

    def test_get_login_intervals_when_logoff_same_as_end_no_login(self):
        talktime = datetime.timedelta(minutes=1)
        logintime = self.end - talktime
        logouttime = self.end

        logoffs = [
            {'time': logouttime,
             'callid': 'login_1',
             'agent': self.aname1,
             'chan_name': 'SIP/1234-00001',
             'talktime': talktime}
        ]

        self._insert_agent_callback_logins_logoffs([], logoffs)
        self._insert_agent_logins_logoffs([], logoffs)

        result = stat_dao.get_login_intervals_in_range(self.session, self.start, self.end)

        expected = {
            self.aid1: sorted([(logintime, logouttime)])
        }

        self.assertEqual(expected, result)

    def test_get_login_intervals_in_range_calls_logins_in_range(self):
        logintimes = [
            datetime.timedelta(minutes=10, seconds=13),
            datetime.timedelta(minutes=20),
            datetime.timedelta(minutes=7, seconds=21),
            datetime.timedelta(hours=2, minutes=3)
        ]

        cb_logins = [
            {'time': self.start + datetime.timedelta(seconds=30),
             'callid': 'login_1',
             'agent': self.aname1,
             'chan_name': 'SIP/1234-00001'
             },
            {'time': self.start + datetime.timedelta(minutes=20),
             'callid': 'login_2',
             'agent': self.aname1,
             'chan_name': 'SIP/1234-00002'
             },
        ]

        cb_logoffs = [
            {'time': cb_logins[0]['time'] + logintimes[0],
             'callid': 'NONE',
             'agent': self.aname1,
             'chan_name': cb_logins[0]['chan_name'],
             'talktime': logintimes[0],
             },
            {'time': cb_logins[1]['time'] + logintimes[1],
             'callid': 'NONE',
             'agent': self.aname1,
             'chan_name': cb_logins[1]['chan_name'],
             'talktime': logintimes[1],
             },
        ]

        self._insert_agent_callback_logins_logoffs(cb_logins, cb_logoffs)

        logins = [
            {'time': self.start + datetime.timedelta(seconds=50),
             'callid': 'login_3',
             'agent': self.aname2,
             'chan_name': 'SIP/5555-00001',
             },
            {'time': self.start + datetime.timedelta(seconds=40),
             'callid': 'login_4',
             'agent': self.aname2,
             'chan_name': 'SIP/5555-00002',
             },
        ]
        logoffs = [
            {'time': logins[0]['time'] + logintimes[2],
             'callid': logins[0]['callid'],
             'agent': self.aname2,
             'chan_name': logins[0]['chan_name'],
             'talktime': logintimes[2],
             },
            {'time': logins[1]['time'] + logintimes[3],
             'callid': logins[1]['callid'],
             'agent': self.aname2,
             'chan_name': logins[1]['chan_name'],
             'talktime': logintimes[3],
             }
        ]

        self._insert_agent_logins_logoffs(logins, logoffs)

        result = stat_dao.get_login_intervals_in_range(self.session, self.start, self.end)

        expected = {
            self.aid1: sorted([(cb_logins[0]['time'], cb_logoffs[0]['time']),
                               (cb_logins[1]['time'], cb_logoffs[1]['time'])]),
            self.aid2: sorted([(logins[1]['time'], logoffs[1]['time'])]),
        }

        self.assertEqual(expected, result)

    def test_get_login_intervals_in_range_logins_before_no_logout(self):
        cb_logins = [
            {'time': self.start - datetime.timedelta(seconds=30),
             'callid': 'login_1',
             'agent': self.aname1,
             'chan_name': 'SIP/1234-00001'
             },
            {'time': self.start - datetime.timedelta(seconds=44),
             'callid': 'login_5',
             'agent': self.aname1,
             'chan_name': 'SIP/1234-00003'
             },
        ]

        self._insert_agent_callback_logins_logoffs(cb_logins, [])

        logins = [
            {'time': self.start - datetime.timedelta(seconds=50),
             'callid': 'login_3',
             'agent': self.aname2,
             'chan_name': 'SIP/5555-00001',
             },
            {'time': self.start - datetime.timedelta(seconds=59),
             'callid': 'login_4',
             'agent': self.aname1,
             'chan_name': 'SIP/1234-00002'
             },
        ]

        self._insert_agent_logins_logoffs(logins, [])

        result = stat_dao.get_login_intervals_in_range(self.session, self.start, self.end)

        expected = {
            self.aid1: [(self.start, self.end)],
            self.aid2: [(self.start, self.end)],
        }

        self.assertEqual(expected, result)

    def test_get_login_intervals_in_range_no_login_logout_calls(self):
        connect1 = QueueLog(
            time=self.start - datetime.timedelta(minutes=5),
            callid='answered_1',
            queuename='queue',
            agent=self.aname1,
            event='CONNECT',
            data1='6',
            data2='linked_callid',
            data3='2'
        )
        self.session.add(connect1)
        connect2 = QueueLog(
            time=self.start + datetime.timedelta(minutes=5),
            callid='answered_2',
            queuename='queue',
            agent=self.aname2,
            event='CONNECT',
            data1='6',
            data2='linked_callid_2',
            data3='4'
        )

        self.session.begin()
        self.session.add(connect2)
        self.session.commit()

        result = stat_dao.get_login_intervals_in_range(self.session, self.start, self.end)

        expected = {}

        self.assertEqual(expected, result)

    def _insert_agent_logins_logoffs(self, logins, logoffs):
        self.session.begin()

        for login in logins:
            callback_login = QueueLog(
                time=login['time'],
                callid=login['callid'],
                queuename='NONE',
                agent=login['agent'],
                event='AGENTLOGIN',
                data1=login['chan_name']
            )
            self.session.add(callback_login)

        for logoff in logoffs:
            callback_logoff = QueueLog(
                time=logoff['time'],
                callid='NONE',
                queuename='NONE',
                agent=logoff['agent'],
                event='AGENTLOGOFF',
                data1=logoff['chan_name'],
                data2=logoff['talktime'].seconds,
            )
            self.session.add(callback_logoff)

        self.session.commit()

    def _insert_agent_callback_logins_logoffs(self, logins, logoffs):
        self.session.begin()

        for login in logins:
            callback_login = QueueLog(
                time=login['time'],
                callid=login['callid'],
                queuename='NONE',
                agent=login['agent'],
                event='AGENTCALLBACKLOGIN',
                data1=login['chan_name']
            )
            self.session.add(callback_login)

        for logoff in logoffs:
            callback_logoff = QueueLog(
                time=logoff['time'],
                callid='NONE',
                queuename='NONE',
                agent=logoff['agent'],
                event='AGENTCALLBACKLOGOFF',
                data1=logoff['chan_name'],
                data2=logoff['talktime'].seconds,
            )
            self.session.add(callback_logoff)

        self.session.commit()

    def _insert_transfered_calls(self, transfered_calls):
        map(lambda transfered_call: self._insert_transfered_call(*transfered_call), transfered_calls)

    def _insert_closed_calls(self, closed_calls):
        map(lambda closed_call: self._insert_closed_call(*closed_call), closed_calls)

    def _insert_completed_calls(self, completed_calls):
        map(lambda completed_call: self._insert_completed_call(*completed_call), completed_calls)

    def _insert_full_calls(self, full_calls):
        map(lambda full_call: self._insert_full_call(*full_call), full_calls)

    def _insert_joinempty_calls(self, je_calls):
        map(lambda je_call: self._insert_joinempty_call(*je_call), je_calls)

    def _insert_leaveempty_calls(self, le_calls):
        map(lambda le_call: self._insert_leaveempty_call(*le_call), le_calls)

    def _insert_ca_ratio_calls(self, ca_ratio_calls):
        map(lambda ca_ratio_call: self._insert_ca_ratio_call(*ca_ratio_call), ca_ratio_calls)

    def _insert_holdtime_calls(self, holdtime_calls):
        map(lambda holdtime_call: self._insert_holdtime_call(*holdtime_call), holdtime_calls)

    def _insert_transfered_call(self, time, callid, qname, aname, waittime, talktime):
        enterqueue = QueueLog(
            time=time.strftime(TIMESTAMP_FORMAT),
            callid=callid,
            queuename=qname,
            agent='NONE',
            event='ENTERQUEUE',
            data2='1001',
            data3='1'
        )

        connect = QueueLog(
            time=(time + datetime.timedelta(seconds=waittime)).strftime(TIMESTAMP_FORMAT),
            callid=callid,
            queuename=qname,
            agent=aname,
            event='CONNECT',
            data1=str(waittime),
            data2='1344965966.141',
            data3='1'
        )

        transfer = QueueLog(
            time=(time + datetime.timedelta(seconds=waittime + talktime)).strftime(TIMESTAMP_FORMAT),
            callid=callid,
            queuename=qname,
            agent=aname,
            event='TRANSFER',
            data1='s',
            data2='user',
            data3=str(waittime),
            data4=str(talktime)
        )

        self.session.begin()
        self.session.add_all([enterqueue, connect, transfer])
        self.session.commit()

    def _insert_completed_call(self, time, callid, qname, aname, waittime, talktime, agent_complete):
        enterqueue = QueueLog(
            time=time.strftime(TIMESTAMP_FORMAT),
            callid=callid,
            queuename=qname,
            agent='NONE',
            event='ENTERQUEUE',
            data2='1001',
            data3='1'
        )

        connect = QueueLog(
            time=(time + datetime.timedelta(seconds=waittime)).strftime(TIMESTAMP_FORMAT),
            callid=callid,
            queuename=qname,
            agent=aname,
            event='CONNECT',
            data1=str(waittime),
            data2='1344965966.141',
            data3='1'
        )

        complete = QueueLog(
            time=(time + datetime.timedelta(seconds=waittime + talktime)).strftime(TIMESTAMP_FORMAT),
            callid=callid,
            queuename=qname,
            agent=aname,
            event='COMPLETEAGENT' if agent_complete else 'COMPLETECALLER',
            data1=str(waittime),
            data2=str(talktime)
        )

        self.session.begin()
        self.session.add_all([enterqueue, connect, complete])
        self.session.commit()

    def _insert_full_call(self, t, callid, qname):
        full = QueueLog(
            time=t.strftime(TIMESTAMP_FORMAT),
            callid=callid,
            queuename=qname,
            agent='NONE',
            event='FULL'
        )

        self.session.begin()
        self.session.add(full)
        self.session.commit()

    def _insert_joinempty_call(self, t, callid, qname):
        je = QueueLog(
            time=t.strftime(TIMESTAMP_FORMAT),
            callid=callid,
            queuename=qname,
            agent='NONE',
            event='JOINEMPTY'
        )

        self.session.begin()
        self.session.add(je)
        self.session.commit()

    def _insert_leaveempty_call(self, t, callid, qname, waittime):
        enterqueue = QueueLog(
            time=t.strftime(TIMESTAMP_FORMAT),
            callid=callid,
            queuename=qname,
            agent='NONE',
            event='ENTERQUEUE',
            data2='1000',
            data3='1'
        )

        leave_time = t + datetime.timedelta(seconds=waittime)
        le = QueueLog(
            time=leave_time.strftime(TIMESTAMP_FORMAT),
            callid=callid,
            queuename=qname,
            agent='NONE',
            event='LEAVEEMPTY'
        )

        self.session.begin()
        self.session.add(enterqueue)
        self.session.add(le)
        self.session.commit()

    def _insert_closed_call(self, t, callid, qname):
        closed = QueueLog(
            time=t.strftime(TIMESTAMP_FORMAT),
            callid=callid,
            queuename=qname,
            agent='NONE',
            event='CLOSED'
        )

        self.session.begin()
        self.session.add(closed)
        self.session.commit()

    def _insert_ca_ratio_call(self, t, callid, qname):
        call = QueueLog(
            time=t,
            callid=callid,
            queuename=qname,
            agent='NONE',
            event='DIVERT_CA_RATIO'
        )

        self.session.begin()
        self.session.add(call)
        self.session.commit()

    def _insert_holdtime_call(self, t, callid, qname):
        call = QueueLog(
            time=t,
            callid=callid,
            queuename=qname,
            agent='NONE',
            event='DIVERT_HOLDTIME'
        )

        self.session.begin()
        self.session.add(call)
        self.session.commit()

    def _insert_agent(self, aname):
        a = StatAgent(name=aname)

        self.session.begin()
        self.session.add(a)
        self.session.commit()

        return a.name, a.id

    def _insert_queue(self, qname):
        q = StatQueue(name=qname)

        self.session.begin()
        self.session.add(q)
        self.session.commit()

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

    def test_merge_agent_statistics(self):
        stat_1 = {1: [(1, 2),
                      (2, 3)]}
        stat_2 = {1: [(4, 5)]}
        stat_3 = {1: [(6, 7)]}
        stat_4 = {1: [(5, 8)]}

        statistics = stat_dao._merge_agent_statistics(stat_1, stat_2, stat_3, stat_4)

        expected = {1: [(1, 2),
                        (2, 3),
                        (4, 5),
                        (5, 8)]}

        self.assertEqual(len(statistics), len(expected))

        for agent, statistic in statistics.iteritems():
            for login in statistic:
                self.assertTrue(login in expected[agent])

        for agent, statistic in expected.iteritems():
            for login in statistic:
                self.assertTrue(login in statistics[agent])

    def test_filter_overlap(self):
        items = [(1, 2), (2, 3)]
        result = stat_dao._filter_overlap(items)

        self.assertEqual(sorted(result), sorted(items))

        items = [(1, 2), (2, 3), (2, 4)]
        expected = [(1, 2), (2, 4)]
        result = stat_dao._filter_overlap(items)

        self.assertEqual(sorted(result), sorted(expected))

        items = [(1, 2), (2, 4), (3, 4)]
        expected = [(1, 2), (2, 4)]
        result = stat_dao._filter_overlap(items)

        self.assertEqual(sorted(result), sorted(expected))
