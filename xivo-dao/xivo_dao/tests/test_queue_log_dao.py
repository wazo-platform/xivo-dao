# -*- coding: UTF-8 -*-
import datetime
import random

from xivo_dao import queue_log_dao
from xivo_dao.queue_log_dao import CallStart
from xivo_dao.alchemy.queue_log import QueueLog
from xivo_dao.tests.test_dao import DAOTestCase

ONE_HOUR = datetime.timedelta(hours=1)
ONE_MICROSECOND = datetime.timedelta(microseconds=1)
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S.%f"


class TestQueueLogDAO(DAOTestCase):

    tables = [QueueLog]

    def setUp(self):
        self.empty_tables()
        self.queue_name = 'q1'

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

        self.session.add(queue_log)
        self.session.commit()

    def _insert_sample(self):
        self._started_calls = []

        self._insert_answered_calls()
        self._insert_abandoned_calls()
        self._insert_timeout_calls()
        self._insert_leaveempty_calls()

    def _insert_answered_calls(self):
        t = datetime.datetime(2012, 1, 1, 0, 0, 0)
        t1 = t
        t2 = t + datetime.timedelta(seconds=2)
        t3 = t + datetime.timedelta(seconds=4)

        w1, w2, w3 = 5, 7, 13
        talk1, talk2, talk3 = 12, 122, 55
        a1, a2 = 'Agent/1002', 'Agent/1003'

        self._insert_entry_queue_enterqueue(t1, 'answered_1', self.queue_name)
        self._insert_entry_queue_answered(
            t1 + datetime.timedelta(seconds=w1), 'answered_1', self.queue_name, a1, w1)
        self._insert_entry_queue_completeagent(
            t1 + datetime.timedelta(seconds=w1 + talk1), 'answered_1', self.queue_name, a1, talk1)

        self._insert_entry_queue_enterqueue(t2, 'answered_2', self.queue_name)
        self._insert_entry_queue_answered(
            t2 + datetime.timedelta(seconds=1), 'answered_2', self.queue_name, a2, w2)
        self._insert_entry_queue_completecaller(
            t2 + datetime.timedelta(seconds=w2 + talk2), 'answered_2', self.queue_name, a2, talk2)

        self._insert_entry_queue_enterqueue(t3, 'answered_3', self.queue_name)
        self._insert_entry_queue_answered(
            t3 + datetime.timedelta(seconds=w3), 'answered_3', self.queue_name, a2, w3)
        self._insert_entry_queue_transfer(
            t3 + datetime.timedelta(seconds=w3 + talk3), 'answered_3', self.queue_name, a2, talk3)

        self._started_calls.extend([
            CallStart('answered_1', 'ENTERQUEUE', t1, self.queue_name),
            CallStart('answered_2', 'ENTERQUEUE', t2, self.queue_name),
            CallStart('answered_3', 'ENTERQUEUE', t3, self.queue_name),
            ])

        self._answered = [
            {'waittime': w1,
             'callid': u'answered_1',
             'queue_name': self.queue_name,
             'event': 'answered',
             'time': t1,
             'talktime': talk1,
             'agent': a1},
            {'waittime': w2,
             'callid': u'answered_2',
             'queue_name': self.queue_name,
             'event': 'answered',
             'time': t2,
             'talktime': talk2,
             'agent': a2},
            {'waittime': w3,
             'callid': u'answered_3',
             'queue_name': self.queue_name,
             'event': 'answered',
             'time': t3,
             'talktime': talk3,
             'agent': a2},
            ]

    def _insert_abandoned_calls(self):
        t1 = datetime.datetime(2012, 1, 1, 0, 1, 0)
        t2 = datetime.datetime(2012, 1, 1, 0, 1, 2)
        w1, w2 = 6, 12

        c1 = CallStart('abandoned_1', 'ENTERQUEUE', t1, self.queue_name)
        c2 = CallStart('abandoned_2', 'ENTERQUEUE', t2, self.queue_name)

        self._started_calls.extend([c1, c2])

        self._insert_entry_queue_enterqueue(c1.time, c1.callid, c1.queuename)
        self._insert_entry_queue_abandoned(t1 + datetime.timedelta(seconds=1),
                                           c1.callid, c1.queuename, w1)

        self._insert_entry_queue_enterqueue(c2.time, c2.callid, c2.queuename)
        self._insert_entry_queue_abandoned(t2 + datetime.timedelta(seconds=1),
                                           c2.callid, c2.queuename, w2)

        self._abandoned = [
            {'waittime': w1,
             'callid': c1.callid,
             'queue_name': c1.queuename,
             'event': 'abandoned',
             'time': t1},
            {'waittime': w2,
             'callid': c2.callid,
             'queue_name': c2.queuename,
             'event': 'abandoned',
             'time': t2},
            ]

    def _insert_timeout_calls(self):
        t1 = datetime.datetime(2012, 1, 1, 0, 2, 0)
        t2 = datetime.datetime(2012, 1, 1, 0, 2, 2)
        w1, w2 = 11, 25

        c1 = CallStart('timeout_1', 'ENTERQUEUE', t1, self.queue_name)
        c2 = CallStart('timeout_2', 'ENTERQUEUE', t2, self.queue_name)

        self._started_calls.extend([c1, c2])

        self._insert_entry_queue_enterqueue(c1.time, c1.callid, c1.queuename)
        self._insert_entry_queue_timeout(t1 + datetime.timedelta(seconds=1),
                                         c1.callid, c1.queuename, w1)

        self._insert_entry_queue_enterqueue(c2.time, c2.callid, c2.queuename)
        self._insert_entry_queue_timeout(t2 + datetime.timedelta(seconds=1),
                                         c2.callid, c2.queuename, w2)

        self._timeout = [
            {'waittime': w1,
             'callid': c1.callid,
             'queue_name': c1.queuename,
             'event': 'timeout',
             'time': t1},
            {'waittime': w2,
             'callid': c2.callid,
             'queue_name': c2.queuename,
             'event': 'timeout',
             'time': t2},
            ]

    def _insert_leaveempty_calls(self):
        t1 = datetime.datetime(2012, 1, 1, 0, 3, 0)
        t2 = datetime.datetime(2012, 1, 1, 0, 3, 2)
        w1, w2 = 55, 13

        c1 = CallStart('leaveempty_1', 'ENTERQUEUE', t1, self.queue_name)
        c2 = CallStart('leaveempty_2', 'ENTERQUEUE', t2, self.queue_name)

        self._started_calls.extend([c1, c2])

        self._insert_entry_queue_enterqueue(c1.time, c1.callid, c1.queuename)
        self._insert_entry_queue_leaveempty(t1 + datetime.timedelta(seconds=w1),
                                            c1.callid, c1.queuename)

        self._insert_entry_queue_enterqueue(c2.time, c2.callid, c2.queuename)
        self._insert_entry_queue_leaveempty(t2 + datetime.timedelta(seconds=w2),
                                            c2.callid, c2.queuename)

        self._leaveempty = [
            {'waittime': w1,
             'callid': c1.callid,
             'queue_name': c1.queuename,
             'event': 'leaveempty',
             'time': t1},
            {'waittime': w2,
             'callid': c2.callid,
             'queue_name': c2.queuename,
             'event': 'leaveempty',
             'time': t2},
            ]

    def _insert_entry_queue_full(self, t, callid, queuename, waittime=0):
        self._insert_entry_queue('FULL', self._build_timestamp(t), callid, queuename)

    def _insert_entry_queue_joinempty(self, t, callid, queuename, waittime=0):
        self._insert_entry_queue('JOINEMPTY', self._build_timestamp(t), callid, queuename)

    def _insert_entry_queue_leaveempty(self, time, callid, queuename, waittime=0):
        self._insert_entry_queue('LEAVEEMPTY', self._build_timestamp(time), callid, queuename)

    def _insert_entry_queue_closed(self, t, callid, queuename, waittime=0):
        self._insert_entry_queue('CLOSED', self._build_timestamp(t), callid, queuename)

    def _insert_entry_queue_answered(self, time, callid, queuename, agent, waittime):
        self._insert_entry_queue(
            'CONNECT', self._build_timestamp(time), callid, queuename, agent=agent, d1=waittime)

    def _insert_entry_queue_abandoned(self, time, callid, queuename, waittime):
        self._insert_entry_queue('ABANDON', self._build_timestamp(time), callid, queuename, d3=waittime)

    def _insert_entry_queue_timeout(self, time, callid, queuename, waittime):
        self._insert_entry_queue('EXITWITHTIMEOUT', self._build_timestamp(time), callid, queuename, d3=waittime)

    def _insert_entry_queue_enterqueue(self, time, callid, queuename, waittime=0):
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
        return datetime.datetime(year, month, day, hour, minute, second, micro).strftime(TIMESTAMP_FORMAT)

    @staticmethod
    def _build_timestamp(t):
        return t.strftime(TIMESTAMP_FORMAT)

    @staticmethod
    def _time_from_timestamp(t):
        return datetime.datetime.strptime(t, TIMESTAMP_FORMAT)

    def test_get_first_time(self):
        queuename = 'q1'
        for minute in [0, 10, 20, 30, 40, 50]:
            datetimewithmicro = datetime.datetime(2012, 1, 1, 0, minute, 59)
            callid = str(12345678.123 + minute)
            self._insert_entry_queue_full(datetimewithmicro, callid, queuename, 0)

        expected = datetime.datetime(2012, 01, 01, 0, 0, 59)

        result = queue_log_dao.get_first_time()

        self.assertEqual(result, expected)

    def test_time_str_to_datetime(self):
        s1 = '2012-01-01 01:01:01.456897'
        expected = datetime.datetime(2012, 01, 01, 01, 01, 01, 456897)

        result = queue_log_dao._time_str_to_datetime(s1)

        self.assertEqual(result, expected)

        s1 = '2012-01-01 01:01:01'
        expected = datetime.datetime(2012, 01, 01, 01, 01, 01)

        result = queue_log_dao._time_str_to_datetime(s1)

        self.assertEqual(result, expected)

    def test_get_queue_names_in_range(self):
        queue_names = sorted('queue_%s' % x for x in range(10))
        t = datetime.datetime(2012, 1, 1, 1, 1, 1)
        timestamp = self._build_date(t.year, t.month, t.day, t.hour, t.minute, t.second)
        for queue_name in queue_names:
            self._insert_entry_queue('FULL', timestamp, queue_name, queue_name)

        one_hour = datetime.timedelta(hours=1)
        result = sorted(queue_log_dao.get_queue_names_in_range(t - one_hour, t + one_hour))

        self.assertEqual(result, queue_names)

    def test_get_agents_after(self):
        agents = sorted('Agent/%s' % (x + 1000) for x in range(10))
        t = datetime.datetime(2012, 1, 1, 1, 1, 1)
        second = t.second
        for agent in agents:
            self._insert_entry_queue('CONNECT', t + datetime.timedelta(seconds=second), agent, 'q', agent)
            second += 1

        result = queue_log_dao.get_agents_after(t)

        self.assertEqual(sorted(result), agents)

    def test_get_queue_answered_call(self):
        self._insert_sample()

        result = queue_log_dao.get_queue_answered_call(self._started_calls)

        self.assertEqual(sorted(result), sorted(self._answered))

    def test_get_queue_abandoned_call(self):
        self._insert_sample()

        result = queue_log_dao.get_queue_abandoned_call(self._started_calls)

        self.assertEqual(result, self._abandoned)

    def test_get_queue_timeout_call(self):
        self._insert_sample()

        result = queue_log_dao.get_queue_timeout_call(self._started_calls)

        self.assertEqual(result, self._timeout)

    def test_get_queue_leaveempty_call(self):
        self._insert_sample()

        result = queue_log_dao.get_queue_leaveempty_call(self._started_calls)

        self.assertEqual(result, self._leaveempty)

    @staticmethod
    def _random_wait_time():
        return int(round(random.random() * 10)) + 1

    def test_get_started_calls(self):
        s = datetime.datetime(2012, 1, 1, 0, 0, 0, 0)
        e = datetime.datetime(2012, 1, 1, 0, 59, 59, 999999)

        self._insert_entry_queue_full(s, '1', self.queue_name)

        self._insert_entry_queue_enterqueue(s - datetime.timedelta(microseconds=1), '2', self.queue_name)
        self._insert_entry_queue_abandoned(s + datetime.timedelta(seconds=1), '2', self.queue_name, 10)

        self._insert_entry_queue_enterqueue(s, '3', self.queue_name)
        self._insert_entry_queue_abandoned(e + datetime.timedelta(seconds=1), '3', self.queue_name, 10)

        self._insert_entry_queue_closed(s + datetime.timedelta(seconds=5), '4', self.queue_name)

        self._insert_entry_queue_joinempty(s + datetime.timedelta(seconds=10), '5', self.queue_name)

        result = queue_log_dao.get_started_calls(s, e)

        expected = [CallStart('1', 'FULL', s, self.queue_name),
                    CallStart('3', 'ENTERQUEUE', s, self.queue_name),
                    CallStart('4', 'CLOSED', s + datetime.timedelta(seconds=5), self.queue_name),
                    CallStart('5', 'JOINEMPTY', s + datetime.timedelta(seconds=10), self.queue_name)]

        self.assertEqual(result, expected)
