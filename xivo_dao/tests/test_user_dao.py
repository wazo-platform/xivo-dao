# Copyright 2012-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, calling, equal_to, raises

from xivo_dao import user_dao
from xivo_dao.tests.test_dao import DAOTestCase


class TestUserFeaturesDAO(DAOTestCase):
    def test_get_user_by_number_context(self):
        context = self.add_context(name='default')
        number = '1234'
        user_line = self.add_user_line_with_exten(exten=number, context=context.name)

        user = user_dao.get_user_by_number_context(number, context.name)

        assert_that(user.id, equal_to(user_line.user.id))

    def test_get_user_by_number_context_line_commented(self):
        context = self.add_context(name='default')
        number = '1234'
        self.add_user_line_with_exten(
            exten=number, context=context.name, commented_line=1
        )

        self.assertRaises(
            LookupError, user_dao.get_user_by_number_context, number, context.name
        )

    def test_get_user_by_agent_id(self):
        agent_id = 42
        user = self.add_user(agent_id=agent_id)

        result = user_dao.get_user_by_agent_id(agent_id)
        assert_that(result, equal_to(user))

        assert_that(
            calling(user_dao.get_user_by_agent_id).with_args(43),
            raises(LookupError),
        )
