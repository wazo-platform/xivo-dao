# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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

import random

from datetime import datetime
from datetime import timedelta
from hamcrest import assert_that, has_length, empty

from xivo_dao import queue_log_dao
from xivo_dao.alchemy.stat_agent import StatAgent
from xivo_dao.alchemy.queue_log import QueueLog
from xivo_dao.helpers.db_utils import commit_or_abort
from xivo_dao.tests.test_dao import DAOTestCase

ONE_HOUR = timedelta(hours=1)
ONE_MICROSECOND = timedelta(microseconds=1)
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S.%f"


class TestQueueLogDAO(DAOTestCase):

    def setUp(self):
        super(TestQueueLogDAO, self).setUp()
        self.queue_name = 'q1'

    def _insert_agent(self, aname):
        a = StatAgent(name=aname)

        self.add_me(a)

        return a.name, a.id

    def _insert_entry_queue(self, event, timestamp, callid, queuename, agent=None,
                            d1=None, d2=None, d3=None, d4=None, d5=None):
        queue_log = QueueLog()
        queue_log.time = timestamp
        queue_log.callid = callid
        queue_log.queuename = queuename
        queue_log.event = event
        if agent:
            queue_log.agent = agent
        if d1:
            queue_log.data1 = d1
        if d2:
            queue_log.data2 = d2
        if d3:
            queue_log.data3 = d3
        if d4:
            queue_log.data4 = d4
        if d5:
            queue_log.data5 = d5

        self.add_me(queue_log)

    def _insert_entry_queue_full(self, t, callid, queuename):
        self._insert_entry_queue('FULL', self._build_timestamp(t), callid, queuename)

    def _insert_entry_queue_joinempty(self, t, callid, queuename):
        self._insert_entry_queue('JOINEMPTY', self._build_timestamp(t), callid, queuename)

    def _insert_entry_queue_leaveempty(self, time, callid, queuename):
        self._insert_entry_queue('LEAVEEMPTY', self._build_timestamp(time), callid, queuename)

    def _insert_entry_queue_closed(self, t, callid, queuename):
        self._insert_entry_queue('CLOSED', self._build_timestamp(t), callid, queuename)

    def _insert_entry_queue_answered(self, time, callid, queuename, agent, waittime):
        self._insert_entry_queue(
            'CONNECT', self._build_timestamp(time), callid, queuename, agent=agent, d1=waittime)

    def _insert_entry_queue_abandoned(self, time, callid, queuename, waittime):
        self._insert_entry_queue('ABANDON', self._build_timestamp(time), callid, queuename, d3=waittime)

    def _insert_entry_queue_timeout(self, time, callid, queuename, waittime):
        self._insert_entry_queue('EXITWITHTIMEOUT', self._build_timestamp(time), callid, queuename, d3=waittime)

    def _insert_entry_queue_enterqueue(self, time, callid, queuename):
        self._insert_entry_queue('ENTERQUEUE', self._build_timestamp(time), callid, queuename)

    def _insert_entry_queue_completeagent(self, time, callid, queuename, agent, talktime):
        self._insert_entry_queue('COMPLETEAGENT', self._build_timestamp(time),
                                 callid, queuename, agent, d2=talktime)

    def _insert_entry_queue_completecaller(self, time, callid, queuename, agent, talktime):
        self._insert_entry_queue('COMPLETECALLER', self._build_timestamp(time),
                                 callid, queuename, agent, d2=talktime)

    def _insert_entry_queue_transfer(self, time, callid, queuename, agent, talktime):
        self._insert_entry_queue('TRANSFER', self._build_timestamp(time),
                                 callid, queuename, agent, d4=talktime)

    @staticmethod
    def _build_date(year, month, day, hour=0, minute=0, second=0, micro=0):
        return datetime(year, month, day, hour, minute, second, micro).strftime(TIMESTAMP_FORMAT)

    @staticmethod
    def _build_timestamp(t):
        return t.strftime(TIMESTAMP_FORMAT)

    @staticmethod
    def _time_from_timestamp(t):
        return datetime.strptime(t, TIMESTAMP_FORMAT)

    def test_get_wrapup_time(self):
        _, agent_id_1 = self._insert_agent('Agent/1')
        _, agent_id_2 = self._insert_agent('Agent/2')
        start = datetime(2012, 10, 1, 6)
        end = datetime(2012, 10, 1, 7, 59, 59, 999999)
        queue_log_data = '''\
| time                       | callid | queuename | agent   | event       | data1 | data2 | data3 | data4 | data5 |
| 2012-10-01 05:59:50.000000 | NONE   | NONE      | Agent/1 | WRAPUPSTART |    30 |       |       |       |       |
| 2012-10-01 06:00:10.000000 | NONE   | NONE      | Agent/1 | WRAPUPSTART |    15 |       |       |       |       |
| 2012-10-01 06:00:15.000000 | NONE   | NONE      | Agent/2 | WRAPUPSTART |    30 |       |       |       |       |
| 2012-10-01 06:59:50.000000 | NONE   | NONE      | Agent/1 | WRAPUPSTART |    15 |       |       |       |       |
| 2012-10-01 07:00:10.000000 | NONE   | NONE      | Agent/1 | WRAPUPSTART |    30 |       |       |       |       |
| 2012-10-01 08:00:10.000000 | NONE   | NONE      | Agent/1 | WRAPUPSTART |    30 |       |       |       |       |
| 2012-10-01 07:59:40.000000 | NONE   | NONE      | Agent/2 | WRAPUPSTART |    30 |       |       |       |       |
'''
        self._insert_queue_log_data(queue_log_data)

        result = queue_log_dao.get_wrapup_times(self.session, start, end, ONE_HOUR)

        expected = {
            datetime(2012, 10, 1, 6): {
                agent_id_1: {'wrapup_time': timedelta(seconds=45)},
                agent_id_2: {'wrapup_time': timedelta(seconds=30)},
            },
            datetime(2012, 10, 1, 7): {
                agent_id_1: {'wrapup_time': timedelta(seconds=35)},
                agent_id_2: {'wrapup_time': timedelta(seconds=20)},
            },
        }

        self.assertEqual(result, expected)

    def test_get_first_time(self):
        self.assertRaises(LookupError, queue_log_dao.get_first_time, self.session)

        queuename = 'q1'
        for minute in [0, 10, 20, 30, 40, 50]:
            datetimewithmicro = datetime(2012, 1, 1, 0, minute, 59)
            callid = str(12345678.123 + minute)
            self._insert_entry_queue_full(datetimewithmicro, callid, queuename)

        expected = datetime(2012, 01, 01, 0, 0, 59)

        result = queue_log_dao.get_first_time(self.session)

        self.assertEqual(result, expected)

    def test_get_queue_names_in_range(self):
        queue_names = sorted(['queue_%s' % x for x in range(10)])
        t = datetime(2012, 1, 1, 1, 1, 1)
        timestamp = self._build_date(t.year, t.month, t.day, t.hour, t.minute, t.second)
        for queue_name in queue_names:
            self._insert_entry_queue('FULL', timestamp, queue_name, queue_name)

        result = sorted(queue_log_dao.get_queue_names_in_range(self.session, t - ONE_HOUR, t + ONE_HOUR))

        self.assertEqual(result, queue_names)

    def test_get_queue_abandoned_call(self):
        start = datetime(2012, 01, 01, 01, 00, 00)
        expected = self._insert_abandon(start, [-1, 0, 10, 30, 59, 60, 120])

        result = queue_log_dao.get_queue_abandoned_call(self.session, start, start + ONE_HOUR - ONE_MICROSECOND)

        self.assertEqual(sorted(result), sorted(expected))

    def test_get_queue_abandoned_call_following_transfer_at_hour_border(self):
        queue_logs = [
            # New call in queue2
            ('2015-05-06 11:59:52.991930', '1430927991.36', 'queue2', 'NONE', 'ENTERQUEUE', '', '0612345678', '1', '', ''),
            ('2015-05-06 12:00:02.110492', '1430927991.36', 'queue2', 'Agent/1002', 'CONNECT', '10', '1430927992.37', '9', '', ''),
            ('2015-05-06 12:00:10.804470', '1430927991.36', 'queue2', 'Agent/1002', 'COMPLETECALLER', '10', '8', '1', '', ''),
            # Agent/1002 blind txfer the call to queue1
            ('2015-05-06 12:00:10.883332', '1430927991.36', 'queue1', 'NONE', 'ENTERQUEUE', '', '0612345678', '1', '', ''),
            ('2015-05-06 12:00:25.887220', '1430927991.36', 'queue1', 'Agent/1001', 'RINGNOANSWER', '15000', '', '', '', ''),
            ('2015-05-06 12:00:29.197769', '1430927991.36', 'queue1', 'NONE', 'ABANDON', '1', '1', '19', '', ''),
        ]
        for queue_log in queue_logs:
            queue_log_dao.insert_entry(*queue_log)

        abandoned_at_11_oclock = list(queue_log_dao.get_queue_abandoned_call(self.session, datetime(2015, 5, 6, 11), datetime(2015, 5, 6, 11, 59, 59, 999999)))
        abandoned_at_12_oclock = list(queue_log_dao.get_queue_abandoned_call(self.session, datetime(2015, 5, 6, 12), datetime(2015, 5, 6, 12, 59, 59, 999999)))

        assert_that(abandoned_at_11_oclock, empty())
        assert_that(abandoned_at_12_oclock, has_length(1))

    def test_get_queue_abandoned_call_no_enterqueue(self):
        queue_logs = [
            ('2015-05-06 12:00:10', '1', 'queue1', 'NONE', 'ENTERQUEUE', '', '0612345678', '1', '', ''),
            ('2015-05-06 12:00:11', '1', 'queue1', 'NONE', 'ABANDON', '1', '1', '19', '', ''),
            ('2015-05-06 12:00:12', '2', 'queue1', 'NONE', 'ABANDON', '1', '1', '30', '', ''),
        ]
        for queue_log in queue_logs:
            queue_log_dao.insert_entry(*queue_log)

        abandoned_at_12_oclock = list(queue_log_dao.get_queue_abandoned_call(self.session, datetime(2015, 5, 6, 12), datetime(2015, 5, 6, 12, 59, 59, 999999)))

        assert_that(abandoned_at_12_oclock, has_length(1))

    def test_get_queue_timeout_call_following_transfer_at_hour_border(self):
        queue_logs = [
            # New call in queue2
            ('2015-05-06 11:59:52.991930', '1430927991.36', 'queue2', 'NONE', 'ENTERQUEUE', '', '0612345678', '1', '', ''),
            ('2015-05-06 12:00:02.110492', '1430927991.36', 'queue2', 'Agent/1002', 'CONNECT', '10', '1430927992.37', '9', '', ''),
            ('2015-05-06 12:00:10.804470', '1430927991.36', 'queue2', 'Agent/1002', 'COMPLETECALLER', '10', '8', '1', '', ''),
            # Agent/1002 blind txfer the call to queue1
            ('2015-05-06 12:00:10.883332', '1430927991.36', 'queue1', 'NONE', 'ENTERQUEUE', '', '0612345678', '1', '', ''),
            ('2015-05-06 12:00:25.887220', '1430927991.36', 'queue1', 'Agent/1001', 'RINGNOANSWER', '15000', '', '', '', ''),
            ('2015-05-06 12:00:29.197769', '1430927991.36', 'queue1', 'NONE', 'EXITWITHTIMEOUT', '1', '1', '20', '', ''),
        ]
        for queue_log in queue_logs:
            queue_log_dao.insert_entry(*queue_log)

        timeout_at_11_oclock = list(queue_log_dao.get_queue_timeout_call(self.session, datetime(2015, 5, 6, 11), datetime(2015, 5, 6, 11, 59, 59, 999999)))
        timeout_at_12_oclock = list(queue_log_dao.get_queue_timeout_call(self.session, datetime(2015, 5, 6, 12), datetime(2015, 5, 6, 12, 59, 59, 999999)))

        assert_that(timeout_at_11_oclock, empty())
        assert_that(timeout_at_12_oclock, has_length(1))


    def test_get_queue_timeout_call(self):
        start = datetime(2012, 01, 01, 01, 00, 00)
        expected = self._insert_timeout(start, [-1, 0, 10, 30, 59, 60, 120])

        result = queue_log_dao.get_queue_timeout_call(self.session, start, start + ONE_HOUR - ONE_MICROSECOND)

        self.assertEqual(sorted(result), sorted(expected))

    def _insert_timeout(self, start, minutes):
        expected = []
        for minute in minutes:
            leave_time = start + timedelta(minutes=minute)
            waittime = self._random_time()
            enter_time = leave_time - timedelta(seconds=waittime)
            callid = str(143897234.123 + minute)
            self._insert_entry_queue_enterqueue(enter_time, callid, self.queue_name)
            self._insert_entry_queue_timeout(leave_time, callid, self.queue_name, waittime)
            if start <= enter_time < start + ONE_HOUR:
                expected.append(
                    {
                        'queue_name': self.queue_name,
                        'event': 'timeout',
                        'time': enter_time,
                        'callid': callid,
                        'waittime': waittime,
                        'talktime': 0,
                    })
        return expected

    def _insert_abandon(self, start, minutes):
        expected = []
        for minute in minutes:
            leave_time = start + timedelta(minutes=minute)
            waittime = self._random_time()
            enter_time = leave_time - timedelta(seconds=waittime)
            callid = str(143897234.123 + minute)
            self._insert_entry_queue_enterqueue(enter_time, callid, self.queue_name)
            self._insert_entry_queue_abandoned(leave_time, callid, self.queue_name, waittime)
            if start <= enter_time < start + ONE_HOUR:
                expected.append(
                    {
                        'queue_name': self.queue_name,
                        'event': 'abandoned',
                        'time': enter_time,
                        'callid': callid,
                        'waittime': waittime,
                        'talktime': 0,
                    })
        return expected

    def _insert_leaveempty(self, start, minutes):
        expected = []
        for minute in minutes:
            leave_time = start + timedelta(minutes=minute)
            waittime = self._random_time()
            enter_time = leave_time - timedelta(seconds=waittime)
            callid = str(143897234.123 + minute)
            self._insert_entry_queue_enterqueue(enter_time, callid, self.queue_name)
            self._insert_entry_queue_leaveempty(leave_time, callid, self.queue_name)
            if start <= enter_time < start + ONE_HOUR:
                expected.append(
                    {
                        'queue_name': self.queue_name,
                        'event': 'leaveempty',
                        'time': enter_time,
                        'callid': callid,
                        'waittime': waittime,
                        'talktime': 0,
                    })
        return expected

    def _insert_ev_fn(self, event_name):
        return {'abandoned': self._insert_entry_queue_abandoned,
                'answered': self._insert_entry_queue_answered,
                'closed': self._insert_entry_queue_closed,
                'full': self._insert_entry_queue_full,
                'joinempty': self._insert_entry_queue_joinempty,
                'leaveempty': self._insert_entry_queue_leaveempty,
                'timeout': self._insert_entry_queue_timeout}[event_name]

    @staticmethod
    def _random_time():
        return int(round(random.random() * 10)) + 1

    def _insert_event_list(self, event_name, start, minutes):
        expected = []
        for minute in minutes:
            delta = timedelta(minutes=minute)
            t = start + delta
            callid = str(1234567.123 + minute)
            waittime = 0
            if event_name in ['answered', 'abandoned', 'timeout', 'leaveempty']:
                waittime = self._random_time()
            self._insert_ev_fn(event_name)(t, callid, self.queue_name, waittime)
            if 0 <= minute < 60:
                expected.append({'queue_name': self.queue_name,
                                 'event': event_name,
                                 'time': t,
                                 'callid': callid,
                                 'waittime': waittime})

        return expected

    def test_delete_event_by_queue_between(self):
        self._insert_entry_queue_full(datetime(2012, 07, 01, 7, 1, 1), 'delete_between_1', 'q1')
        self._insert_entry_queue_full(datetime(2012, 07, 01, 8, 1, 1), 'delete_between_2', 'q1')
        self._insert_entry_queue_full(datetime(2012, 07, 01, 9, 1, 1), 'delete_between_3', 'q1')
        self._insert_entry_queue_full(datetime(2012, 07, 01, 8, 1, 0), 'delete_between_4', 'q2')

        queue_log_dao.delete_event_by_queue_between(
            'FULL', 'q1', '2012-07-01 08:00:00.000000', '2012-07-01 08:59:59.999999')

        callids = [r.callid for r in self.session.query(QueueLog.callid)
                   .filter(QueueLog.callid.like('delete_between_%'))]

        expected = ['delete_between_1', 'delete_between_3', 'delete_between_4']

        self.assertEquals(callids, expected)

    def test_insert_entry(self):
        queue_log_dao.insert_entry('time', 'callid', 'queue', 'agent', 'event', '1', '2', '3', '4', '5')

        result = [r for r in self.session.query(QueueLog).all()][0]
        self.assertEqual(result.time, 'time')
        self.assertEqual(result.callid, 'callid')
        self.assertEqual(result.queuename, 'queue')
        self.assertEqual(result.agent, 'agent')
        self.assertEqual(result.event, 'event')
        self.assertEqual(result.data1, '1')
        self.assertEqual(result.data2, '2')
        self.assertEqual(result.data3, '3')
        self.assertEqual(result.data4, '4')
        self.assertEqual(result.data5, '5')

    def test_hours_with_calls(self):
        start = datetime(2012, 01, 01)
        end = datetime(2012, 6, 30, 23, 59, 59, 999999)
        res = [h for h in queue_log_dao.hours_with_calls(self.session, start, end)]

        self.assertEqual(res, [])

        def _insert_at(t):
            queue_log_dao.insert_entry(t, 'hours', 'queue', 'agent', 'event')

        _insert_at('2011-12-31 12:55:22.123123')
        _insert_at('2012-01-01 08:45:23.2345')
        _insert_at('2012-06-30 23:59:59.999999')
        _insert_at('2012-07-01 00:00:00.000000')

        expected = [
            datetime(2012, 1, 1, 8),
            datetime(2012, 6, 30, 23)
        ]

        res = [h for h in queue_log_dao.hours_with_calls(self.session, start, end)]

        self.assertEqual(res, expected)

    def test_last_callid_with_event_for_agent(self):
        t = datetime(2012, 1, 1)
        event = 'FULL'
        agent = 'Agent/1234'
        queue = 'queue'

        self._insert_entry_queue(
            event,
            self._build_timestamp(t),
            'one',
            queue,
            agent,
        )

        self._insert_entry_queue(
            event,
            self._build_timestamp(t + timedelta(minutes=3)),
            'two',
            queue,
            agent,
        )

        res = queue_log_dao.get_last_callid_with_event_for_agent(
            event,
            agent,
        )

        self.assertEqual(res, 'two')

    def _insert_queue_log_data(self, queue_log_data):
        with commit_or_abort(self.session):
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
