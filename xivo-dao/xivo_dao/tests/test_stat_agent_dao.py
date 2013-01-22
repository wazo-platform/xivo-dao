# -*- coding: utf-8 -*-

# Copyright (C) 2012-2013 Avencall
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

from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.alchemy.stat_agent import StatAgent
from xivo_dao import stat_agent_dao


class TestStatAgentDAO(DAOTestCase):

    tables = [StatAgent]

    def setUp(self):
        self.empty_tables()

    def test_insert_if_missing(self):
        old_agents = ['Agent/%s' % (number + 1000) for number in range(5)]
        for agent_name in old_agents:
            agent = StatAgent()
            agent.name = agent_name
            self.session.add(agent)
        self.session.commit()

        new_agents = ['Agent/%s' % (number + 1000) for number in range(5, 10)]

        all_agents = sorted(old_agents + new_agents)

        stat_agent_dao.insert_if_missing(all_agents)

        result = sorted([r.name for r in self.session.query(StatAgent.name)])

        self.assertEqual(result, all_agents)

    def test_id_from_name(self):
        agent = StatAgent()
        agent.name = 'Agent/1234'

        self.session.add(agent)
        self.session.commit()

        result = stat_agent_dao.id_from_name(agent.name)

        self.assertEqual(result, agent.id)
