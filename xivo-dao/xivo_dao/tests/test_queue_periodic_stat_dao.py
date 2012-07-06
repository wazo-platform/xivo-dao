# -*- coding: utf-8 -*-
import datetime

from xivo_dao import queue_periodic_stat_dao
from xivo_dao.alchemy.queue_periodic_stat import QueuePeriodicStat
from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_dao.tests.test_dao import DAOTestCase


class TestQueuePeriodicStatDAO(DAOTestCase):

    tables = [QueueFeatures, QueuePeriodicStat]

    def setUp(self):
        self.empty_tables()

    def test_insert_periodic_stat(self):
        stats = {'full': 4,
                 'total': 10}
        period_start = datetime.datetime(2012, 01, 01, 00, 00, 00)

        queue_periodic_stat_dao.insert_stats(stats, period_start)

        try:
            result = self.session.query(QueuePeriodicStat).filter(QueuePeriodicStat.time == period_start)[0]

            self.assertEqual(result.full, 4)
            self.assertEqual(result.total, 10)
        except LookupError:
            self.assertTrue(False, 'Should have found a row')
