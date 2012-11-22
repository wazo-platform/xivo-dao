# -*- coding: utf-8 -*-

from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.alchemy.agent_login_status import AgentLoginStatus
from xivo_dao import agent_login_dao


class TestAgentLoginDao(DAOTestCase):

    tables = [AgentLoginStatus]

    def setUp(self):
        self.empty_tables()

    def test_is_agent_logged_in_with_no_agents(self):
        agent_id = 1

        expected = False

        logged_in = agent_login_dao.is_agent_logged_in(agent_id)

        self.assertEqual(expected, logged_in)

    def test_is_agent_logged_in_when_one_agent_logged_in(self):
        agent = self._create_agent(1)

        expected = True

        logged_in = agent_login_dao.is_agent_logged_in(agent.agent_id)

        self.assertEquals(expected, logged_in)

    def test_log_in_agent(self):
        agent_id = 1
        interface = 'Local/1001@default'

        agent_login_dao.log_in_agent(agent_id, interface)

        agent = agent_login_dao.get_status(agent_id)

        self.assertEquals(agent.agent_id, agent_id)
        self.assertEquals(agent.interface, interface)

    def test_log_off_agent(self):
        agent_id = 1
        interface = 'Local/1001@default'
        self._create_agent(agent_id, interface)

        agent_login_dao.log_off_agent(agent_id)

        self.assertRaises(LookupError, agent_login_dao.get_status, 1)

    def test_get_status_with_unlogged_agent_raise_error(self):
        self.assertRaises(LookupError, agent_login_dao.get_status, 1)

    def _create_agent(self, agent_id, interface='Local/1001@default'):
        agent = AgentLoginStatus()
        agent.agent_id = agent_id
        agent.interface = interface

        try:
            self.session.add(agent)
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

        return agent
