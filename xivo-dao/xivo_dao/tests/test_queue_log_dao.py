# -*- coding: UTF-8 -*-
import datetime

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

    def _insert_entry_queue(self, event, timestamp, callid, queuename):
        queue_log = QueueLog()
        queue_log.time = timestamp
        queue_log.callid = callid
        queue_log.queuename = queuename
        queue_log.event = event
        self.session.add(queue_log)
        self.session.commit()

    def _insert_entry_queue_full(self, timestamp, callid, queuename):
        self._insert_entry_queue('FULL', timestamp, callid, queuename)

    def _insert_entry_queue_joinempty(self, timestamp, callid, queuename):
        self._insert_entry_queue('JOINEMPTY', timestamp, callid, queuename)

    def _insert_entry_queue_leaveempty(self, timestamp, callid, queuename):
        self._insert_entry_queue('LEAVEEMPTY', timestamp, callid, queuename)

    def _insert_entry_queue_closed(self, timestamp, callid, queuename):
        self._insert_entry_queue('CLOSED', timestamp, callid, queuename)

    def _insert_entry_queue_answered(self, timestamp, callid, queuename):
        self._insert_entry_queue('CONNECT', timestamp, callid, queuename)

    def _insert_entry_queue_abandoned(self, timestamp, callid, queuename):
        self._insert_entry_queue('ABANDON', timestamp, callid, queuename)

    def _insert_entry_queue_timeout(self, timestamp, callid, queuename):
        self._insert_entry_queue('EXITWITHTIMEOUT', timestamp, callid, queuename)

    @staticmethod
    def _build_date(year, month, day, hour=0, minute=0, second=0, micro=0):
        return datetime.datetime(year, month, day, hour, minute, second, micro).strftime(TIMESTAMP_FORMAT)

    @staticmethod
    def _build_timestamp(t):
        return t.strftime(TIMESTAMP_FORMAT)

    def test_get_first_time(self):
        queuename = 'q1'
        for minute in [0, 10, 20, 30, 40, 50]:
            datetimewithmicro = self._build_date(2012, 01, 01, 00, minute, 59)
            callid = str(12345678.123 + minute)
            self._insert_entry_queue_full(datetimewithmicro, callid, queuename)

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

    def _insert_ev_fn(self, event_name):
        return {'abandoned': self._insert_entry_queue_abandoned,
                'answered': self._insert_entry_queue_answered,
                'closed': self._insert_entry_queue_closed,
                'full': self._insert_entry_queue_full,
                'joinempty': self._insert_entry_queue_joinempty,
                'leaveempty': self._insert_entry_queue_leaveempty,
                'timeout': self._insert_entry_queue_timeout}[event_name]

    def _insert_event_list(self, event_name, start, minutes):
        expected = []
        for minute in minutes:
            delta = datetime.timedelta(minutes=minute)
            t = self._build_timestamp(start + delta)
            callid = str(1234567.123 + minute)
            self._insert_ev_fn(event_name)(t, callid, self.queue_name)
            if 0 <= minute < 60:
                expected.append({'queue_name': self.queue_name,
                                 'event': event_name,
                                 'time': t,
                                 'callid': callid})

        return expected
