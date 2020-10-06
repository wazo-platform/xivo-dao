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
                'number': 'number1',
                'tenant_uuid': 'tenant1',
            },
            {
                'number': 'number2',
                'tenant_uuid': 'tenant2',
            },
            {
                'number': 'number3',
                'tenant_uuid': 'tenant3',
            },
            {
                'number': 'number4',
                'tenant_uuid': 'tenant4',
            },
        ]
        self._insert_agent('Agent/number1', 'tenant1')
        self._insert_agent('Agent/number2', 'tenant2')

        with flush_session(self.session):
            stat_agent_dao.insert_missing_agents(self.session, confd_agents)

        result = [(name, tenant_uuid) for name, tenant_uuid in self.session.query(StatAgent.name, StatAgent.tenant_uuid).all()]

        self.assertTrue(('Agent/number1', 'tenant1') in result)
        self.assertTrue(('Agent/number2', 'tenant2') in result)
        self.assertTrue(('Agent/number3', 'tenant3') in result)
        self.assertTrue(('Agent/number4', 'tenant4') in result)
        self.assertEquals(len(result), 4)

    def _insert_agent(self, name, tenant_uuid=None):
        agent = StatAgent()
        agent.name = name
        agent.tenant_uuid = tenant_uuid or self.default_tenant.uuid

        self.add_me(agent)

        return agent
