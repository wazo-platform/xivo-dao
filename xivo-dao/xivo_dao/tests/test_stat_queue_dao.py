# -*- coding: UTF-8 -*-

from xivo_dao.alchemy.stat_queue import StatQueue
from xivo_dao import stat_queue_dao
from xivo_dao.tests.test_dao import DAOTestCase


class TestStatQueueDAO(DAOTestCase):

    tables = [StatQueue]

    def setUp(self):
        self.empty_tables()

    def test_id_from_name(self):
        queue = StatQueue()
        queue.name = 'test_queue'

        self.session.add(queue)
        self.session.commit()

        result = stat_queue_dao.id_from_name(queue.name)

        self.assertEqual(result, queue.id)

    def test_insert_if_missing(self):
        old_queues = ['queue_%s' % number for number in range(5)]
        for queue_name in old_queues:
            queue = StatQueue()
            queue.name = queue_name
            self.session.add(queue)
        self.session.commit()

        new_queues = ['queue_%s' % number for number in range(5, 10)]

        all_queues = sorted(old_queues + new_queues)

        stat_queue_dao.insert_if_missing(all_queues)

        result = sorted([r.name for r in self.session.query(StatQueue.name)])

        self.assertEqual(result, all_queues)
