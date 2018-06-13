# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import (
    assert_that,
    none,
)
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.resources.func_key.tests.test_helpers import FuncKeyHelper

from ..func_key_dest_agent import FuncKeyDestAgent


class TestDelete(DAOTestCase, FuncKeyHelper):

    def setUp(self):
        super(TestDelete, self).setUp()
        self.setup_funckeys()

    def test_funckeys_are_deleted(self):
        agent = self.add_agent()
        extension = self.add_extension()
        self.add_agent_destination(agent.id, extension.id)

        self.session.delete(agent)
        self.session.flush()

        row = self.session.query(FuncKeyDestAgent).first()
        assert_that(row, none())
