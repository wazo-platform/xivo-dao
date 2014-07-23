# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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
from mock import patch, Mock
from psycopg2.tests.testutils import unittest
from hamcrest import assert_that, equal_to
from xivo_dao.data_handler.queue_members.model import QueueMember
from xivo_dao.data_handler.queue_members import services as queue_members_services
from xivo_dao.alchemy.queuefeatures import QueueFeatures
from sqlalchemy.testing.assertions import assert_raises
from xivo_dao.data_handler.queue_members.exception import QueueNotExistsError


class TestQueueMembers(unittest.TestCase):

    @patch('xivo_dao.data_handler.queue_members.dao.get_by_queue_id_and_agent_id')
    @patch('xivo_dao.queue_dao.get')
    def test_get_by_queue_id_and_agent_id(self, patch_get_queue, patch_get_by_queue_id_and_agent_id):
        agent_id = 3
        queue_id = 2
        patch_get_queue.return_value = Mock(QueueFeatures)
        queue_member = patch_get_by_queue_id_and_agent_id.return_value = QueueMember(agent_id=agent_id, queue_id=queue_id, penalty=5)

        result = queue_members_services.get_by_queue_id_and_agent_id(queue_id, agent_id)

        patch_get_queue.assert_called_once_with(queue_id)
        patch_get_by_queue_id_and_agent_id.assert_called_once_with(queue_id, agent_id)
        assert_that(result, equal_to(queue_member))

    @patch('xivo_dao.data_handler.queue_members.dao.get_by_queue_id_and_agent_id')
    @patch('xivo_dao.queue_dao.get')
    def test_get_by_queue_id_and_agent_id_no_queue(self, patch_get_queue, patch_get_by_queue_id_and_agent_id):
        agent_id = 3
        queue_id = 2
        patch_get_queue.side_effect = LookupError

        assert_raises(QueueNotExistsError, queue_members_services.get_by_queue_id_and_agent_id, queue_id, agent_id)
