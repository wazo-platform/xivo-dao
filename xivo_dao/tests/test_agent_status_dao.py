# Copyright 2013-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, contains, empty, has_properties, none
from xivo_dao import agent_status_dao
from xivo_dao.tests.test_dao import DAOTestCase, UNKNOWN_UUID
from xivo_dao.alchemy.agent_login_status import AgentLoginStatus
from xivo_dao.alchemy.agent_membership_status import AgentMembershipStatus
from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_dao.alchemy.queuemember import QueueMember
from sqlalchemy import and_


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
                user_ids=contains(user.id),
            ),
        )

    def test_log_in_agent_no_user(self):
        agent_id = 1
        agent_number = '2'
        extension = '1001'
        context = 'default'
        interface = 'sip/abcdef'
        paused = False
        paused_reason = None
        state_interface = interface

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
                user_ids=empty(),
            ),
        )

    def test_log_off_agent(self):
        agent_id = 1
        agent_number = '42'
        self._insert_agent_login_status(agent_id, agent_number)

        agent_status_dao.log_off_agent(agent_id)

        agent_status = self.session.query(AgentLoginStatus).get(agent_id)
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

        self.assertEqual(extension, result_extension)
        self.assertEqual(context, result_context)

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

        self.assertEqual(result, agent_id)

    def test_get_status_with_unlogged_agent_returns_none(self):
        agent_id = 1
        agent_status = agent_status_dao.get_status(agent_id)
        self.assertEqual(agent_status, None)

    def test_get_status_with_logged_agent_returns_an_agent(self):
        agent = self.add_agent()
        agent_login_status = self._insert_agent_login_status(agent.id, agent.number)
        agent_membership = self._insert_agent_membership(agent.id, 1, 'queue1', 64)

        result = agent_status_dao.get_status(agent.id)

        assert_that(
            result,
            has_properties(
                agent_id=agent.id,
                agent_number=agent.number,
                extension=agent_login_status.extension,
                interface=agent_login_status.interface,
                state_interface=agent_login_status.state_interface,
                queues=contains(
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
        agent_membership = self._insert_agent_membership(agent.id, 1, 'queue1', 64)

        result = agent_status_dao.get_status(agent.id, tenant_uuids=[tenant.uuid])
        assert_that(
            result,
            has_properties(
                agent_id=agent.id,
                queues=contains(has_properties(id=agent_membership.queue_id)),
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
        agent_login_status = self._insert_agent_login_status(agent.id, agent.number)
        agent_membership = self._insert_agent_membership(agent.id, 1, 'queue1')

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
                queues=contains(
                    has_properties(
                        id=agent_membership.queue_id, name=agent_membership.queue_name
                    )
                ),
                user_ids=contains(user.id),
            ),
        )

    def test_get_status_by_number_with_logged_agent_no_user(self):
        agent = self.add_agent()
        agent_login_status = self._insert_agent_login_status(agent.id, agent.number)
        agent_membership = self._insert_agent_membership(agent.id, 1, 'queue1')

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
                queues=contains(
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
                queues=contains(has_properties(id=agent_membership.queue_id)),
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
        agent_membership = self._insert_agent_membership(agent.id, 1, 'queue1')

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
                queues=contains(
                    has_properties(
                        id=agent_membership.queue_id, name=agent_membership.queue_name
                    )
                ),
                user_ids=contains(user.id),
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
                queues=contains(has_properties(id=agent_membership.queue_id)),
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

    def test_get_status_by_state_interface_with_logged_agent(self):
        agent = self.add_agent()
        user = self.add_user(agentid=agent.id)
        agent_login_status = self._insert_agent_login_status(agent.id, agent.number)
        agent_membership = self._insert_agent_membership(agent.id, 1, 'queue1')

        result = agent_status_dao.get_status_by_state_interface(
            agent_login_status.state_interface
        )

        assert_that(
            result,
            has_properties(
                agent_id=agent.id,
                agent_number=agent.number,
                extension=agent_login_status.extension,
                context=agent_login_status.context,
                interface=agent_login_status.interface,
                state_interface=agent_login_status.state_interface,
                queues=contains(
                    has_properties(
                        id=agent_membership.queue_id, name=agent_membership.queue_name
                    )
                ),
                user_ids=contains(user.id),
            ),
        )

    def test_get_status_by_state_interface_with_wrong_state_interface(self):
        result = agent_status_dao.get_status_by_state_interface("wrong state interface")

        assert_that(result, none())

    def test_get_statuses_of_unlogged_agent(self):
        agent = self.add_agent()

        statuses = agent_status_dao.get_statuses()

        assert_that(
            statuses,
            contains(
                has_properties(
                    agent_id=agent.id,
                    agent_number=agent.number,
                    logged=False,
                    extension=None,
                    context=None,
                    state_interface=None,
                )
            ),
        )

    def test_get_statuses_of_logged_agent(self):
        agent = self.add_agent()
        agent_login_status = self._insert_agent_login_status(agent.id, agent.number)

        statuses = agent_status_dao.get_statuses()

        assert_that(
            statuses,
            contains(
                has_properties(
                    agent_id=agent.id,
                    agent_number=agent.number,
                    logged=True,
                    extension=agent_login_status.extension,
                    context=agent_login_status.context,
                    state_interface=agent_login_status.state_interface,
                )
            ),
        )

    def test_get_statuses_of_logged_agent_multi_tenant(self):
        tenant = self.add_tenant()
        agent = self.add_agent(tenant_uuid=tenant.uuid)
        self._insert_agent_login_status(agent.id, agent.number)

        statuses = agent_status_dao.get_statuses(tenant_uuids=[tenant.uuid])

        self.assertEqual(len(statuses), 1)
        self.assertEqual(statuses[0].agent_id, agent.id)
        self.assertEqual(statuses[0].tenant_uuid, tenant.uuid)
        assert_that(
            statuses,
            contains(has_properties(agent_id=agent.id, tenant_uuid=tenant.uuid)),
        )

        statuses = agent_status_dao.get_statuses(
            tenant_uuids=[self.default_tenant.uuid]
        )
        assert_that(statuses, empty())

    def test_get_statuses_of_logged_for_queue(self):
        agent = self.add_agent()
        queue = self._insert_queue(1, 'queue1', '3000')
        self._insert_agent_queue_member(agent.id, queue.name)
        agent_login_status = self._insert_agent_login_status(agent.id, agent.number)

        statuses = agent_status_dao.get_statuses_for_queue(queue.id)

        assert_that(
            statuses,
            contains(
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
            contains(has_properties(agent_id=agent1.id, agent_number=agent1.number)),
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
            contains(has_properties(agent_id=agent1.id, agent_number=agent1.number)),
        )

    def test_get_logged_agent_ids(self):
        agent_id = 1
        agent_number = '42'
        self._insert_agent_login_status(agent_id, agent_number)

        agent_ids = agent_status_dao.get_logged_agent_ids()

        assert_that(agent_ids, contains(agent_id))

    def test_get_logged_agent_ids_multi_tenant(self):
        tenant = self.add_tenant()
        agent = self.add_agent(id=1, number='42', tenant_uuid=tenant.uuid)
        self._insert_agent_login_status(agent.id, agent.number)

        agent_ids = agent_status_dao.get_logged_agent_ids(tenant_uuids=[tenant.uuid])
        assert_that(agent_ids, contains(agent.id))

        agent_ids = agent_status_dao.get_logged_agent_ids(
            tenant_uuids=[self.default_tenant.uuid, tenant.uuid],
        )
        assert_that(agent_ids, contains(agent.id))

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
        queue1 = agent_status_dao._Queue(1, 'queue1', 3)
        queue2 = agent_status_dao._Queue(2, 'queue2', 4)

        queues = [queue1, queue2]

        agent_status_dao.add_agent_to_queues(agent.id, queues)

        memberships = self.session.query(AgentMembershipStatus).all()
        assert_that(
            memberships,
            contains(
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

        queues = [
            agent_status_dao._Queue(1, 'queue1', 0),
            agent_status_dao._Queue(2, 'queue2', 0),
        ]

        agent_status_dao.add_agent_to_queues(agent1.id, queues)
        agent_status_dao.add_agent_to_queues(agent2.id, queues)

        agent1_status = agent_status_dao.get_status(agent1.id)
        agent2_status = agent_status_dao.get_status(agent2.id)

        assert_that(
            agent1_status,
            has_properties(
                queues=contains(
                    has_properties(id=1, name='queue1'),
                    has_properties(id=2, name='queue2'),
                )
            ),
        )

        assert_that(
            agent2_status,
            has_properties(
                queues=contains(
                    has_properties(id=1, name='queue1'),
                    has_properties(id=2, name='queue2'),
                )
            ),
        )

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
            contains(
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
            contains(
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
        assert_that(memberships, contains(has_properties(penalty=queue_penalty_after)))

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
