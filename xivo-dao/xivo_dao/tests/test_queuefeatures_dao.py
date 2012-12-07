# vim: set fileencoding=utf-8 :

# Copyright (C) 2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall SAS. See the LICENSE file at top of the
# source tree or delivered in the installable package in which XiVO CTI Server
# is distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_dao import queue_features_dao
from xivo_dao.tests.test_dao import DAOTestCase


class TestQueueFeaturesDAO(DAOTestCase):

    tables = [QueueFeatures]

    def setUp(self):
        self.empty_tables()

    def test_id_from_name(self):
        queue = QueueFeatures()
        queue.name = 'test_queue'
        queue.displayname = 'Queue Test'

        self.session.add(queue)
        self.session.commit()

        result = queue_features_dao.id_from_name(queue.name)

        self.assertEqual(result, queue.id)

    def test_queue_name(self):
        queue = QueueFeatures()
        queue.name = 'my_queue'
        queue.displayname = 'My Queue'

        self.session.add(queue)
        self.session.commit()

        result = queue_features_dao.queue_name(queue.id)

        self.assertEquals(result, 'my_queue')

    def test_is_a_queue(self):
        self.assertFalse(queue_features_dao.is_a_queue('not_a_queue'))

        queue = QueueFeatures()
        queue.name = 'a_queue'
        queue.displayname = 'My queue'

        self.session.add(queue)
        self.session.commit()

        self.assertTrue(queue_features_dao.is_a_queue('a_queue'))

    def test_get_queue_name(self):
        self.assertRaises(LookupError, queue_features_dao.get_queue_name, 1)

        queue = QueueFeatures()
        queue.name = 'my_queue'
        queue.displayname = 'My Queue'

        self.session.add(queue)
        self.session.commit()

        result = queue_features_dao.get_queue_name(queue.id)

        self.assertEqual(result, queue.name)

    def test_get_name_number(self):
        self.assertRaises(LookupError, queue_features_dao.get_queue_name, 1)

        queue = QueueFeatures()
        queue.name = 'my_queue'
        queue.displayname = 'My Queue'
        queue.number = '3000'

        self.session.add(queue)
        self.session.commit()

        name, number = queue_features_dao.get_display_name_number(queue.id)

        self.assertEqual(name, 'My Queue')
        self.assertEqual(number, '3000')
