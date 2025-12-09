# Copyright 2013-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, contains_exactly, empty, has_properties, none
from sqlalchemy import and_

from xivo_dao import agent_status_dao
from xivo_dao.alchemy.agent_login_status import AgentLoginStatus
from xivo_dao.alchemy.agent_membership_status import AgentMembershipStatus
from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.tests.test_dao import UNKNOWN_UUID, DAOTestCase


class TestAgentStatusDao(DAOTestCase):
    def test_log_in_agent(self):
        agent_id = 1
        agent_number = '2'
        extension = '1001'
        context = 'default'
        interface = 'sip/abcdef'
        paused = False
        paused_reason = None
        state_interface = interface

        agent = self.add_agent(id=agent_id, number=agent_number)
        user = self.add_user(agentid=agent.id)

        agent_status_dao.log_in_agent(
            agent_id, agent_number, extension, context, interface, state_interface
        )

        agent_status = agent_status_dao.get_status(agent_id)

        assert_that(
            agent_status,
            has_properties(
                agent_id=agent_id,
                agent_number=agent_number,
                extension=extension,
                context=context,
                interface=interface,
                paused=paused,
                paused_reason=paused_reason,
                state_interface=state_interface,
                user_ids=contains_exactly(user.id),
            ),
        )

    def test_log_in_agent_no_user(self):
        agent_number = '2'
        extension = '1001'
        context = 'default'
        interface = 'sip/abcdef'
        paused = False
        paused_reason = None
        state_interface = interface

        agent = self.add_agent(number=agent_number)

        agent_status_dao.log_in_agent(
            agent.id, agent.number, extension, context, interface, state_interface
        )

        agent_status = agent_status_dao.get_status(agent.id)

        assert_that(
            agent_status,
            has_properties(
                agent_id=agent.id,
                agent_number=agent.number,
                extension=extension,
                context=context,
                interface=interface,
                paused=paused,
                paused_reason=paused_reason,
                state_interface=state_interface,
                user_ids=empty(),
            ),
        )

    def test_log_off_agent(self):
        agent_id = 1
        agent_number = '42'
        self._insert_agent_login_status(agent_id, agent_number)

        agent_status_dao.log_off_agent(agent_id)

        agent_status = self.session.get(AgentLoginStatus, agent_id)
        assert_that(agent_status, none())

    def test_get_extension_from_agent_id(self):
        agent_id = 13
        agent_interface = 'sip/asdf'
        agent_number = 42
        extension = '1000'
        context = 'default'

        agent = self.add_agent(id=agent_id, number=agent_number)
        self._insert_agent_login_status(
            agent.id,
            agent.number,
            extension,
            context,
            interface=agent_interface,
            state_interface=agent_interface,
        )

        result_extension, result_context = agent_status_dao.get_extension_from_agent_id(
            agent_id
        )

        assert extension == result_extension
        assert context == result_context

    def test_get_extension_from_agent_id_not_found(self):
        agent_id = 13

        self.assertRaises(
            LookupError, agent_status_dao.get_extension_from_agent_id, agent_id
        )

    def test_get_agent_id_from_extension_not_found(self):
        extension = '100'
        context = 'default'

        self.assertRaises(
            LookupError,
            agent_status_dao.get_agent_id_from_extension,
            extension,
            context,
        )

    def test_get_agent_id_from_extension(self):
        agent_id = 13
        agent_interface = 'sip/asdf'
        agent_number = 42
        extension = '1000'
        context = 'default'
        agent = self.add_agent(id=agent_id, number=agent_number)
        self._insert_agent_login_status(
            agent.id,
            agent.number,
            extension,
            context,
            interface=agent_interface,
            state_interface=agent_interface,
        )

        result = agent_status_dao.get_agent_id_from_extension(extension, context)

        assert result == agent_id

    def test_get_status_with_unlogged_agent_returns_none(self):
        agent_id = 1
        agent_status = agent_status_dao.get_status(agent_id)
        assert agent_status is None

    def test_get_status_with_logged_agent_returns_an_agent(self):
        agent = self.add_agent()
        queue = self.add_queuefeatures(name='queue1')
        agent_login_status = self._insert_agent_login_status(agent.id, agent.number)
        agent_membership = self._insert_agent_membership(
            agent.id, queue.id, queue.name, 64
        )

        result = agent_status_dao.get_status(agent.id)

        assert_that(
            result,
            has_properties(
                agent_id=agent.id,
                agent_number=agent.number,
                extension=agent_login_status.extension,
                interface=agent_login_status.interface,
                state_interface=agent_login_status.state_interface,
                queues=contains_exactly(
                    has_properties(
                        id=agent_membership.queue_id,
                        name=agent_membership.queue_name,
                        penalty=agent_membership.penalty,
                    )
                ),
            ),
        )

    def test_get_status_with_logged_agent_returns_an_agent_multi_tenant(self):
        tenant = self.add_tenant()
        agent = self.add_agent(tenant_uuid=tenant.uuid)
        self._insert_agent_login_status(agent.id, agent.number)
        queue = self.add_queuefeatures(name='queue1', tenant_uuid=tenant.uuid)
        agent_membership = self._insert_agent_membership(agent.id, 1, queue.name, 64)

        result = agent_status_dao.get_status(agent.id, tenant_uuids=[tenant.uuid])
        assert_that(
            result,
            has_properties(
                agent_id=agent.id,
                queues=contains_exactly(has_properties(id=agent_membership.queue_id)),
            ),
        )

        result = agent_status_dao.get_status(
            agent.id, tenant_uuids=[self.default_tenant.uuid]
        )
        assert_that(result, none())

    def test_get_status_by_number_with_unlogged_agent_returns_none(self):
        agent_number = '1001'
        agent_status = agent_status_dao.get_status_by_number(agent_number)
        assert_that(agent_status, none())

    def test_get_status_by_number_with_logged_agent(self):
        agent = self.add_agent()
        user = self.add_user(agentid=agent.id)
        queue = self.add_queuefeatures(name='queue1')
        agent_login_status = self._insert_agent_login_status(agent.id, agent.number)
        agent_membership = self._insert_agent_membership(agent.id, queue.id, queue.name)

        result = agent_status_dao.get_status_by_number(agent.number)

        assert_that(
            result,
            has_properties(
                agent_id=agent.id,
                agent_number=agent.number,
                extension=agent_login_status.extension,
                context=agent_login_status.context,
                interface=agent_login_status.interface,
                state_interface=agent_login_status.state_interface,
                queues=contains_exactly(
                    has_properties(
                        id=agent_membership.queue_id, name=agent_membership.queue_name
                    )
                ),
                user_ids=contains_exactly(user.id),
            ),
        )

    def test_get_status_by_number_with_logged_agent_no_user(self):
        agent = self.add_agent()
        agent_login_status = self._insert_agent_login_status(agent.id, agent.number)
        queue = self.add_queuefeatures(name='queue1')
        agent_membership = self._insert_agent_membership(agent.id, queue.id, queue.name)

        result = agent_status_dao.get_status_by_number(agent.number)

        assert_that(
            result,
            has_properties(
                agent_id=agent.id,
                agent_number=agent.number,
                extension=agent_login_status.extension,
                context=agent_login_status.context,
                interface=agent_login_status.interface,
                state_interface=agent_login_status.state_interface,
                queues=contains_exactly(
                    has_properties(
                        id=agent_membership.queue_id, name=agent_membership.queue_name
                    )
                ),
                user_ids=empty(),
            ),
        )

    def test_get_status_by_number_with_logged_agent_multi_tenant(self):
        tenant = self.add_tenant()
        agent = self.add_agent(tenant_uuid=tenant.uuid)
        self._insert_agent_login_status(agent.id, agent.number)
        agent_membership = self._insert_agent_membership(agent.id, 1, 'queue1', 64)

        result = agent_status_dao.get_status_by_number(
            agent.number, tenant_uuids=[tenant.uuid]
        )

        assert_that(
            result,
            has_properties(
                agent_id=agent.id,
                queues=contains_exactly(has_properties(id=agent_membership.queue_id)),
            ),
        )

        result = agent_status_dao.get_status_by_number(
            agent.number,
            tenant_uuids=[self.default_tenant.uuid],
        )
        assert_that(result, none())

    def test_get_status_by_user_without_user(self):
        result = agent_status_dao.get_status_by_user(UNKNOWN_UUID)
        assert_that(result, none())

    def test_get_status_by_user_without_agent(self):
        user = self.add_user()

        result = agent_status_dao.get_status_by_user(user.uuid)

        assert_that(result, none())

    def test_get_status_by_user_with_unlogged_agent_returns_none(self):
        agent = self.add_agent()
        user = self.add_user(agentid=agent.id)

        result = agent_status_dao.get_status_by_user(user.uuid)

        assert_that(result, none())

    def test_get_status_by_user_with_logged_agent(self):
        agent = self.add_agent()
        user = self.add_user(agentid=agent.id)
        agent_login_status = self._insert_agent_login_status(agent.id, agent.number)
        queue = self.add_queuefeatures(name='queue1')
        agent_membership = self._insert_agent_membership(agent.id, queue.id, queue.name)

        result = agent_status_dao.get_status_by_user(user.uuid)

        assert_that(
            result,
            has_properties(
                agent_id=agent.id,
                agent_number=agent.number,
                extension=agent_login_status.extension,
                context=agent_login_status.context,
                interface=agent_login_status.interface,
                state_interface=agent_login_status.state_interface,
                queues=contains_exactly(
                    has_properties(
                        id=agent_membership.queue_id, name=agent_membership.queue_name
                    )
                ),
                user_ids=contains_exactly(user.id),
            ),
        )

    def test_get_status_by_user_with_logged_agent_multi_tenant(self):
        tenant = self.add_tenant()
        agent = self.add_agent(tenant_uuid=tenant.uuid)
        user = self.add_user(agentid=agent.id, tenant_uuid=tenant.uuid)
        self._insert_agent_login_status(agent.id, agent.number)
        agent_membership = self._insert_agent_membership(agent.id, 1, 'queue1', 64)

        result = agent_status_dao.get_status_by_user(
            user.uuid, tenant_uuids=[tenant.uuid]
        )

        assert_that(
            result,
            has_properties(
                agent_id=agent.id,
                queues=contains_exactly(has_properties(id=agent_membership.queue_id)),
            ),
        )

        result = agent_status_dao.get_status_by_user(
            user.uuid,
            tenant_uuids=[self.default_tenant.uuid],
        )

        assert_that(result, none())

        # empty tenant list = no warnings
        result = agent_status_dao.get_status_by_user(user.uuid, tenant_uuids=[])

        assert_that(result, none())

    def test_get_statuses_of_unlogged_agent(self):
        agent = self.add_agent()

        statuses = agent_status_dao.get_statuses()

        assert len(statuses) == 1
        assert statuses[0].agent_id == agent.id
        assert statuses[0].tenant_uuid == agent.tenant_uuid
        assert statuses[0].agent_number == agent.number
        assert statuses[0].logged is False
        assert statuses[0].extension is None
        assert statuses[0].context is None
        assert statuses[0].state_interface is None
        assert len(statuses[0].queues) == 0

    def test_get_statuses_of_logged_agent(self):
        agent = self.add_agent()
        agent_login_status = self._insert_agent_login_status(agent.id, agent.number)

        statuses = agent_status_dao.get_statuses()

        assert len(statuses) == 1
        assert statuses[0].agent_id == agent.id
        assert statuses[0].tenant_uuid == agent.tenant_uuid
        assert statuses[0].agent_number == agent.number
        assert statuses[0].logged is True
        assert statuses[0].extension == agent_login_status.extension
        assert statuses[0].context == agent_login_status.context
        assert statuses[0].state_interface == agent_login_status.state_interface
        assert len(statuses[0].queues) == 0

    def test_get_statuses_of_logged_agent_multi_tenant(self):
        tenant = self.add_tenant()
        agent = self.add_agent(tenant_uuid=tenant.uuid)
        self._insert_agent_login_status(agent.id, agent.number)

        statuses = agent_status_dao.get_statuses(tenant_uuids=[tenant.uuid])

        assert len(statuses) == 1
        assert statuses[0].agent_id == agent.id
        assert statuses[0].tenant_uuid == tenant.uuid

        statuses = agent_status_dao.get_statuses(
            tenant_uuids=[self.default_tenant.uuid]
        )

        assert len(statuses) == 0

    def test_get_statuses_of_logged_for_queue(self):
        agent = self.add_agent()
        queue = self.add_queuefeatures(name='queue1', number='3000')
        self._insert_agent_membership(agent.id, queue.id, queue.name)
        agent_login_status = self._insert_agent_login_status(agent.id, agent.number)

        statuses = agent_status_dao.get_statuses_for_queue(queue.id)

        assert_that(
            statuses,
            contains_exactly(
                has_properties(
                    agent_id=agent.id,
                    agent_number=agent.number,
                    extension=agent_login_status.extension,
                    context=agent_login_status.context,
                    interface=agent_login_status.interface,
                    state_interface=agent_login_status.state_interface,
                )
            ),
        )

    def test_get_statuses_to_add_to_queue(self):
        agent1 = self.add_agent()
        agent2 = self.add_agent()
        queue1 = self._insert_queue(1, 'queue1', '3000')
        queue2 = self._insert_queue(2, 'queue2', '3001')
        self._insert_agent_login_status(agent1.id, agent1.number)
        self._insert_agent_login_status(agent2.id, agent2.number)
        self._insert_agent_queue_member(agent1.id, queue1.name)
        self._insert_agent_queue_member(agent1.id, queue2.name)
        self._insert_agent_queue_member(agent2.id, queue1.name)
        self._insert_agent_membership(agent1.id, queue2.id, queue2.name)
        self._insert_agent_membership(agent2.id, queue1.id, queue1.name)

        statuses = agent_status_dao.get_statuses_to_add_to_queue(queue1.id)

        assert_that(
            statuses,
            contains_exactly(
                has_properties(agent_id=agent1.id, agent_number=agent1.number)
            ),
        )

    def test_get_statuses_to_remove_from_queue(self):
        agent1 = self.add_agent()
        agent2 = self.add_agent()
        queue1 = self._insert_queue(1, 'queue1', '3000')
        queue2 = self._insert_queue(2, 'queue2', '3001')
        self._insert_agent_login_status(agent1.id, agent1.number)
        self._insert_agent_login_status(agent2.id, agent2.number)
        self._insert_agent_queue_member(agent1.id, queue2.name)
        self._insert_agent_queue_member(agent2.id, queue1.name)
        self._insert_agent_membership(agent1.id, queue1.id, queue1.name)
        self._insert_agent_membership(agent1.id, queue2.id, queue2.name)
        self._insert_agent_membership(agent2.id, queue1.id, queue1.name)

        statuses = agent_status_dao.get_statuses_to_remove_from_queue(queue1.id)

        assert_that(
            statuses,
            contains_exactly(
                has_properties(agent_id=agent1.id, agent_number=agent1.number)
            ),
        )

    def test_get_logged_agent_ids(self):
        agent_id = 1
        agent_number = '42'
        self._insert_agent_login_status(agent_id, agent_number)

        agent_ids = agent_status_dao.get_logged_agent_ids()

        assert_that(agent_ids, contains_exactly(agent_id))

    def test_get_logged_agent_ids_multi_tenant(self):
        tenant = self.add_tenant()
        agent = self.add_agent(id=1, number='42', tenant_uuid=tenant.uuid)
        self._insert_agent_login_status(agent.id, agent.number)

        agent_ids = agent_status_dao.get_logged_agent_ids(tenant_uuids=[tenant.uuid])
        assert_that(agent_ids, contains_exactly(agent.id))

        agent_ids = agent_status_dao.get_logged_agent_ids(
            tenant_uuids=[self.default_tenant.uuid, tenant.uuid],
        )
        assert_that(agent_ids, contains_exactly(agent.id))

        agent_ids = agent_status_dao.get_logged_agent_ids(
            tenant_uuids=[self.default_tenant.uuid]
        )
        assert_that(agent_ids, empty())

    def test_is_extension_in_use_with_an_agent(self):
        agent_id = 1
        agent_number = '42'
        extension = '1001'
        context = 'default'
        self._insert_agent_login_status(agent_id, agent_number, extension, context)

        in_use = agent_status_dao.is_extension_in_use(extension, context)

        self.assertTrue(in_use)

    def test_is_extension_in_use_with_no_agent(self):
        extension = '1001'
        context = 'default'

        in_use = agent_status_dao.is_extension_in_use(extension, context)

        self.assertFalse(in_use)

    def test_add_agent_to_queues(self):
        agent = self.add_agent()
        queue1 = agent_status_dao._Queue(
            id=1,
            name='queue1',
            display_name='First Queue',
            penalty=3,
            logged=False,
            paused=False,
            paused_reason=None,
            login_at=None,
        )
        queue2 = agent_status_dao._Queue(
            id=2,
            name='queue2',
            display_name='Second Queue',
            penalty=4,
            logged=False,
            paused=False,
            paused_reason=None,
            login_at=None,
        )

        queues = [queue1, queue2]

        agent_status_dao.add_agent_to_queues(agent.id, queues)

        memberships = self.session.query(AgentMembershipStatus).all()
        assert_that(
            memberships,
            contains_exactly(
                has_properties(
                    queue_id=queue1.id, queue_name=queue1.name, penalty=queue1.penalty
                ),
                has_properties(
                    queue_id=queue2.id, queue_name=queue2.name, penalty=queue2.penalty
                ),
            ),
        )

    def test_add_agent_to_queue_two_agents(self):
        agent1 = self.add_agent()
        self._insert_agent_login_status(agent1.id, agent1.number)
        agent2 = self.add_agent()
        self._insert_agent_login_status(
            agent2.id,
            agent2.number,
            '1002',
            'default',
            interface='Local/2@foo',
            state_interface='SIP/defabc',
        )
        queue_1 = self.add_queuefeatures(name='queue1')
        queue_2 = self.add_queuefeatures(name='queue2')

        queues = [
            agent_status_dao._Queue(
                id=queue_1.id,
                name='queue1',
                display_name='Queue One',
                penalty=0,
                logged=False,
                paused=False,
                paused_reason=None,
                login_at=None,
            ),
            agent_status_dao._Queue(
                id=queue_2.id,
                name='queue2',
                display_name='Queue Two',
                penalty=0,
                logged=False,
                paused=False,
                paused_reason=None,
                login_at=None,
            ),
        ]

        agent_status_dao.add_agent_to_queues(agent1.id, queues)
        agent_status_dao.add_agent_to_queues(agent2.id, queues)

        agent1_status = agent_status_dao.get_status(agent1.id)
        agent2_status = agent_status_dao.get_status(agent2.id)

        assert len(agent1_status.queues) == 2
        assert agent1_status.queues[0].id == queue_1.id
        assert agent1_status.queues[0].name == queue_1.name
        assert agent1_status.queues[1].id == queue_2.id
        assert agent1_status.queues[1].name == queue_2.name

        assert len(agent2_status.queues) == 2
        assert agent2_status.queues[0].id == queue_1.id
        assert agent2_status.queues[0].name == queue_1.name
        assert agent2_status.queues[1].id == queue_2.id
        assert agent2_status.queues[1].name == queue_2.name

    def test_remove_agent_from_queues_one_queue(self):
        agent = self.add_agent()
        self._insert_agent_membership(agent.id, 1, 'queue1')

        queue_ids = [1]

        agent_status_dao.remove_agent_from_queues(agent.id, queue_ids)

        memberships = self.session.query(AgentMembershipStatus).all()
        assert_that(memberships, empty())

    def test_remove_agent_from_queues_remove_only_one_queue(self):
        agent = self.add_agent()
        self._insert_agent_membership(agent.id, 1, 'queue1')
        self._insert_agent_membership(agent.id, 2, 'queue2')

        queue_ids = [1]

        agent_status_dao.remove_agent_from_queues(agent.id, queue_ids)
        memberships = self.session.query(AgentMembershipStatus).all()
        assert_that(
            memberships,
            contains_exactly(
                has_properties(queue_id=2, queue_name='queue2', agent_id=agent.id),
            ),
        )

    def test_remove_agent_from_all_queues(self):
        agent = self.add_agent()
        self._insert_agent_membership(agent.id, 1, 'queue1')
        self._insert_agent_membership(agent.id, 2, 'queue2')

        agent_status_dao.remove_agent_from_all_queues(agent.id)

        memberships = self.session.query(AgentMembershipStatus).all()
        assert_that(memberships, empty())

    def test_remove_all_agents_from_queue(self):
        queue1_id = 42
        queue1_name = 'queue1'
        queue2_id = 43
        queue2_name = 'queue2'
        self._insert_agent_membership(1, queue1_id, queue1_name)
        self._insert_agent_membership(2, queue1_id, queue1_name)
        self._insert_agent_membership(1, queue2_id, queue2_name)

        agent_status_dao.remove_all_agents_from_queue(queue1_id)

        memberships = self.session.query(AgentMembershipStatus).all()
        assert_that(
            memberships,
            contains_exactly(
                has_properties(queue_id=queue2_id, queue_name=queue2_name),
            ),
        )

    def test_update_penalty(self):
        agent_id = 42
        queue_id = 42
        queue_name = '42'
        queue_penalty_before = 42
        queue_penalty_after = 43
        self._insert_agent_membership(
            agent_id, queue_id, queue_name, queue_penalty_before
        )

        agent_status_dao.update_penalty(agent_id, queue_id, queue_penalty_after)

        memberships = self.session.query(AgentMembershipStatus).filter(
            and_(
                AgentMembershipStatus.queue_id == queue_id,
                AgentMembershipStatus.agent_id == agent_id,
            )
        )
        assert_that(
            memberships, contains_exactly(has_properties(penalty=queue_penalty_after))
        )

    def test_update_pause_status(self):
        agent_number = '1000'
        reason = 'Time for pause'

        agent = self.add_agent(number=agent_number)
        self._insert_agent_login_status(agent.id, agent_number)

        agent_status_dao.update_pause_status(agent.id, True, reason)
        agent_status = agent_status_dao.get_status(agent.id)

        assert_that(
            agent_status,
            has_properties(
                agent_id=agent.id,
                paused=True,
                paused_reason=reason,
            ),
        )

        agent_status_dao.update_pause_status(agent.id, False)
        agent_status = agent_status_dao.get_status(agent.id)
        assert_that(agent_status, has_properties(agent_id=agent.id, paused=False))

        agent_status_dao.update_pause_status(agent.id, True)
        agent_status = agent_status_dao.get_status(agent.id)

        assert_that(
            agent_status,
            has_properties(agent_id=agent.id, paused=True, paused_reason=None),
        )

    def test_get_agent_login_status_by_id_for_logoff(self):
        agent = self.add_agent()
        self._insert_agent_login_status(agent.id, agent.number)

        agent_login_status = agent_status_dao.get_agent_login_status_by_id_for_logoff(
            agent.id
        )
        assert_that(agent_login_status, has_properties(agent_id=agent.id))

        agent_status_dao.log_off_agent(agent.id)

        agent_login_status = agent_status_dao.get_agent_login_status_by_id_for_logoff(
            agent.id
        )
        assert_that(agent_login_status, none())

    def _insert_agent_login_status(
        self,
        agent_id,
        agent_number,
        extension=None,
        context='default',
        interface=None,
        state_interface='SIP/abcdef',
    ):
        if extension is None:
            extension = f'1{agent_number}'
        if interface is None:
            interface = f'Local/{agent_id}@foo'
        agent_status = AgentLoginStatus()
        agent_status.agent_id = agent_id
        agent_status.agent_number = agent_number
        agent_status.extension = extension
        agent_status.context = context
        agent_status.interface = interface
        agent_status.state_interface = state_interface

        self.add_me(agent_status)

        return agent_status

    def _insert_agent_membership(self, agent_id, queue_id, queue_name, queue_penalty=0):
        agent_membership = AgentMembershipStatus(
            agent_id=agent_id,
            queue_id=queue_id,
            queue_name=queue_name,
            penalty=queue_penalty,
        )
        self.add_me(agent_membership)

        return agent_membership

    def _insert_queue(self, queue_id, queue_name, queue_number):
        queue = QueueFeatures()
        queue.tenant_uuid = self.default_tenant.uuid
        queue.name = queue_name
        queue.displayname = queue_name
        queue.number = queue_number

        self.add_me(queue)

        return queue

    def _insert_agent_queue_member(self, agent_id, queue_name):
        queue_member = QueueMember()
        queue_member.queue_name = queue_name
        queue_member.interface = f'Agent/{agent_id}'
        queue_member.penalty = 0
        queue_member.usertype = 'agent'
        queue_member.userid = agent_id
        queue_member.channel = 'foobar'
        queue_member.category = 'queue'

        self.add_me(queue_member)
