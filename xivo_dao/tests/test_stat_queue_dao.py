# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao import stat_queue_dao
from xivo_dao.alchemy.stat_queue import StatQueue
from xivo_dao.helpers.db_utils import flush_session
from xivo_dao.tests.test_dao import DAOTestCase


class TestStatQueueDAO(DAOTestCase):

    def test_id_from_name(self):
        queue = self._insert_queue('test_queue')

        result = stat_queue_dao.id_from_name(queue.name)

        self.assertEqual(result, queue.id)

    def test_insert_if_missing(self):
        old_queues = ['queue_%s' % number for number in range(5)]
        for queue_name in old_queues:
            self._insert_queue(queue_name)

        new_queues = ['queue_%s' % number for number in range(5, 10)]

        all_queues = sorted(old_queues + new_queues)

        with flush_session(self.session):
            stat_queue_dao.insert_if_missing(self.session, all_queues)

        result = sorted(r.name for r in self.session.query(StatQueue.name))

        self.assertEqual(result, all_queues)

    def test_clean_table(self):
        self._insert_queue('queue1')

        stat_queue_dao.clean_table(self.session)

        self.assertTrue(self.session.query(StatQueue).first() is None)

    def _insert_queue(self, name):
        queue = StatQueue()
        queue.name = name

        self.add_me(queue)

        return queue
