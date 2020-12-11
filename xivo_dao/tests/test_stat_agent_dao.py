# -*- coding: utf-8 -*-
# Copyright 2012-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import uuid

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
        # 1: in confd + in cel + in stat
        # 2: in confd + not in cel + in stat
        # 3: in confd + not in cel + not in stat',
        # 4: in confd + in cel + not in stat',
        # 5: not in confd + in cel + not in stat',
        # 6: not in confd + in cel + in stat',
        # 7: not in confd + not in cel + in stat',
        confd_agents = [
            {
                'id': 1,
                'number': '1',
                'tenant_uuid': 'tenant1',
            },
            {
                'id': 2,
                'number': '2',
                'tenant_uuid': 'tenant2',
            },
            {
                'id': 3,
                'number': '3',
                'tenant_uuid': 'tenant3',
            },
            {
                'id': 4,
                'number': '4',
                'tenant_uuid': 'tenant4',
            },
        ]
        self._insert_agent('Agent/1', 'tenant1', 1)
        self._insert_agent('Agent/2', 'tenant2', 2)
        self._insert_agent('Agent/6', 'tenant6', 6)
        self._insert_agent('Agent/7', 'tenant7', 7)

        new_agents = ['Agent/1', 'Agent/4', 'Agent/5']
        master_tenant = str(uuid.uuid4())

        with flush_session(self.session):
            stat_agent_dao.insert_missing_agents(self.session, new_agents, confd_agents, master_tenant)

        result = self._fetch_stat_agents()
        self.assertTrue(('Agent/1', 'tenant1', 1, False) in result)
        self.assertTrue(('Agent/2', 'tenant2', 2, False) in result)
        self.assertTrue(('Agent/3', 'tenant3', 3, False) in result)
        self.assertTrue(('Agent/4', 'tenant4', 4, False) in result)
        self.assertTrue(('Agent/5', master_tenant, None, True) in result)
        self.assertTrue(('Agent/6', 'tenant6', 6, True) in result)
        self.assertTrue(('Agent/7', 'tenant7', 7, True) in result)
        self.assertEquals(len(result), 7)

    def test_when_agent_marked_as_deleted_then_new_one_is_created(self):
        confd_agents = [{'id': 1, 'number': '1', 'tenant_uuid': 'tenant'}]
        self._insert_agent('Agent/1', 'tenant', agent_id=999, deleted=True)
        new_agents = ['Agent/1']
        master_tenant = str(uuid.uuid4())

        with flush_session(self.session):
            stat_agent_dao.insert_missing_agents(self.session, new_agents, confd_agents, master_tenant)

        result = self._fetch_stat_agents()
        self.assertTrue(('Agent/1', 'tenant', 1, False) in result)
        self.assertTrue(('Agent/1_', 'tenant', 999, True) in result)
        self.assertEquals(len(result), 2)

    def test_mark_recreated_agents_with_same_number_as_deleted(self):
        confd_agents = {'Agent/1': {'id': 1, 'number': '1', 'tenant_uuid': 'tenant'}}
        self._insert_agent('Agent/1', 'tenant', agent_id=999, deleted=False)

        with flush_session(self.session):
            stat_agent_dao._mark_recreated_agents_with_same_number_as_deleted(self.session, confd_agents)

        result = self._fetch_stat_agents()
        self.assertTrue(('Agent/1', 'tenant', 999, True) in result)
        self.assertEquals(len(result), 1)

    def test_mark_non_confd_agents_as_deleted(self):
        confd_agents = [{'id': 1, 'number': '1', 'tenant_uuid': 'tenant'}]
        self._insert_agent('Agent/2', 'tenant', agent_id=2, deleted=False)
        self._insert_agent('Agent/3', 'tenant', agent_id=None, deleted=False)

        with flush_session(self.session):
            stat_agent_dao._mark_non_confd_agents_as_deleted(self.session, confd_agents)

        result = self._fetch_stat_agents()
        self.assertTrue(('Agent/2', 'tenant', 2, True) in result)
        self.assertTrue(('Agent/3', 'tenant', None, True) in result)
        self.assertEquals(len(result), 2)

    def test_create_missing_agents(self):
        confd_agents = {
            'Agent/1': {'id': 1, 'number': '1', 'tenant_uuid': 'tenant'},
        }
        new_agents = ['Agent/2', 'Agent/3']
        master_tenant = str(uuid.uuid4())
        self._insert_agent('Agent/3', 'tenant', deleted=True)

        with flush_session(self.session):
            stat_agent_dao._create_missing_agents(
                self.session, new_agents, confd_agents, master_tenant
            )

        result = self._fetch_stat_agents()
        self.assertTrue(('Agent/1', 'tenant', 1, False) in result)
        self.assertTrue(('Agent/2', master_tenant, None, True) in result)
        self.assertTrue(('Agent/3', 'tenant', None, True) in result)
        self.assertEquals(len(result), 3)

    def test_rename_deleted_agents_with_duplicate_name(self):
        confd_agents = {'Agent/1': {'id': 1, 'number': 'agent', 'tenant_uuid': 'tenant'}}
        self._insert_agent('Agent/1', 'tenant', agent_id=1, deleted=True)
        self._insert_agent('Agent/1', 'tenant', agent_id=1, deleted=True)

        with flush_session(self.session):
            stat_agent_dao._rename_deleted_agents_with_duplicate_name(
                self.session, confd_agents
            )

        result = self._fetch_stat_agents()
        self.assertTrue(('Agent/1_', 'tenant', 1, True) in result)
        self.assertTrue(('Agent/1__', 'tenant', 1, True) in result)
        self.assertEquals(len(result), 2)

    def _fetch_stat_agents(self):
        return [
            (name, tenant_uuid, agent_id, deleted)
            for name, tenant_uuid, agent_id, deleted
            in self.session.query(
                StatAgent.name, StatAgent.tenant_uuid, StatAgent.agent_id, StatAgent.deleted
            ).all()
        ]

    def _insert_agent(self, name, tenant_uuid=None, agent_id=None, deleted=False):
        agent = StatAgent()
        agent.name = name
        agent.tenant_uuid = tenant_uuid or self.default_tenant.uuid
        agent.agent_id = agent_id
        agent.deleted = deleted

        self.add_me(agent)

        return agent
