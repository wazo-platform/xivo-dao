# Copyright 2012-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, contains_inanyorder

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
        # 1: in confd + in stat
        # 2: in confd + not in stat',
        # 3: not in confd + in stat',
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
        ]
        self._insert_agent('Agent/1', 'tenant1', 1)
        self._insert_agent('Agent/3', 'tenant3', 3)

        with flush_session(self.session):
            stat_agent_dao.insert_missing_agents(self.session, confd_agents)

        result = self._fetch_stat_agents()
        assert_that(result, contains_inanyorder(
            ('Agent/1', 'tenant1', 1, False),
            ('Agent/2', 'tenant2', 2, False),
            ('Agent/3', 'tenant3', 3, True),
        ))

    def test_when_agent_marked_as_deleted_then_new_one_is_created(self):
        confd_agents = [{'id': 1, 'number': '1', 'tenant_uuid': 'tenant'}]
        self._insert_agent('Agent/1', 'tenant', agent_id=999, deleted=True)

        with flush_session(self.session):
            stat_agent_dao.insert_missing_agents(self.session, confd_agents)

        result = self._fetch_stat_agents()
        assert_that(result, contains_inanyorder(
            ('Agent/1', 'tenant', 1, False),
            ('Agent/1_', 'tenant', 999, True),
        ))

    def test_mark_recreated_agents_with_same_number_as_deleted(self):
        confd_agents = {'Agent/1': {'id': 1, 'number': '1', 'tenant_uuid': 'tenant'}}
        self._insert_agent('Agent/1', 'tenant', agent_id=999, deleted=False)

        with flush_session(self.session):
            stat_agent_dao._mark_recreated_agents_with_same_number_as_deleted(self.session, confd_agents)

        result = self._fetch_stat_agents()
        assert_that(result, contains_inanyorder(
            ('Agent/1', 'tenant', 999, True)
        ))

    def test_mark_non_confd_agents_as_deleted(self):
        confd_agents = [{'id': 1, 'number': '1', 'tenant_uuid': 'tenant'}]
        self._insert_agent('Agent/2', 'tenant', agent_id=2, deleted=False)
        self._insert_agent('Agent/3', 'tenant', agent_id=None, deleted=False)

        with flush_session(self.session):
            stat_agent_dao._mark_non_confd_agents_as_deleted(self.session, confd_agents)

        result = self._fetch_stat_agents()
        assert_that(result, contains_inanyorder(
            ('Agent/2', 'tenant', 2, True),
            ('Agent/3', 'tenant', None, True),
        ))

    def test_create_missing_agents(self):
        confd_agents = {
            'Agent/1': {'id': 1, 'number': '1', 'tenant_uuid': 'tenant'},
        }
        self._insert_agent('Agent/2', 'tenant', deleted=True)

        with flush_session(self.session):
            stat_agent_dao._create_missing_agents(self.session, confd_agents)

        result = self._fetch_stat_agents()
        assert_that(result, contains_inanyorder(
            ('Agent/1', 'tenant', 1, False),
            ('Agent/2', 'tenant', None, True),
        ))

    def test_rename_deleted_agents_with_duplicate_name(self):
        confd_agents = {'Agent/1': {'id': 1, 'number': 'agent', 'tenant_uuid': 'tenant'}}
        self._insert_agent('Agent/1', 'tenant', agent_id=1, deleted=True)
        self._insert_agent('Agent/1', 'tenant', agent_id=1, deleted=True)

        with flush_session(self.session):
            stat_agent_dao._rename_deleted_agents_with_duplicate_name(
                self.session, confd_agents
            )

        result = self._fetch_stat_agents()
        assert_that(result, contains_inanyorder(
            ('Agent/1_', 'tenant', 1, True),
            ('Agent/1__', 'tenant', 1, True),
        ))

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
