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

    def _insert_entry_queue(self, event, timestamp, callid, queuename,
                            d1=None, d2=None, d3=None, d4=None, d5=None):
        queue_log = QueueLog()
        queue_log.time = timestamp
        queue_log.callid = callid
        queue_log.queuename = queuename
        queue_log.event = event
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

    def _insert_entry_queue_full(self, timestamp, callid, queuename, waittime):
        self._insert_entry_queue('FULL', timestamp, callid, queuename)

    def _insert_entry_queue_joinempty(self, timestamp, callid, queuename, waittime):
        self._insert_entry_queue('JOINEMPTY', timestamp, callid, queuename)

    def _insert_entry_queue_leaveempty(self, timestamp, callid, queuename, waittime):
        wait = datetime.timedelta(seconds=waittime, microseconds=1)
        end = self._time_from_timestamp(timestamp)
        start = end - wait
        self._insert_entry_queue('ENTERQUEUE', self._build_timestamp(start), callid, queuename)
        self._insert_entry_queue('LEAVEEMPTY', timestamp, callid, queuename)

    def _insert_entry_queue_closed(self, timestamp, callid, queuename, waittime):
        self._insert_entry_queue('CLOSED', timestamp, callid, queuename)

    def _insert_entry_queue_answered(self, timestamp, callid, queuename, waittime):
        self._insert_entry_queue('CONNECT', timestamp, callid, queuename, d1=waittime)

    def _insert_entry_queue_abandoned(self, timestamp, callid, queuename, waittime):
        self._insert_entry_queue('ABANDON', timestamp, callid, queuename, d3=waittime)

    def _insert_entry_queue_timeout(self, timestamp, callid, queuename, waittime):
        self._insert_entry_queue('EXITWITHTIMEOUT', timestamp, callid, queuename, d3=waittime)

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
            datetimewithmicro = self._build_date(2012, 01, 01, 00, minute, 59)
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

    def test_get_queue_answered_call(self):
        start = datetime.datetime(2012, 01, 01, 01, 00, 00)
        expected = self._insert_event_list('answered', start, [-1, 0, 10, 30, 59, 60, 120])

        result = queue_log_dao.get_queue_answered_call(start, start + ONE_HOUR - ONE_MICROSECOND)

        self.assertEqual(sorted(result), sorted(expected))

    def test_get_queue_abandoned_call(self):
        start = datetime.datetime(2012, 01, 01, 01, 00, 00)
        expected = self._insert_event_list('abandoned', start, [-1, 0, 10, 30, 59, 60, 120])

        result = queue_log_dao.get_queue_abandoned_call(start, start + ONE_HOUR - ONE_MICROSECOND)

        self.assertEqual(sorted(result), sorted(expected))

    def test_get_queue_timeout_call(self):
        start = datetime.datetime(2012, 01, 01, 01, 00, 00)
        expected = self._insert_event_list('timeout', start, [-1, 0, 10, 30, 59, 60, 120])

        result = queue_log_dao.get_queue_timeout_call(start, start + ONE_HOUR - ONE_MICROSECOND)

        self.assertEqual(sorted(result), sorted(expected))

    def test_get_queue_joinempty_call(self):
        start = datetime.datetime(2012, 01, 01, 01, 00, 00)
        expected = self._insert_event_list('joinempty', start, [-1, 0, 10, 30, 59, 60, 120])

        result = queue_log_dao.get_queue_joinempty_call(start, start + ONE_HOUR - ONE_MICROSECOND)

        self.assertEqual(sorted(result), sorted(expected))

    def test_get_queue_leaveempty_call(self):
        start = datetime.datetime(2012, 01, 01, 01, 00, 00)
        expected = self._insert_event_list('leaveempty', start, [-1, 0, 10, 30, 59, 60, 120])

        result = queue_log_dao.get_queue_leaveempty_call(start, start + ONE_HOUR - ONE_MICROSECOND)

        self.assertEqual(sorted(result), sorted(expected))

    def test_get_queue_leaveempty_call_no_enterqueue(self):
        start = datetime.datetime(2012, 01, 01, 01, 00, 00)
        timestamp = self._build_timestamp(start)
        self._insert_entry_queue('LEAVEEMPTY', timestamp, '123456.34', self.queue_name)
        result = queue_log_dao.get_queue_leaveempty_call(start, start + ONE_HOUR - ONE_MICROSECOND)

        self.assertEqual(result[0]['waittime'], 0)

    def _insert_ev_fn(self, event_name):
        return {'abandoned': self._insert_entry_queue_abandoned,
                'answered': self._insert_entry_queue_answered,
                'closed': self._insert_entry_queue_closed,
                'full': self._insert_entry_queue_full,
                'joinempty': self._insert_entry_queue_joinempty,
                'leaveempty': self._insert_entry_queue_leaveempty,
                'timeout': self._insert_entry_queue_timeout}[event_name]

    @staticmethod
    def _random_wait_time():
        return int(round(random.random() * 10))

    def _insert_event_list(self, event_name, start, minutes):
        expected = []
        for minute in minutes:
            delta = datetime.timedelta(minutes=minute)
            t = self._build_timestamp(start + delta)
            callid = str(1234567.123 + minute)
            waittime = 0
            if event_name in ['answered', 'abandoned', 'timeout', 'leaveempty']:
                waittime = self._random_wait_time()
            self._insert_ev_fn(event_name)(t, callid, self.queue_name, waittime)
            if 0 <= minute < 60:
                expected.append({'queue_name': self.queue_name,
                                 'event': event_name,
                                 'time': t,
                                 'callid': callid,
                                 'waittime': waittime})

        return expected
