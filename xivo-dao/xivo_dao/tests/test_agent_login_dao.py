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
        extension = '1001'
        context = 'default'

        agent_login_dao.log_in_agent(agent_id, extension, context)

        agent = agent_login_dao.get_status(agent_id)

        self.assertEquals(agent.agent_id, agent_id)
        self.assertEquals(agent.extension, extension)
        self.assertEquals(agent.context, context)

    def test_log_off_agent(self):
        agent_id = 1
        extension = '1001'
        context = 'default'
        self._create_agent(agent_id, extension, context)

        agent_login_dao.log_off_agent(agent_id)

        self.assertRaises(LookupError, agent_login_dao.get_status, 1)

    def test_get_status_with_unlogged_agent_raise_error(self):
        self.assertRaises(LookupError, agent_login_dao.get_status, 1)

    def test_is_extension_in_use_with_an_agent(self):
        agent_id = 1
        extension = '1001'
        context = 'default'
        self._create_agent(agent_id, extension, context)

        in_use = agent_login_dao.is_extension_in_use(extension, context)

        self.assertTrue(in_use)

    def test_is_extension_in_use_with_no_agent(self):
        extension = '1001'
        context = 'default'

        in_use = agent_login_dao.is_extension_in_use(extension, context)

        self.assertFalse(in_use)

    def _create_agent(self, agent_id, extension='1001', context='default'):
        agent = AgentLoginStatus()
        agent.extension = extension
        agent.context = context

        try:
            self.session.add(agent)
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

        return agent
