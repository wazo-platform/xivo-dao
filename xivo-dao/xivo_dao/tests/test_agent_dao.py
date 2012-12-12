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

from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_dao import agent_dao
from xivo_dao.tests.test_dao import DAOTestCase


class TestAgentFeaturesDAO(DAOTestCase):

    agent_number = '1234'
    agent_context = 'test'

    tables = [AgentFeatures]

    def setUp(self):
        self.empty_tables()

    def test_agent_number(self):
        agent_id = self._insert_agent()

        number = agent_dao.agent_number(agent_id)

        self.assertEqual(number, self.agent_number)

    def test_agent_context(self):
        agent_id = self._insert_agent()

        context = agent_dao.agent_context(agent_id)

        self.assertEqual(context, self.agent_context)

    def test_agent_number_unknown(self):
        self.assertRaises(LookupError, lambda: agent_dao.agent_number(-1))

    def test_agent_interface(self):
        agent_id = self._insert_agent()

        interface = agent_dao.agent_interface(agent_id)

        self.assertEqual(interface, 'Agent/%s' % self.agent_number)

    def test_agent_id(self):
        expected_agent_id = self._insert_agent()

        agent_id = agent_dao.agent_id(self.agent_number)

        self.assertEqual(str(expected_agent_id), agent_id)

    def test_agent_id_inexistant(self):
        self.assertRaises(LookupError, agent_dao.agent_id, '2345')

    def _insert_agent(self):
        agent = AgentFeatures()
        agent.numgroup = 6
        agent.number = self.agent_number
        agent.passwd = ''
        agent.context = self.agent_context
        agent.language = ''

        self.session.add(agent)
        self.session.commit()

        return agent.id
