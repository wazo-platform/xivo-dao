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
from mock import patch
from xivo_dao.data_handler.queue_members import validator
from xivo_dao.data_handler.queue_members.exception import QueueNotExistsError, \
    QueueMemberNotExistsError
from xivo_dao.data_handler.queue_members.model import QueueMember


class TestQueueMembersValidator(unittest.TestCase):

    @patch('xivo_dao.queue_dao.get')
    @patch('xivo_dao.data_handler.queue_members.dao.get_by_queue_id_and_agent_id')
    def test_validate_edit_agent_queue_association(self, patch_get_by_queue_and_agent, patch_get_queue):
        queue_member = QueueMember(agent_id=3, queue_id=5, penalty=3)
        validator.validate_edit_agent_queue_association(queue_member)

        patch_get_queue.assert_called_once_with(queue_member.queue_id)
        patch_get_by_queue_and_agent.assert_called_once_with(queue_member.queue_id, queue_member.agent_id)

    @patch('xivo_dao.queue_dao.get')
    @patch('xivo_dao.data_handler.queue_members.dao.get_by_queue_id_and_agent_id')
    def test_validate_edit_agent_queue_association_no_such_queue(self, patch_get_by_queue_and_agent, patch_get_queue):
        patch_get_queue.side_effect = LookupError
        queue_member = QueueMember(agent_id=3, queue_id=5, penalty=3)
        self.assertRaises(QueueNotExistsError, validator.validate_edit_agent_queue_association, queue_member)

    @patch('xivo_dao.queue_dao.get')
    @patch('xivo_dao.data_handler.queue_members.dao.get_by_queue_id_and_agent_id')
    def test_validate_edit_agent_queue_association_no_such_association(self, patch_get_by_queue_and_agent, patch_get_queue):
        patch_get_by_queue_and_agent.side_effect = QueueMemberNotExistsError('QueueMember')
        queue_member = QueueMember(agent_id=3, queue_id=5, penalty=3)
        self.assertRaises(QueueMemberNotExistsError, validator.validate_edit_agent_queue_association, queue_member)
