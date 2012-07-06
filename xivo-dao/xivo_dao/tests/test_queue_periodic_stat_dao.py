# -*- coding: utf-8 -*-
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.alchemy.queue_periodic_stat import QueuePeriodicStat
from xivo_dao.alchemy.queuefeatures import QueueFeatures


class TestQueuePeriodicStatDAO(DAOTestCase):

    tables = [QueueFeatures, QueuePeriodicStat]

    def setUp(self):
        self.empty_tables()

    def test_(self):
        pass
