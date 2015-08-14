# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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

from hamcrest import assert_that, equal_to

from sqlalchemy.exc import SQLAlchemyError
from xivo_dao import agent_dao
from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.tests.helpers.session import mocked_dao_session
from xivo_dao.tests.test_dao import DAOTestCase


class TestAgentDAO(DAOTestCase):

    agent_number = '1234'
    agent1_number = '1001'
    agent2_number = '1002'
    agent_context = 'test'

    def test_agent_context(self):
        agent = self._insert_agent()

        context = agent_dao.agent_context(agent.id)

        self.assertEqual(context, self.agent_context)

    def test_agent_context_bad_args(self):
        self.assertRaises(ValueError, agent_dao.agent_context, None)

    def test_agent_interface(self):
        agent = self._insert_agent()

        interface = agent_dao.agent_interface(agent.id)

        self.assertEqual(interface, 'Agent/%s' % self.agent_number)

    def test_agent_interface_bad_args(self):
        self.assertRaises(ValueError, agent_dao.agent_interface, None)

    def test_agent_interface_not_exist(self):
        self.assertRaises(LookupError, agent_dao.agent_interface(1))

    def test_add_agent(self):
        agent = AgentFeatures()
        agent.numgroup = 6
        agent.number = '15'
        agent.passwd = ''
        agent.context = self.agent_context
        agent.language = ''
        agent.description = ''
        agent_dao.add_agent(agent)
        self.assertTrue(agent.id > 0)
        self.assertTrue(agent.number == '15')

    def test_add_agent_bad_args(self):
        self.assertRaises(ValueError, agent_dao.add_agent, None)

    def test_del_agent(self):
        agent_dao.del_agent(self._insert_agent().id)
        self.assertTrue(agent_dao.all() == [])

    def test_del_agent_bad_args(self):
        self.assertRaises(ValueError, agent_dao.del_agent, None)

    @mocked_dao_session
    def test_del_agent_db_error(self, session):
        session.commit.side_effect = SQLAlchemyError()

        self.assertRaises(SQLAlchemyError, agent_dao.del_agent, 1)
        session.rollback.assert_called_once_with()

    def test_agent_with_id(self):
        agent = self._insert_agent()
        queue_member = self._insert_queue_member('foobar', 'Agent/2', agent.id)
        queue = self._insert_queue(64, queue_member.queue_name)

        result = agent_dao.agent_with_id(agent.id)

        self.assertEqual(result.id, agent.id)
        self.assertEqual(result.number, agent.number)
        self.assertEqual(len(result.queues), 1)
        self.assertEqual(result.queues[0].id, queue.id)
        self.assertEqual(result.queues[0].name, queue_member.queue_name)
        self.assertEqual(result.queues[0].penalty, queue_member.penalty)

    def test_agent_with_id_not_exist(self):
        self.assertRaises(LookupError, agent_dao.agent_with_id, 1)

    def test_agent_with_number(self):
        agent = self._insert_agent()

        result = agent_dao.agent_with_number(agent.number)

        assert_that(result.id, equal_to(agent.id))
        assert_that(result.number, equal_to(agent.number))

    def test_agent_with_number_not_exist(self):
        self.assertRaises(LookupError, agent_dao.agent_with_number, '1234')

    def test_get(self):
        agent = self._insert_agent()

        result = agent_dao.get(agent.id)

        assert_that(result.id, equal_to(agent.id))
        assert_that(result.numgroup, equal_to(agent.numgroup))
        assert_that(result.number, equal_to(agent.number))
        assert_that(result.passwd, equal_to(agent.passwd))
        assert_that(result.context, equal_to(agent.context))
        assert_that(result.language, equal_to(agent.language))

    def test_get_not_exist(self):
        result = agent_dao.get(1)

        assert_that(result, equal_to(None))

    def test_all(self):
        agent1 = self._insert_agent(self.agent1_number)
        agent2 = self._insert_agent(self.agent2_number)

        expected = [agent1, agent2]

        result = agent_dao.all()

        assert_that(result, equal_to(expected))

    def test_all_empty(self):
        result = agent_dao.all()
        self.assertEqual([], result)

    def _insert_agent(self, number=agent_number):
        agent = AgentFeatures()
        agent.numgroup = 6
        agent.number = number
        agent.passwd = ''
        agent.context = self.agent_context
        agent.language = ''
        agent.description = ''

        self.add_me(agent)

        return agent

    def _insert_queue(self, queue_id, name):
        queue = QueueFeatures()
        queue.id = queue_id
        queue.name = name
        queue.displayname = name
        queue.number = '3000'

        self.add_me(queue)

        return queue

    def _insert_queue_member(self, queue_name, member_name, agent_id=1, penalty=0):
        queue_member = QueueMember()
        queue_member.queue_name = queue_name
        queue_member.interface = member_name
        queue_member.penalty = penalty
        queue_member.usertype = 'agent'
        queue_member.userid = agent_id
        queue_member.channel = 'foobar'
        queue_member.category = 'queue'
        queue_member.position = 0

        self.add_me(queue_member)

        return queue_member
