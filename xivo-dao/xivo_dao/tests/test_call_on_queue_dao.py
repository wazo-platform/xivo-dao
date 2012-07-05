# -*- coding: UTF-8 -*-

from xivo_dao.alchemy.call_on_queue import CallOnQueue
from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_dao.tests.test_dao import DAOTestCase
import datetime
from xivo_dao.call_on_queue_dao import add_full_call


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

        return queue.id

    def test_add_full_call(self):
        timestamp = self._build_date(2012, 01, 02, 00, 00, 00)
        queue_id = self._insert_queue_to_queuefeatures()

        add_full_call('callid', timestamp, queue_id)

        res = self.session.query(CallOnQueue).filter(CallOnQueue.callid == 'callid')

        self.assertEqual(res[0].callid, 'callid')
