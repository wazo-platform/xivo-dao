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
