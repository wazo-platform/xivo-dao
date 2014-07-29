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
import unittest
from hamcrest import assert_that, equal_to
from xivo_dao.data_handler.queue_members.model import QueueMemberAgent
from xivo_dao.data_handler.queue_members import services as queue_members_services
from mock import patch


class TestQueueMembers(unittest.TestCase):

    @patch('xivo_dao.data_handler.queue_members.validator.validate_get_agent_queue_association')
    @patch('xivo_dao.data_handler.queue_members.dao.get_by_queue_id_and_agent_id')
    def test_get_by_queue_id_and_agent_id(self, patch_get_by_queue_id_and_agent_id, patch_validate):
        agent_id = 3
        queue_id = 2
        queue_member = patch_get_by_queue_id_and_agent_id.return_value = QueueMemberAgent(agent_id=agent_id, queue_id=queue_id, penalty=5)

        result = queue_members_services.get_by_queue_id_and_agent_id(queue_id, agent_id)

        patch_validate.assert_called_once_with(queue_id, agent_id)
        patch_get_by_queue_id_and_agent_id.assert_called_once_with(queue_id, agent_id)
        assert_that(result, equal_to(queue_member))

    @patch('xivo_dao.data_handler.queue_members.notifier.agent_queue_association_updated')
    @patch('xivo_dao.data_handler.queue_members.dao.edit_agent_queue_association')
    @patch('xivo_dao.data_handler.queue_members.validator.validate_edit_agent_queue_association')
    def test_edit_agent_queue_association(self, patch_validate_edit_agent, patch_edit_agent, patch_notify_edition):
        queue_member = QueueMemberAgent(agent_id=12, queue_id=2, penalty=4)

        queue_members_services.edit_agent_queue_association(queue_member)

        patch_validate_edit_agent.assert_called_once_with(queue_member)
        patch_edit_agent.assert_called_once_with(queue_member)
        patch_notify_edition.assert_called_once_with(queue_member)
