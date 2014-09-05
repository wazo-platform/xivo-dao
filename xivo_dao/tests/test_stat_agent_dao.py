# -*- coding: utf-8 -*-

# Copyright (C) 2012-2014 Avencall
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

from xivo_dao import stat_agent_dao
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.alchemy.stat_agent import StatAgent


class TestStatAgentDAO(DAOTestCase):

    def test_id_from_name(self):
        agent = self._insert_agent('Agent/1234')

        result = stat_agent_dao.id_from_name(agent.name)

        self.assertEqual(result, agent.id)

    def test_clean_table(self):
        self._insert_agent('Agent/123')

        stat_agent_dao.clean_table(self.session)

        self.assertTrue(self.session.query(StatAgent).first() is None)

    def _insert_agent(self, name):
        agent = StatAgent()
        agent.name = name

        self.add_me(agent)

        return agent
