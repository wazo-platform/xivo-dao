# -*- coding: utf-8 -*-
# Copyright 2012-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, calling, equal_to, raises

from xivo_dao import user_dao
from xivo_dao.tests.test_dao import DAOTestCase


class TestUserFeaturesDAO(DAOTestCase):

    def test_get_user_by_number_context(self):
        context, number = 'default', '1234'
        user_line = self.add_user_line_with_exten(exten=number,
                                                  context=context)

        user = user_dao.get_user_by_number_context(number, context)

        assert_that(user.id, equal_to(user_line.user.id))

    def test_get_user_by_number_context_line_commented(self):
        context, number = 'default', '1234'
        self.add_user_line_with_exten(exten=number,
                                      context=context,
                                      commented_line=1)

        self.assertRaises(LookupError, user_dao.get_user_by_number_context, number, context)

    def test_get_user_by_agent_id(self):
        agent_id = 42
        user = self.add_user(agent_id=agent_id)

        result = user_dao.get_user_by_agent_id(agent_id)
        assert_that(result, equal_to(user))

        assert_that(
            calling(user_dao.get_user_by_agent_id).with_args(43),
            raises(LookupError),
        )
