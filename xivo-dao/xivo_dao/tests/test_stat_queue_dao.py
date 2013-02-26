# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from xivo_dao.alchemy.stat_queue import StatQueue
from xivo_dao import stat_queue_dao
from xivo_dao.tests.test_dao import DAOTestCase


class TestStatQueueDAO(DAOTestCase):

    tables = [StatQueue]

    def setUp(self):
        self.empty_tables()

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

        self.session.begin()
        stat_queue_dao.insert_if_missing(self.session, all_queues)
        self.session.commit()

        result = sorted(r.name for r in self.session.query(StatQueue.name))

        self.assertEqual(result, all_queues)

    def test_clean_table(self):
        self._insert_queue('queue1')

        stat_queue_dao.clean_table(self.session)

        self.assertTrue(self.session.query(StatQueue).first() is None)

    def _insert_queue(self, name):
        queue = StatQueue()
        queue.name = name

        self.session.begin()
        self.session.add(queue)
        self.session.commit()

        return queue
