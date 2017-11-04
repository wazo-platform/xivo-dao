# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import assert_that, equal_to

from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.resources.agent import dao as agent_dao


class TestAgentExist(DAOTestCase):

    def test_given_no_agent_then_returns_false(self):
        result = agent_dao.exists(1)

        assert_that(result, equal_to(False))

    def test_given_agent_exists_then_return_true(self):
        agent_row = self.add_agent()

        result = agent_dao.exists(agent_row.id)

        assert_that(result, equal_to(True))
