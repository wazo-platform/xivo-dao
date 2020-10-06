# -*- coding: utf-8 -*-
# Copyright 2012-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao import stat_agent_dao
from xivo_dao.alchemy.stat_agent import StatAgent
from xivo_dao.helpers.db_utils import flush_session
from xivo_dao.tests.test_dao import DAOTestCase


class TestStatAgentDAO(DAOTestCase):

    def test_clean_table(self):
        self._insert_agent('Agent/123')

        stat_agent_dao.clean_table(self.session)

        self.assertTrue(self.session.query(StatAgent).first() is None)

    def test_insert_missing_agents(self):
        confd_agents = [
            {
                'id': 1,
                'number': 'number1',
                'tenant_uuid': 'tenant1',
            },
            {
                'id': 2,
                'number': 'number2',
                'tenant_uuid': 'tenant2',
            },
            {
                'id': 3,
                'number': 'number3',
                'tenant_uuid': 'tenant3',
            },
            {
                'id': 4,
                'number': 'number4',
                'tenant_uuid': 'tenant4',
            },
        ]
        self._insert_agent('Agent/number1', 'tenant1', 1)
        self._insert_agent('Agent/number2', 'tenant2', 2)

        with flush_session(self.session):
            stat_agent_dao.insert_missing_agents(self.session, confd_agents)

        result = [
            (name, tenant_uuid, agent_id)
            for name, tenant_uuid, agent_id
            in self.session.query(
                StatAgent.name, StatAgent.tenant_uuid, StatAgent.agent_id
            ).all()
        ]

        self.assertTrue(('Agent/number1', 'tenant1', 1) in result)
        self.assertTrue(('Agent/number2', 'tenant2', 2) in result)
        self.assertTrue(('Agent/number3', 'tenant3', 3) in result)
        self.assertTrue(('Agent/number4', 'tenant4', 4) in result)
        self.assertEquals(len(result), 4)

    def _insert_agent(self, name, tenant_uuid=None, agent_id=None):
        agent = StatAgent()
        agent.name = name
        agent.tenant_uuid = tenant_uuid or self.default_tenant.uuid
        agent.agent_id = agent_id

        self.add_me(agent)

        return agent
