# -*- coding: UTF-8 -*-

from xivo_dao.alchemy.call_on_queue import CallOnQueue
from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_dao.tests.test_dao import DAOTestCase
import datetime
from xivo_dao import call_on_queue_dao


class TestCallOnQueueDAO(DAOTestCase):

    tables = [CallOnQueue, QueueFeatures]

    def setUp(self):
        self.empty_tables()

    @staticmethod
    def _build_date(year, month, day, hour=0, minute=0, second=0, micro=0):
        return datetime.datetime(year, month, day, hour, minute, second, micro).strftime("%Y-%m-%d %H:%M:%S.%f")

    def _insert_queue_to_queuefeatures(self):
        queue = QueueFeatures()
        queue.name = 'test_queue'
        queue.displayname = 'Queue Test'

        self.session.add(queue)
        self.session.commit()

        return queue.name, queue.id

    def test_add_full_call(self):
        timestamp = self._build_date(2012, 01, 02, 00, 00, 00)
        queue_name, _ = self._insert_queue_to_queuefeatures()

        call_on_queue_dao.add_full_call('callid', timestamp, queue_name)

        res = self.session.query(CallOnQueue).filter(CallOnQueue.callid == 'callid')

        self.assertEqual(res[0].callid, 'callid')

    def test_get_periodic_stats_full(self):
        start = datetime.datetime(2012, 01, 01, 00, 00, 00)
        end = datetime.datetime(2012, 01, 01, 00, 59, 59, 999999)
        stats = call_on_queue_dao.get_periodic_stats(start, end)

        self.assertEqual(stats['full'], 0)

        queue_name, _ = self._insert_queue_to_queuefeatures()

        for minute_increment in [-5, 5, 15, 22, 35, 65, 120]:
            delta = datetime.timedelta(minutes=minute_increment)
            time = start + delta
            call_on_queue_dao.add_full_call('callid%s' % minute_increment, time, queue_name)

        stats = call_on_queue_dao.get_periodic_stats(start, end)

        self.assertEqual(stats['full'], 4)

    def test_get_periodic_stats_total(self):
        start = datetime.datetime(2012, 01, 01, 00, 00, 00)
        end = datetime.datetime(2012, 01, 01, 00, 59, 59, 999999)
        stats = call_on_queue_dao.get_periodic_stats(start, end)

        self.assertEqual(stats['total'], 0)

        queue_name, queue_id = self._insert_queue_to_queuefeatures()

        for minute_increment in [-5, 5, 15, 22, 35, 65, 120]:
            delta = datetime.timedelta(minutes=minute_increment)
            time = start + delta
            call_on_queue_dao.add_full_call('callid%s' % minute_increment, time, queue_name)

        other_call = CallOnQueue()
        other_call.time = start
        other_call.callid = 'other type'
        other_call.queue_id = queue_id
        other_call.status = 'abandoned'

        self.session.add(other_call)
        self.session.commit()

        stats = call_on_queue_dao.get_periodic_stats(start, end)

        self.assertEqual(stats['total'], 5)

    def test_get_most_recent_time(self):
        start = datetime.datetime(2012, 01, 01, 00, 00, 00)

        queue_name, queue_id = self._insert_queue_to_queuefeatures()

        for minute_increment in [-5, 5, 15, 22, 35, 65, 120]:
            delta = datetime.timedelta(minutes=minute_increment)
            time = start + delta
            call_on_queue_dao.add_full_call('callid%s' % minute_increment, time, queue_name)

        result = call_on_queue_dao.get_most_recent_time()
        expected = start + datetime.timedelta(minutes=120)

        self.assertEqual(result, expected)
