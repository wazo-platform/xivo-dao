# Copyright 2013-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, contains_exactly, empty, equal_to, has_properties

from xivo_dao import agent_dao
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.tests.test_dao import UNKNOWN_UUID, DAOTestCase


class TestAgentDAO(DAOTestCase):
    agent_number = '1234'
    agent1_number = '1001'
    agent2_number = '1002'
    agent_context = 'test'

    def test_agent_with_id(self):
        agent = self.add_agent()
        user = self.add_user(agentid=agent.id)
        queue_member = self._insert_queue_member('foobar', 'Agent/2', agent.id)
        queue = self.add_queuefeatures(id=64, name=queue_member.queue_name)

        result = agent_dao.agent_with_id(agent.id)

        assert_that(
            result,
            has_properties(
                id=agent.id,
                number=agent.number,
                queues=contains_exactly(
                    has_properties(
                        id=queue.id,
                        name=queue_member.queue_name,
                        penalty=queue_member.penalty,
                    )
                ),
                user_ids=contains_exactly(user.id),
            ),
        )

    def test_agent_with_id_no_user(self):
        agent = self.add_agent()
        queue_member = self._insert_queue_member('foobar', 'Agent/2', agent.id)
        queue = self.add_queuefeatures(id=64, name=queue_member.queue_name)

        result = agent_dao.agent_with_id(agent.id)

        assert_that(
            result,
            has_properties(
                id=agent.id,
                number=agent.number,
                queues=contains_exactly(
                    has_properties(
                        id=queue.id,
                        name=queue_member.queue_name,
                        penalty=queue_member.penalty,
                    )
                ),
                user_ids=empty(),
            ),
        )

    def test_agent_with_id_not_exist(self):
        self.assertRaises(LookupError, agent_dao.agent_with_id, 1)

    def test_agent_with_id_multi_tenant(self):
        tenant = self.add_tenant()
        agent = self.add_agent(tenant_uuid=tenant.uuid)
        self.assertRaises(
            LookupError,
            agent_dao.agent_with_id,
            agent.id,
            tenant_uuids=[self.default_tenant.uuid],
        )

        result = agent_dao.agent_with_id(
            agent.id, tenant_uuids=[self.default_tenant.uuid, tenant.uuid]
        )
        assert result.id == agent.id

    def test_agent_with_number(self):
        agent = self.add_agent()
        user = self.add_user(agentid=agent.id)

        result = agent_dao.agent_with_number(agent.number)

        assert_that(
            result,
            has_properties(
                id=agent.id,
                number=agent.number,
                user_ids=contains_exactly(user.id),
            ),
        )

    def test_agent_with_number_no_user(self):
        agent = self.add_agent()

        result = agent_dao.agent_with_number(agent.number)

        assert_that(
            result,
            has_properties(
                id=agent.id,
                number=agent.number,
                user_ids=empty(),
            ),
        )

    def test_agent_with_number_not_exist(self):
        self.assertRaises(LookupError, agent_dao.agent_with_number, '1234')

    def test_agent_with_number_multi_tenant(self):
        tenant = self.add_tenant()
        agent = self.add_agent(tenant_uuid=tenant.uuid)
        self.assertRaises(
            LookupError,
            agent_dao.agent_with_number,
            agent.number,
            tenant_uuids=[self.default_tenant.uuid],
        )

        result = agent_dao.agent_with_number(
            agent.number, tenant_uuids=[self.default_tenant.uuid, tenant.uuid]
        )

        assert_that(result, has_properties(id=agent.id, number=agent.number))

    def test_agent_with_user_uuid(self):
        agent = self.add_agent()
        user = self.add_user(agentid=agent.id)

        result = agent_dao.agent_with_user_uuid(user.uuid)

        assert_that(
            result, has_properties(id=agent.id, user_ids=contains_exactly(user.id))
        )

    def test_agent_with_user_uuid_unknown_user(self):
        self.add_agent()

        self.assertRaises(LookupError, agent_dao.agent_with_user_uuid, UNKNOWN_UUID)

    def test_agent_with_user_uuid_multi_tenant(self):
        tenant = self.add_tenant()
        agent = self.add_agent(tenant_uuid=tenant.uuid)
        user = self.add_user(agentid=agent.id, tenant_uuid=tenant.uuid)

        self.assertRaises(
            LookupError,
            agent_dao.agent_with_user_uuid,
            user.uuid,
            tenant_uuids=[self.default_tenant.uuid],
        )
        result = agent_dao.agent_with_user_uuid(
            user.uuid, tenant_uuids=[self.default_tenant.uuid, tenant.uuid]
        )

        assert_that(result.id, equal_to(agent.id))

    def test_get(self):
        agent = self.add_agent()

        result = agent_dao.get(agent.id)

        assert_that(
            result,
            has_properties(
                id=agent.id,
                number=agent.number,
                passwd=agent.passwd,
                context=agent.context,
                language=agent.language,
            ),
        )

    def test_get_not_exist(self):
        result = agent_dao.get(1)

        assert_that(result, equal_to(None))

    def test_get_multi_tenant(self):
        tenant = self.add_tenant()
        agent1 = self.add_agent(number=self.agent1_number, tenant_uuid=tenant.uuid)
        agent2 = self.add_agent(
            number=self.agent2_number, tenant_uuid=self.default_tenant.uuid
        )

        result = agent_dao.get(agent1.id, tenant_uuids=[self.default_tenant.uuid])
        assert_that(result, equal_to(None))

        result = agent_dao.get(
            agent2.id, tenant_uuids=[self.default_tenant.uuid, tenant.uuid]
        )
        assert_that(result, equal_to(agent2))

        result = agent_dao.get(agent1.id, tenant_uuids=[tenant.uuid])
        assert_that(result, equal_to(agent1))

    def test_all(self):
        agent1 = self.add_agent(number=self.agent1_number)
        agent2 = self.add_agent(number=self.agent2_number)

        expected = [agent1, agent2]

        result = agent_dao.all()

        assert_that(result, equal_to(expected))

    def test_all_empty(self):
        result = agent_dao.all()
        assert_that(result, empty())

    def test_all_multi_tenant(self):
        tenant = self.add_tenant()
        agent1 = self.add_agent(
            number=self.agent1_number, tenant_uuid=self.default_tenant.uuid
        )
        agent2 = self.add_agent(number=self.agent2_number, tenant_uuid=tenant.uuid)

        expected_tenant1 = [agent1]
        result = agent_dao.all(tenant_uuids=[self.default_tenant.uuid])
        assert_that(result, equal_to(expected_tenant1))

        expected_tenant2 = [agent2]
        result = agent_dao.all(tenant_uuids=[tenant.uuid])
        assert_that(result, equal_to(expected_tenant2))

        expected_all = [agent1, agent2]
        result = agent_dao.all(tenant_uuids=[self.default_tenant.uuid, tenant.uuid])
        assert_that(result, equal_to(expected_all))

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
