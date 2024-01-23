# Copyright 2021-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, equal_to, none

from xivo_dao.tests.test_dao import DAOTestCase


class TestAgentStatus(DAOTestCase):
    def test_agent_relationsip(self):
        agent = self.add_agent()
        agent_status = self.add_agent_login_status(agent_id=agent.id)

        self.session.expire_all()

        assert_that(agent_status.agent, equal_to(agent))

    def test_agent_relationsip_no_agent(self):
        agent_status = self.add_agent_login_status(agent_id=42)

        self.session.expire_all()

        assert_that(agent_status.agent, none())
