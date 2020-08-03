# -*- coding: utf-8 -*-
# Copyright 2013-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, equal_to

from xivo_dao import agent_dao
from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.tests.test_dao import DAOTestCase

UNKNOWN_UUID = '57e8c8a2-bc75-4472-a529-8929da26dfb4'


class TestAgentDAO(DAOTestCase):

    agent_number = '1234'
    agent1_number = '1001'
    agent2_number = '1002'
    agent_context = 'test'

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

    def test_agent_with_id_multi_tenant(self):
        tenant = self.add_tenant()
        agent = self._insert_agent(tenant_uuid=tenant.uuid)
        self.assertRaises(LookupError, agent_dao.agent_with_id, agent.id, tenant_uuids=[self.default_tenant.uuid])

        result = agent_dao.agent_with_id(agent.id, tenant_uuids=[self.default_tenant.uuid, tenant.uuid])
        self.assertEqual(result.id, agent.id)

    def test_agent_with_number(self):
        agent = self._insert_agent()

        result = agent_dao.agent_with_number(agent.number)

        assert_that(result.id, equal_to(agent.id))
        assert_that(result.number, equal_to(agent.number))

    def test_agent_with_number_not_exist(self):
        self.assertRaises(LookupError, agent_dao.agent_with_number, '1234')

    def test_agent_with_number_multi_tenant(self):
        tenant = self.add_tenant()
        agent = self._insert_agent(tenant_uuid=tenant.uuid)
        self.assertRaises(LookupError, agent_dao.agent_with_number, agent.number, tenant_uuids=[self.default_tenant.uuid])

        result = agent_dao.agent_with_number(agent.number, tenant_uuids=[self.default_tenant.uuid, tenant.uuid])
        self.assertEqual(result.id, agent.id)
        self.assertEqual(result.number, equal_to(agent.number))

    def test_agent_with_user_uuid(self):
        agent = self._insert_agent()
        user = self.add_user(agentid=agent.id)

        result = agent_dao.agent_with_user_uuid(user.uuid)

        assert_that(result.id, equal_to(agent.id))

    def test_agent_with_user_uuid_unknown_user(self):
        agent = self._insert_agent()

        self.assertRaises(LookupError, agent_dao.agent_with_user_uuid, UNKNOWN_UUID)

    def test_agent_with_user_uuid_multi_tenant(self):
        tenant = self.add_tenant()
        agent = self._insert_agent(tenant_uuid=tenant.uuid)
        user = self.add_user(agentid=agent.id, tenant_uuid=tenant.uuid)

        self.assertRaises(LookupError, agent_dao.agent_with_user_uuid, user.uuid, tenant_uuids=[self.default_tenant.uuid])
        result = agent_dao.agent_with_user_uuid(user.uuid, tenant_uuids=[self.default_tenant.uuid, tenant.uuid])

        assert_that(result.id, equal_to(agent.id))

    def test_get(self):
        agent = self._insert_agent()

        result = agent_dao.get(agent.id)

        assert_that(result.id, equal_to(agent.id))
        assert_that(result.number, equal_to(agent.number))
        assert_that(result.passwd, equal_to(agent.passwd))
        assert_that(result.context, equal_to(agent.context))
        assert_that(result.language, equal_to(agent.language))

    def test_get_not_exist(self):
        result = agent_dao.get(1)

        assert_that(result, equal_to(None))

    def test_get_multi_tenant(self):
        tenant = self.add_tenant()
        agent1 = self._insert_agent(self.agent1_number, tenant_uuid=tenant.uuid)
        agent2 = self._insert_agent(self.agent2_number, tenant_uuid=self.default_tenant.uuid)

        result = agent_dao.get(agent1.id, tenant_uuids=[self.default_tenant.uuid])
        assert_that(result, equal_to(None))

        result = agent_dao.get(agent2.id, tenant_uuids=[self.default_tenant.uuid, tenant.uuid])
        assert_that(result, equal_to(agent2))

        result = agent_dao.get(agent1.id, tenant_uuids=[tenant.uuid])
        assert_that(result, equal_to(agent1))

    def test_all(self):
        agent1 = self._insert_agent(self.agent1_number)
        agent2 = self._insert_agent(self.agent2_number)

        expected = [agent1, agent2]

        result = agent_dao.all()

        assert_that(result, equal_to(expected))

    def test_all_empty(self):
        result = agent_dao.all()
        self.assertEqual([], result)

    def test_all_multi_tenant(self):
        tenant = self.add_tenant()
        agent1 = self._insert_agent(self.agent1_number, tenant_uuid=self.default_tenant.uuid)
        agent2 = self._insert_agent(self.agent2_number, tenant_uuid=tenant.uuid)

        expected_tenant1 = [agent1]
        result = agent_dao.all(tenant_uuids=[self.default_tenant.uuid])
        assert_that(result, equal_to(expected_tenant1))

        expected_tenant2 = [agent2]
        result = agent_dao.all(tenant_uuids=[tenant.uuid])
        assert_that(result, equal_to(expected_tenant2))

        expected_all = [agent1, agent2]
        result = agent_dao.all(tenant_uuids=[self.default_tenant.uuid, tenant.uuid])
        assert_that(result, equal_to(expected_all))

    def _insert_agent(self, number=agent_number, tenant_uuid=None):
        agent = AgentFeatures()
        agent.tenant_uuid = tenant_uuid or self.default_tenant.uuid
        agent.number = number
        agent.passwd = ''
        agent.context = self.agent_context
        agent.language = ''
        agent.description = ''

        self.add_me(agent)

        return agent

    def _insert_queue(self, queue_id, name, tenant_uuid=None):
        queue = QueueFeatures()
        queue.tenant_uuid = tenant_uuid or self.default_tenant.uuid
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
