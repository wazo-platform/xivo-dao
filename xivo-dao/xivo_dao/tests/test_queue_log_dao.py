# -*- coding: UTF-8 -*-

from xivo_dao import queue_log_dao
from xivo_dao.alchemy.queue_log import QueueLog
import datetime
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

        datetimestart = self._build_date(2012, 01, 01, 00, 00, 00)
        datetimeend = self._build_date(2012, 01, 01, 00, 59, 59)

        result = queue_log_dao.get_queue_full_call(datetimestart, datetimeend)

        self.assertEqual(sorted(result), sorted(expected_result))
