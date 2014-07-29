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
from hamcrest import assert_that, all_of, has_property

from xivo_dao.data_handler.queue_members import dao as queue_members_dao
from xivo_dao.data_handler.queue_members.exception import QueueMemberNotExistsError
from xivo_dao.data_handler.queue_members.model import QueueMemberAgent
from xivo_dao.tests.test_dao import DAOTestCase


class TestQueueAgentAssociation(DAOTestCase):

    def test_get_by_queue_and_agent_id(self):
        agent_id = 23
        queue_id = 2
        penalty = 5
        queue_name = 'myqueue'
        self.add_queuefeatures(id=queue_id, name=queue_name)
        self.add_agent(id=agent_id, number='1200')
        self.add_queue_member(queue_name=queue_name,
                              interface='Agent/1200',
                              penalty=penalty,
                              usertype='agent',
                              userid=agent_id,
                              channel='Agent',
                              category='queue')

        result = queue_members_dao.get_by_queue_id_and_agent_id(queue_id, agent_id)

        assert_that(result, all_of(has_property('penalty', penalty),
                                   has_property('agent_id', agent_id),
                                   has_property('queue_id', queue_id)))

    def test_get_by_queue_and_agent_id_not_exists(self):
        self.assertRaises(QueueMemberNotExistsError, queue_members_dao.get_by_queue_id_and_agent_id, 1, 8)

    def test_edit_agent_queue_association(self):
        agent_id = 23
        queue_id = 2
        penalty = 4
        queue_name = 'myqueue'
        self.add_queuefeatures(id=queue_id, name=queue_name)
        self.add_agent(id=agent_id, number='1200')
        self.add_queue_member(queue_name=queue_name, interface='Agent/1200', penalty=penalty, usertype='agent', userid=agent_id, channel='Agent', category='queue')

        queue_member = QueueMemberAgent(agent_id=agent_id, queue_id=queue_id, penalty=6)
        queue_members_dao.edit_agent_queue_association(queue_member)

        assert_that(queue_members_dao.get_by_queue_id_and_agent_id(queue_id, agent_id), has_property('penalty', 6))
