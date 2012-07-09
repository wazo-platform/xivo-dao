# -*- coding: utf-8 -*-
import datetime

from xivo_dao.alchemy.stat_queue_periodic import StatQueuePeriodic
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.alchemy.stat_queue import StatQueue
from xivo_dao import stat_queue_periodic_dao
from sqlalchemy import func


class TestStatQueuePeriodicDAO(DAOTestCase):

    tables = [StatQueue, StatQueuePeriodic]

    def setUp(self):
        self.empty_tables()

    def test_insert_periodic_stat(self):
        stats = {'full': 4,
                 'total': 10}
        period_start = datetime.datetime(2012, 01, 01, 00, 00, 00)

        stat_queue_periodic_dao.insert_stats(stats, period_start)

        try:
            result = self.session.query(StatQueuePeriodic).filter(StatQueuePeriodic.time == period_start)[0]

            self.assertEqual(result.full, 4)
            self.assertEqual(result.total, 10)
        except LookupError:
            self.assertTrue(False, 'Should have found a row')

    def test_clean_table(self):
        stats = {'full': 4,
                 'total': 10}
        period_start = datetime.datetime(2012, 01, 01, 00, 00, 00)

        stat_queue_periodic_dao.insert_stats(stats, period_start)

        stat_queue_periodic_dao.clean_table()

        total = self.session.query(func.count(StatQueuePeriodic.time))[0][0]

        self.assertEqual(total, 0)
