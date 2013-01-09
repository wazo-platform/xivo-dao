# -*- coding: utf-8 -*-

from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_dao.alchemy.agent_login_status import AgentLoginStatus
from xivo_dao import agent_login_dao


class TestAgentLoginDao(DAOTestCase):

    tables = [AgentFeatures, AgentLoginStatus]

    def setUp(self):
        self.empty_tables()

    def test_is_agent_logged_in_with_no_agents(self):
        agent_id = 1

        expected = False

        logged_in = agent_login_dao.is_agent_logged_in(agent_id)

        self.assertEqual(expected, logged_in)

    def test_is_agent_logged_in_when_one_agent_logged_in(self):
        agent_status = self._insert_agent_status(1)

        expected = True

        logged_in = agent_login_dao.is_agent_logged_in(agent_status.agent_id)

        self.assertEquals(expected, logged_in)

    def test_log_in_agent(self):
        agent_id = 1
        extension = '1001'
        context = 'default'
        interface = 'sip/abcdef'
        state_interface = interface

        agent_login_dao.log_in_agent(agent_id, extension, context, interface, state_interface)

        agent_status = agent_login_dao.get_status(agent_id)

        self.assertEquals(agent_status.agent_id, agent_id)
        self.assertEquals(agent_status.extension, extension)
        self.assertEquals(agent_status.context, context)
        self.assertEquals(agent_status.interface, interface)
        self.assertEquals(agent_status.state_interface, state_interface)

    def test_log_off_agent(self):
        agent_id = 1
        self._insert_agent_status(agent_id)

        agent_login_dao.log_off_agent(agent_id)

        agent_status = self.session.query(AgentLoginStatus).get(agent_id)
        self.assertEquals(agent_status, None)

    def test_get_status_with_unlogged_agent_returns_none(self):
        agent_id = 1
        agent_status = agent_login_dao.get_status(agent_id)
        self.assertEquals(agent_status, None)

    def test_get_statuses_of_unlogged_agent(self):
        agent = self._insert_agent(42, '12')

        statuses = agent_login_dao.get_statuses()

        self.assertEqual(len(statuses), 1)
        self.assertEqual(statuses[0].agent_id, agent.id)
        self.assertEqual(statuses[0].agent_number, agent.number)
        self.assertEqual(statuses[0].logged, False)
        self.assertEqual(statuses[0].extension, None)
        self.assertEqual(statuses[0].context, None)

    def test_get_statuses_of_logged_agent(self):
        agent = self._insert_agent(42, '12')
        self._insert_agent_status(agent.id)

        statuses = agent_login_dao.get_statuses()

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
        self._insert_agent_status(agent_id, extension, context)

        in_use = agent_login_dao.is_extension_in_use(extension, context)

        self.assertTrue(in_use)

    def test_is_extension_in_use_with_no_agent(self):
        extension = '1001'
        context = 'default'

        in_use = agent_login_dao.is_extension_in_use(extension, context)

        self.assertFalse(in_use)

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

    def _insert_agent_status(self, agent_id, extension='1001', context='default', interface='sip/abcdef'):
        agent_status = AgentLoginStatus()
        agent_status.agent_id = agent_id
        agent_status.extension = extension
        agent_status.context = context
        agent_status.interface = interface
        agent_status.state_interface = interface

        try:
            self.session.add(agent_status)
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

        return agent_status
