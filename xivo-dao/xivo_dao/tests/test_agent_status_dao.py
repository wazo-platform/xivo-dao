# -*- coding: utf-8 -*-

from xivo_dao import agent_status_dao
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_dao.alchemy.agent_login_status import AgentLoginStatus
from xivo_dao.alchemy.agent_membership_status import AgentMembershipStatus


class TestAgentStatusDao(DAOTestCase):

    tables = [AgentFeatures, AgentLoginStatus, AgentMembershipStatus]

    def setUp(self):
        self.empty_tables()

    def test_is_agent_logged_in_with_no_agents(self):
        agent_id = 1

        expected = False

        logged_in = agent_status_dao.is_agent_logged_in(agent_id)

        self.assertEqual(expected, logged_in)

    def test_is_agent_logged_in_when_one_agent_logged_in(self):
        agent_login_status = self._insert_agent_login_status(1)

        expected = True

        logged_in = agent_status_dao.is_agent_logged_in(agent_login_status.agent_id)

        self.assertEquals(expected, logged_in)

    def test_log_in_agent(self):
        agent_id = 1
        extension = '1001'
        context = 'default'
        interface = 'sip/abcdef'
        state_interface = interface

        agent_status_dao.log_in_agent(agent_id, extension, context, interface, state_interface)

        agent_status = agent_status_dao.get_status(agent_id)

        self.assertEquals(agent_status.agent_id, agent_id)
        self.assertEquals(agent_status.extension, extension)
        self.assertEquals(agent_status.context, context)
        self.assertEquals(agent_status.interface, interface)
        self.assertEquals(agent_status.state_interface, state_interface)

    def test_log_off_agent(self):
        agent_id = 1
        self._insert_agent_login_status(agent_id)

        agent_status_dao.log_off_agent(agent_id)

        agent_status = self.session.query(AgentLoginStatus).get(agent_id)
        self.assertEquals(agent_status, None)

    def test_get_status_with_unlogged_agent_returns_none(self):
        agent_id = 1
        agent_status = agent_status_dao.get_status(agent_id)
        self.assertEquals(agent_status, None)

    def test_get_status_with_logged_agent_returns_an_agent(self):
        agent = self._insert_agent(42, '12')
        agent_login_status = self._insert_agent_login_status(agent.id)
        agent_membership = self._insert_agent_membership(agent.id, 1, 'queue1')

        result = agent_status_dao.get_status(agent.id)

        self.assertEquals(result.agent_id, agent.id)
        self.assertEquals(result.extension, agent_login_status.extension)
        self.assertEquals(result.context, agent_login_status.context)
        self.assertEquals(result.interface, agent_login_status.interface)
        self.assertEquals(result.state_interface, agent_login_status.state_interface)
        self.assertEquals(len(result.queues), 1)
        self.assertEquals(result.queues[0].id, agent_membership.queue_id)
        self.assertEquals(result.queues[0].name, agent_membership.queue_name)

    def test_get_statuses_of_unlogged_agent(self):
        agent = self._insert_agent(42, '12')

        statuses = agent_status_dao.get_statuses()

        self.assertEqual(len(statuses), 1)
        self.assertEqual(statuses[0].agent_id, agent.id)
        self.assertEqual(statuses[0].agent_number, agent.number)
        self.assertEqual(statuses[0].logged, False)
        self.assertEqual(statuses[0].extension, None)
        self.assertEqual(statuses[0].context, None)

    def test_get_statuses_of_logged_agent(self):
        agent = self._insert_agent(42, '12')
        self._insert_agent_login_status(agent.id)

        statuses = agent_status_dao.get_statuses()

        self.assertEqual(len(statuses), 1)
        self.assertEqual(statuses[0].agent_id, agent.id)
        self.assertEqual(statuses[0].agent_number, agent.number)
        self.assertEqual(statuses[0].logged, True)
        self.assertEqual(statuses[0].extension, '1001')
        self.assertEqual(statuses[0].context, 'default')

    def test_is_extension_in_use_with_an_agent(self):
        agent_id = 1
        extension = '1001'
        context = 'default'
        self._insert_agent_login_status(agent_id, extension, context)

        in_use = agent_status_dao.is_extension_in_use(extension, context)

        self.assertTrue(in_use)

    def test_is_extension_in_use_with_no_agent(self):
        extension = '1001'
        context = 'default'

        in_use = agent_status_dao.is_extension_in_use(extension, context)

        self.assertFalse(in_use)

    def test_add_agent_to_queues(self):
        agent = self._insert_agent(42, '12')

        queues = [agent_status_dao._Queue(1, 'queue1'),
                  agent_status_dao._Queue(2, 'queue2'),
                  ]

        agent_status_dao.add_agent_to_queues(agent.id, queues)

        memberships = self.session.query(AgentMembershipStatus).all()
        self.assertEquals(len(memberships), 2)
        self.assertEquals(memberships[0].queue_id, 1)
        self.assertEquals(memberships[0].queue_name, 'queue1')
        self.assertEquals(memberships[1].queue_id, 2)
        self.assertEquals(memberships[1].queue_name, 'queue2')

    def test_add_agent_to_queue_two_agents(self):
        agent1 = self._insert_agent(42, '12')
        agent1_status = self._insert_agent_login_status(agent1.id)
        agent2 = self._insert_agent(43, '13')
        agent2_status = self._insert_agent_login_status(agent2.id, '1002', 'default', interface='Local/2@foo', state_interface='SIP/defabc')

        queues = [agent_status_dao._Queue(1, 'queue1'),
                  agent_status_dao._Queue(2, 'queue2'),
                  ]

        agent_status_dao.add_agent_to_queues(agent1.id, queues)
        agent_status_dao.add_agent_to_queues(agent2.id, queues)

        agent1_status = agent_status_dao.get_status(agent1.id)
        agent2_status = agent_status_dao.get_status(agent2.id)

        self.assertEquals(len(agent1_status.queues), 2)
        self.assertEquals(agent1_status.queues[0].id, 1)
        self.assertEquals(agent1_status.queues[0].name, 'queue1')
        self.assertEquals(agent1_status.queues[1].id, 2)
        self.assertEquals(agent1_status.queues[1].name, 'queue2')

        self.assertEquals(len(agent2_status.queues), 2)
        self.assertEquals(agent2_status.queues[0].id, 1)
        self.assertEquals(agent2_status.queues[0].name, 'queue1')
        self.assertEquals(agent2_status.queues[1].id, 2)
        self.assertEquals(agent2_status.queues[1].name, 'queue2')

    def test_remove_agent_from_queues_one_queue(self):
        agent = self._insert_agent(42, '12')
        self._insert_agent_membership(agent.id, 1, 'queue1')

        queues = [agent_status_dao._Queue(1, 'queue1')]

        agent_status_dao.remove_agent_from_queues(agent.id, queues)

        memberships = self.session.query(AgentMembershipStatus).all()
        self.assertEquals(len(memberships), 0)

    def test_remove_agent_from_queues_remove_only_one_queue(self):
        agent = self._insert_agent(42, '12')
        self._insert_agent_membership(agent.id, 1, 'queue1')
        self._insert_agent_membership(agent.id, 2, 'queue2')

        queues = [agent_status_dao._Queue(1, 'queue1')]

        agent_status_dao.remove_agent_from_queues(agent.id, queues)

        memberships = self.session.query(AgentMembershipStatus).all()
        self.assertEquals(len(memberships), 1)
        self.assertEquals(memberships[0].queue_id, 2)
        self.assertEquals(memberships[0].queue_name, 'queue2')
        self.assertEquals(memberships[0].agent_id, agent.id)


    def _insert_agent(self, agent_id, agent_number):
        agent = AgentFeatures()
        agent.id = agent_id
        agent.number = agent_number
        agent.numgroup = 6
        agent.passwd = ''
        agent.context = 'foobar'
        agent.language = ''

        self.session.add(agent)
        self.session.commit()

        return agent

    def _insert_agent_login_status(self, agent_id, extension='1001', context='default', interface='Local/1@foo',
                             state_interface='SIP/abcdef'):
        agent_status = AgentLoginStatus()
        agent_status.agent_id = agent_id
        agent_status.extension = extension
        agent_status.context = context
        agent_status.interface = interface
        agent_status.state_interface = state_interface

        try:
            self.session.add(agent_status)
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

        return agent_status

    def _insert_agent_membership(self, agent_id, queue_id, queue_name):
        agent_membership = AgentMembershipStatus(agent_id=agent_id,
                                                 queue_id=queue_id,
                                                 queue_name=queue_name)
        try:
            self.session.add(agent_membership)
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

        return agent_membership
