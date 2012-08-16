# -*- coding: UTF-8 -*-
import datetime
import random

from xivo_dao import queue_log_dao
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

    def test_get_enterqueue_time(self):
        callid = '1234'
        t1 = self._build_date(2012, 01, 01, 01, 01)
        t2 = self._build_date(2012, 01, 01, 01, 23, 43)
        self._insert_entry_queue('ENTERQUEUE', t1, callid, self.queue_name)
        self._insert_entry_queue('LEAVEEMPTY', t2, callid, self.queue_name)

        expected = {callid: datetime.datetime(2012, 01, 01, 01, 01)}
        result = queue_log_dao.get_enterqueue_time([callid])

        self.assertEqual(result, expected)

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
        queue_names = sorted(['queue_%s' % x for x in range(10)])
        t = datetime.datetime(2012, 1, 1, 1, 1, 1)
        timestamp = self._build_date(t.year, t.month, t.day, t.hour, t.minute, t.second)
        for queue_name in queue_names:
            self._insert_entry_queue('FULL', timestamp, queue_name, queue_name)

        one_hour = datetime.timedelta(hours=1)
        result = sorted(queue_log_dao.get_queue_names_in_range(t - one_hour, t + one_hour))

        self.assertEqual(result, queue_names)

    def test_get_queue_full_call(self):
        start = datetime.datetime(2012, 01, 01, 01, 00, 00)
        expected = self._insert_event_list('full', start, [-1, 0, 10, 30, 59, 60, 120])

        result = queue_log_dao.get_queue_full_call(start, start + ONE_HOUR - ONE_MICROSECOND)

        self.assertEqual(sorted(result), sorted(expected))

    def test_get_queue_closed_call(self):
        start = datetime.datetime(2012, 01, 01, 01, 00, 00)
        expected = self._insert_event_list('closed', start, [-1, 0, 10, 30, 59, 60, 120])

        result = queue_log_dao.get_queue_closed_call(start, start + ONE_HOUR - ONE_MICROSECOND)

        self.assertEqual(sorted(result), sorted(expected))

    def test_get_queue_abandoned_call(self):
        start = datetime.datetime(2012, 01, 01, 01, 00, 00)
        expected = self._insert_abandon(start, [-1, 0, 10, 30, 59, 60, 120])

        result = queue_log_dao.get_queue_abandoned_call(start, start + ONE_HOUR - ONE_MICROSECOND)

        self.assertEqual(sorted(result), sorted(expected))

    def test_get_queue_timeout_call(self):
        start = datetime.datetime(2012, 01, 01, 01, 00, 00)
        expected = self._insert_timeout(start, [-1, 0, 10, 30, 59, 60, 120])

        result = queue_log_dao.get_queue_timeout_call(start, start + ONE_HOUR - ONE_MICROSECOND)

        self.assertEqual(sorted(result), sorted(expected))

    def test_get_queue_joinempty_call(self):
        start = datetime.datetime(2012, 01, 01, 01, 00, 00)
        expected = self._insert_event_list('joinempty', start, [-1, 0, 10, 30, 59, 60, 120])

        result = queue_log_dao.get_queue_joinempty_call(start, start + ONE_HOUR - ONE_MICROSECOND)

        self.assertEqual(sorted(result), sorted(expected))

    def test_get_queue_leaveempty_call(self):
        start = datetime.datetime(2012, 01, 01, 01, 00, 00)
        expected = self._insert_leaveempty(start, [-1, 0, 10, 30, 59, 60, 120])

        result = queue_log_dao.get_queue_leaveempty_call(start, start + ONE_HOUR - ONE_MICROSECOND)

        self.assertEqual(sorted(result), sorted(expected))

    def _insert_timeout(self, start, minutes):
        expected = []
        for minute in minutes:
            leave_time = start + datetime.timedelta(minutes=minute)
            waittime = self._random_time()
            enter_time = leave_time - datetime.timedelta(seconds=waittime)
            callid = str(143897234.123 + minute)
            self._insert_entry_queue_enterqueue(enter_time, callid, self.queue_name)
            self._insert_entry_queue_timeout(leave_time, callid, self.queue_name, waittime)
            if start <= enter_time < start + datetime.timedelta(hours=1):
                expected.append({
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
            leave_time = start + datetime.timedelta(minutes=minute)
            waittime = self._random_time()
            enter_time = leave_time - datetime.timedelta(seconds=waittime)
            callid = str(143897234.123 + minute)
            self._insert_entry_queue_enterqueue(enter_time, callid, self.queue_name)
            self._insert_entry_queue_abandoned(leave_time, callid, self.queue_name, waittime)
            if start <= enter_time < start + datetime.timedelta(hours=1):
                expected.append({
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
            leave_time = start + datetime.timedelta(minutes=minute)
            waittime = self._random_time()
            enter_time = leave_time - datetime.timedelta(seconds=waittime)
            callid = str(143897234.123 + minute)
            self._insert_entry_queue_enterqueue(enter_time, callid, self.queue_name)
            self._insert_entry_queue_leaveempty(leave_time, callid, self.queue_name)
            if start <= enter_time < start + datetime.timedelta(hours=1):
                expected.append({
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
            delta = datetime.timedelta(minutes=minute)
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
        self._insert_entry_queue_full(datetime.datetime(2012, 07, 01, 7, 1, 1), 'delete_between_1', 'q1')
        self._insert_entry_queue_full(datetime.datetime(2012, 07, 01, 8, 1, 1), 'delete_between_2', 'q1')
        self._insert_entry_queue_full(datetime.datetime(2012, 07, 01, 9, 1, 1), 'delete_between_3', 'q1')
        self._insert_entry_queue_full(datetime.datetime(2012, 07, 01, 8, 1, 0), 'delete_between_4', 'q2')

        queue_log_dao.delete_event_by_queue_between(
            'FULL', 'q1', '2012-07-01 08:00:00.000000', '2012-07-01 08:59:59.999999')

        callids = [r.callid for r in self.session.query(QueueLog.callid)\
                                                 .filter(QueueLog.callid.like('delete_between_%'))]

        expected = ['delete_between_1', 'delete_between_3', 'delete_between_4']

        self.assertEquals(callids, expected)
