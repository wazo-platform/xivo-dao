# vim: set fileencoding=utf-8 :
# XiVO CTI Server

# Copyright (C) 2007-2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Pro-formatique SARL. See the LICENSE file at top of the
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

from xivo_dao import agent_dao
from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.tests.test_dao import DAOTestCase


class TestAgentDAO(DAOTestCase):

    agent_number = '1234'
    agent_context = 'test'

    tables = [AgentFeatures, QueueMember]

    def setUp(self):
        self.empty_tables()

    def test_agent_number(self):
        agent = self._insert_agent()

        number = agent_dao.agent_number(agent.id)

        self.assertEqual(number, self.agent_number)

    def test_agent_context(self):
        agent = self._insert_agent()

        context = agent_dao.agent_context(agent.id)

        self.assertEqual(context, self.agent_context)

    def test_agent_number_unknown(self):
        self.assertRaises(LookupError, lambda: agent_dao.agent_number(-1))

    def test_agent_interface(self):
        agent = self._insert_agent()

        interface = agent_dao.agent_interface(agent.id)

        self.assertEqual(interface, 'Agent/%s' % self.agent_number)

    def test_agent_id(self):
        agent = self._insert_agent()

        agent_id = agent_dao.agent_id(self.agent_number)

        self.assertEqual(str(agent.id), agent_id)

    def test_agent_id_inexistant(self):
        self.assertRaises(LookupError, agent_dao.agent_id, '2345')

    def test_agent_with_id(self):
        agent = self._insert_agent()
        queue_member = self._insert_queue_member('foobar', 'Agent/2', agent.id)

        result = agent_dao.agent_with_id(agent.id)

        self.assertEqual(result.id, agent.id)
        self.assertEqual(result.number, agent.number)
        self.assertEqual(len(result.queues), 1)
        self.assertEqual(result.queues[0].name, queue_member.queue_name)
        self.assertEqual(result.queues[0].penalty, queue_member.penalty)
        self.assertEqual(result.queues[0].skills, queue_member.skills)

    def _insert_agent(self):
        agent = AgentFeatures()
        agent.numgroup = 6
        agent.number = self.agent_number
        agent.passwd = ''
        agent.context = self.agent_context
        agent.language = ''

        self.session.add(agent)
        self.session.commit()

        return agent

    def _insert_queue_member(self, queue_name, member_name, agent_id=1, penalty=0, skills='agent-1'):
        queue_member = QueueMember()
        queue_member.queue_name = queue_name
        queue_member.interface = member_name
        queue_member.penalty = penalty
        queue_member.usertype = 'agent'
        queue_member.userid = agent_id
        queue_member.channel = 'foobar'
        queue_member.category = 'queue'
        queue_member.position = 0
        queue_member.skills = skills

        try:
            self.session.add(queue_member)
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

        return queue_member
