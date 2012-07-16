# -*- coding: UTF-8 -*-
import datetime

from xivo_dao import queue_log_dao
from xivo_dao.alchemy.queue_log import QueueLog
from xivo_dao.tests.test_dao import DAOTestCase


class TestQueueLogDAO(DAOTestCase):

    tables = [QueueLog]

    def setUp(self):
        self.empty_tables()

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

    def _insert_entry_queue_closed(self, timestamp, callid, queuename):
        self._insert_entry_queue('CLOSED', timestamp, callid, queuename)

    @staticmethod
    def _build_date(year, month, day, hour=0, minute=0, second=0, micro=0):
        return datetime.datetime(year, month, day, hour, minute, second, micro).strftime("%Y-%m-%d %H:%M:%S.%f")

    def test_get_queue_full_call(self):
        queuename = 'q1'
        expected_result = []
        for minute in [0, 10, 20, 30, 40, 50]:
            datetimewithmicro = self._build_date(2012, 01, 01, 00, minute, 00)
            callid = str(12345678.123 + minute)
            self._insert_entry_queue_full(datetimewithmicro, callid, queuename)
            expected_result.append({'queue_name': queuename,
                                    'event': 'full',
                                    'time': datetimewithmicro,
                                    'callid': callid})
        after = self._build_date(2012, 01, 02, 00, 00, 00)
        self._insert_entry_queue_full(after, '1234.123', queuename)
        self._insert_entry_queue_closed(after, '1234.124', queuename)

        before = self._build_date(2011, 12, 31, 00, 00, 00)
        self._insert_entry_queue_full(before, '5555555.123', queuename)
        self._insert_entry_queue_closed(before, '5555555.124', queuename)

        datetimestart = datetime.datetime(2012, 01, 01, 00, 00, 00)
        datetimeend = datetime.datetime(2012, 01, 01, 00, 59, 59)

        result = queue_log_dao.get_queue_full_call(datetimestart, datetimeend)

        self.assertEqual(sorted(result), sorted(expected_result))

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

    def test_get_queue_closed_call(self):
        queuename = 'q1'
        expected_result = []
        for minute in [0, 10, 20, 30, 40, 50]:
            datetimewithmicro = self._build_date(2012, 01, 01, 00, minute, 00)
            callid = str(12345678.123 + minute)
            self._insert_entry_queue_closed(datetimewithmicro, callid, queuename)
            expected_result.append({'queue_name': queuename,
                                    'event': 'closed',
                                    'time': datetimewithmicro,
                                    'callid': callid})
        after = self._build_date(2012, 01, 02, 00, 00, 00)
        self._insert_entry_queue_full(after, '1234.123', queuename)
        self._insert_entry_queue_closed(after, '1234.124', queuename)

        before = self._build_date(2011, 12, 31, 00, 00, 00)
        self._insert_entry_queue_full(before, '5555555.123', queuename)
        self._insert_entry_queue_closed(before, '5555555.124', queuename)

        datetimestart = datetime.datetime(2012, 01, 01, 00, 00, 00)
        datetimeend = datetime.datetime(2012, 01, 01, 00, 59, 59)

        result = queue_log_dao.get_queue_closed_call(datetimestart, datetimeend)

        self.assertEqual(sorted(result), sorted(expected_result))
