# -*- coding: UTF-8 -*-

from xivo_dao.alchemy.call_on_queue import CallOnQueue
from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_dao.tests.test_dao import DAOTestCase
import datetime


class TestCallOnQueueDAO(DAOTestCase):

    tables = [CallOnQueue, QueueFeatures]

    def setUp(self):
        self.empty_tables()

    @staticmethod
    def _build_date(year, month, day, hour=0, minute=0, second=0, micro=0):
        return datetime.datetime(year, month, day, hour, minute, second, micro).strftime("%Y-%m-%d %H:%M:%S.%f")

    def _insert_entry(self, status, timestamp, callid, queue_id):
        call_on_queue = CallOnQueue()
        call_on_queue.time = timestamp
        call_on_queue.callid = callid
        call_on_queue.queue_id = queue_id
        call_on_queue.status = status
        self.session.add(call_on_queue)
        self.session.commit()

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
        self._insert_entry('full', timestamp, 'callid', queue_id)

        res = (self.session.query(CallOnQueue.time, CallOnQueue.callid, CallOnQueue.queue_id))

        self.assertEqual(res.count(), 1)
