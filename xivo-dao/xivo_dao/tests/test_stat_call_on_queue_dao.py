# -*- coding: UTF-8 -*-

from xivo_dao.alchemy.stat_call_on_queue import StatCallOnQueue
from xivo_dao.tests.test_dao import DAOTestCase
import datetime
from xivo_dao import stat_call_on_queue_dao
from xivo_dao.alchemy.stat_queue import StatQueue


class TestStatCallOnQueueDAO(DAOTestCase):

    tables = [StatCallOnQueue, StatQueue]

    def setUp(self):
        self.empty_tables()

    @staticmethod
    def _build_date(year, month, day, hour=0, minute=0, second=0, micro=0):
        return datetime.datetime(year, month, day, hour, minute, second, micro).strftime("%Y-%m-%d %H:%M:%S.%f")

    def _insert_queue_to_stat_queue(self):
        queue = StatQueue()
        queue.name = 'test_queue'

        self.session.add(queue)
        self.session.commit()

        return queue.name, queue.id

    def test_add_full_call(self):
        timestamp = self._build_date(2012, 01, 02, 00, 00, 00)
        queue_name, _ = self._insert_queue_to_stat_queue()

        stat_call_on_queue_dao.add_full_call('callid', timestamp, queue_name)

        res = self.session.query(StatCallOnQueue).filter(StatCallOnQueue.callid == 'callid')

        self.assertEqual(res[0].callid, 'callid')

    def test_get_periodic_stats_full(self):
        start = datetime.datetime(2012, 01, 01, 00, 00, 00)
        end = datetime.datetime(2012, 01, 01, 00, 59, 59, 999999)
        stats = stat_call_on_queue_dao.get_periodic_stats(start, end)

        self.assertEqual(stats['full'], 0)

        queue_name, _ = self._insert_queue_to_stat_queue()

        for minute_increment in [-5, 5, 15, 22, 35, 65, 120]:
            delta = datetime.timedelta(minutes=minute_increment)
            time = start + delta
            stat_call_on_queue_dao.add_full_call('callid%s' % minute_increment, time, queue_name)

        stats = stat_call_on_queue_dao.get_periodic_stats(start, end)

        self.assertEqual(stats['full'], 4)

    def test_get_periodic_stats_total(self):
        start = datetime.datetime(2012, 01, 01, 00, 00, 00)
        end = datetime.datetime(2012, 01, 01, 00, 59, 59, 999999)
        stats = stat_call_on_queue_dao.get_periodic_stats(start, end)

        self.assertEqual(stats['total'], 0)

        queue_name, queue_id = self._insert_queue_to_stat_queue()

        for minute_increment in [-5, 5, 15, 22, 35, 65, 120]:
            delta = datetime.timedelta(minutes=minute_increment)
            time = start + delta
            stat_call_on_queue_dao.add_full_call('callid%s' % minute_increment, time, queue_name)

        other_call = StatCallOnQueue()
        other_call.time = start
        other_call.callid = 'other type'
        other_call.queue_id = queue_id
        other_call.status = 'abandoned'

        self.session.add(other_call)
        self.session.commit()

        stats = stat_call_on_queue_dao.get_periodic_stats(start, end)

        self.assertEqual(stats['total'], 5)

    def test_get_most_recent_time(self):
        start = datetime.datetime(2012, 01, 01, 00, 00, 00)

        queue_name, queue_id = self._insert_queue_to_stat_queue()

        for minute_increment in [-5, 5, 15, 22, 35, 65, 120]:
            delta = datetime.timedelta(minutes=minute_increment)
            time = start + delta
            stat_call_on_queue_dao.add_full_call('callid%s' % minute_increment, time, queue_name)

        result = stat_call_on_queue_dao.get_most_recent_time()
        expected = start + datetime.timedelta(minutes=120)

        self.assertEqual(result, expected)
