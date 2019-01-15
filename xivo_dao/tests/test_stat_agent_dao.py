# -*- coding: utf-8 -*-
# Copyright (C) 2012-2014 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

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
