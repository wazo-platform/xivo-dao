# Copyright 2014-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains_exactly,
    empty,
    has_item,
    has_items,
    has_properties,
    is_,
)

from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.resources.func_key.tests.test_helpers import FuncKeyHelper

from .. import dao


class TestFuncKeyDao(DAOTestCase, FuncKeyHelper):

    def setUp(self):
        super().setUp()
        self.setup_funckeys()


class TestFindAllForwards(TestFuncKeyDao):

    def prepare_user_and_forward(self, exten, fwd_type, number=None):
        user_row = self.add_user()

        exten_row = self.add_extenfeatures(exten, fwd_type)
        forward_row = self.add_forward_destination(exten_row.uuid, number)
        self.add_func_key_mapping(func_key_id=forward_row.func_key_id,
                                  destination_type_id=forward_row.destination_type_id,
                                  template_id=user_row.func_key_private_template_id,
                                  position=1,
                                  blf=True)

        return user_row, forward_row

    def test_given_no_forwards_then_returns_empty_list(self):
        result = dao.find_all_forwards(1, 'unconditional')

        assert_that(result, contains_exactly())

    def test_given_unconditional_forward_then_list_contains_unconditional_forward(self):
        number = '1234'
        user_row, forward_row = self.prepare_user_and_forward('_*21.', 'fwdunc', number)

        result = dao.find_all_forwards(user_row.id, 'unconditional')

        assert_that(result, contains_exactly(
            has_properties(
                number=number,
            )
        ))

    def test_given_noanswer_forward_then_list_contains_noanswer_forward(self):
        number = '1234'
        user_row, forward_row = self.prepare_user_and_forward('_*22.', 'fwdrna', number)

        result = dao.find_all_forwards(user_row.id, 'noanswer')

        assert_that(result, contains_exactly(
            has_properties(
                number=number,
            )
        ))

    def test_given_busy_forward_then_list_contains_busy_forward(self):
        number = '1234'
        user_row, forward_row = self.prepare_user_and_forward('_*23.', 'fwdbusy', number)

        result = dao.find_all_forwards(user_row.id, 'busy')

        assert_that(result, contains_exactly(
            has_properties(
                number=number,
            )
        ))


class TestFindUsersHavingUserDestination(TestFuncKeyDao):

    def test_given_user_not_a_user_destination(self):
        user_row = self.add_user()

        result = dao.find_users_having_user_destination(user_row)
        assert_that(result, is_(empty()))

    def test_given_user_is_multiple_user_destination(self):
        user1 = self.add_user()
        user2 = self.add_user()
        user3 = self.add_user()
        user1_destination = self.add_user_destination(user1.id)
        self.add_func_key_to_user(user1_destination, user2)
        self.add_func_key_to_user(user1_destination, user3)

        result = dao.find_users_having_user_destination(user1)

        assert_that(result, has_items(
            has_properties(id=user2.id),
            has_properties(id=user3.id)
        ))

    def test_given_user_is_multiple_user_destination_with_public_template(self):
        template1 = self.add_func_key_template()
        user1 = self.add_user()
        user2 = self.add_user()
        user3 = self.add_user(func_key_template_id=template1.id)
        user1_destination = self.add_user_destination(user1.id)

        self.add_func_key_to_user(user1_destination, user2)
        self.add_destination_to_template(user1_destination, template1)

        result = dao.find_users_having_user_destination(user1)

        assert_that(result, has_items(
            has_properties(id=user2.id),
            has_properties(id=user3.id)
        ))

    def test_given_user_is_self_destination(self):
        user1 = self.add_user()
        user1_destination = self.add_user_destination(user1.id)
        self.add_func_key_to_user(user1_destination, user1)

        result = dao.find_users_having_user_destination(user1)

        assert_that(result, has_item(
            has_properties(id=user1.id)
        ))
