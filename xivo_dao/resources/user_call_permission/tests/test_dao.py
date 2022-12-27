# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (assert_that,
                      empty,
                      equal_to,
                      has_properties,
                      has_length,
                      none,
                      has_items,
                      contains)

from xivo_dao.alchemy.rightcallmember import RightCallMember as UserCallPermission
from xivo_dao.helpers.exception import NotFoundError, InputError
from xivo_dao.resources.user_call_permission import dao as user_call_permission_dao
from xivo_dao.tests.test_dao import DAOTestCase


class TestFindAllBy(DAOTestCase):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, user_call_permission_dao.find_by, invalid=42)

    def test_find_all_by_when_no_user_call_permission(self):
        result = user_call_permission_dao.find_all_by()

        assert_that(result, empty())

    def test_find_all_by(self):
        user_call_permission = self.add_user_call_permission_with_user_and_call_permission()

        result = user_call_permission_dao.find_all_by(user_id=user_call_permission.user_id)
        assert_that(result, contains(user_call_permission))

        result = user_call_permission_dao.find_all_by(call_permission_id=user_call_permission.call_permission_id)
        assert_that(result, contains(user_call_permission))

        result = user_call_permission_dao.find_all_by(user_id=user_call_permission.user_id,
                                                      call_permission_id=user_call_permission.call_permission_id)
        assert_that(result, contains(user_call_permission))

    def test_find_all_by_user_id_two_user_call_permissions(self):
        user = self.add_user()
        call_permission1 = self.add_call_permission()
        call_permission2 = self.add_call_permission()
        self.add_user_call_permission(user_id=user.id,
                                      call_permission_id=call_permission1.id)
        self.add_user_call_permission(user_id=user.id,
                                      call_permission_id=call_permission2.id)

        result = user_call_permission_dao.find_all_by(user_id=user.id)

        assert_that(result, has_items(
            has_properties({'user_id': user.id,
                            'call_permission_id': call_permission2.id}),
            has_properties({'user_id': user.id,
                            'call_permission_id': call_permission1.id}),
        ))

    def test_find_all_by_call_permission_id_two_user_call_permissions(self):
        call_permission = self.add_call_permission()
        user1 = self.add_user()
        user2 = self.add_user()
        self.add_user_call_permission(user_id=user1.id,
                                      call_permission_id=call_permission.id)
        self.add_user_call_permission(user_id=user2.id,
                                      call_permission_id=call_permission.id)

        result = user_call_permission_dao.find_all_by(call_permission_id=call_permission.id)

        assert_that(result, has_items(
            has_properties({'user_id': user1.id,
                            'call_permission_id': call_permission.id}),
            has_properties({'user_id': user2.id,
                            'call_permission_id': call_permission.id}),
        ))

    def test_find_all_by_user_id_call_permission_id_two_user_call_permissions(self):
        call_permission = self.add_call_permission()
        user1 = self.add_user()
        user2 = self.add_user()
        self.add_user_call_permission(user_id=user1.id,
                                      call_permission_id=call_permission.id)
        self.add_user_call_permission(user_id=user2.id,
                                      call_permission_id=call_permission.id)

        result = user_call_permission_dao.find_all_by(call_permission_id=call_permission.id,
                                                      user_id=user1.id)

        assert_that(result, has_items(
            has_properties({'user_id': user1.id,
                            'call_permission_id': call_permission.id}),
        ))

    def test_find_all_by_when_group_associate_to_call_permission(self):
        call_permission = self.add_call_permission()
        user = self.add_user()
        group = self.add_group()
        self.add_user_call_permission(user_id=user.id,
                                      call_permission_id=call_permission.id)
        self.add_group_call_permission(typeval=group.id,
                                       call_permission_id=call_permission.id)

        result = user_call_permission_dao.find_all_by(call_permission_id=call_permission.id)

        assert_that(result, has_length(1))
        assert_that(result, has_items(
            has_properties({'user_id': user.id,
                            'call_permission_id': call_permission.id}),
        ))


class TestFindBy(DAOTestCase):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, user_call_permission_dao.find_by, invalid=42)

    def test_find_by_when_no_user_call_permission(self):
        result = user_call_permission_dao.find_by()

        assert_that(result, equal_to(None))

    def test_find_by(self):
        user_call_permission = self.add_user_call_permission_with_user_and_call_permission()

        result = user_call_permission_dao.find_by(user_id=user_call_permission.user_id)
        assert_that(result, equal_to(user_call_permission))

        result = user_call_permission_dao.find_by(call_permission_id=user_call_permission.call_permission_id)
        assert_that(result, equal_to(user_call_permission))

        result = user_call_permission_dao.find_by(user_id=user_call_permission.user_id,
                                                  call_permission_id=user_call_permission.call_permission_id)
        assert_that(result, equal_to(user_call_permission))


class TestGetBy(DAOTestCase):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, user_call_permission_dao.get_by, invalid=42)

    def test_given_user_call_permission_does_not_exist_then_raises_error(self):
        self.assertRaises(NotFoundError, user_call_permission_dao.get_by, user_id=1)

    def test_get_by_user_id(self):
        user_call_permission = self.add_user_call_permission_with_user_and_call_permission()

        result = user_call_permission_dao.get_by(user_id=user_call_permission.user_id)
        assert_that(result, equal_to(user_call_permission))


class TestAssociate(DAOTestCase):

    def test_associate_user_with_call_permission(self):
        user = self.add_user()
        call_permission = self.add_call_permission()

        result = user_call_permission_dao.associate(user, call_permission)

        assert_that(result, has_properties({'user_id': user.id,
                                            'call_permission_id': call_permission.id}))

    def test_associate_user_with_call_permission_already_associated(self):
        user = self.add_user()
        call_permission = self.add_call_permission()
        user_call_permission_dao.associate(user, call_permission)

        result = user_call_permission_dao.associate(user, call_permission)

        assert_that(result, has_properties({'user_id': user.id,
                                            'call_permission_id': call_permission.id}))


class TestDissociate(DAOTestCase):

    def test_dissociate_user_call_permission(self):
        user_call_permission = self.add_user_call_permission_with_user_and_call_permission()

        user_call_permission_dao.dissociate(user_call_permission.user, user_call_permission.call_permission)

        result = (self.session.query(UserCallPermission)
                  .filter(UserCallPermission.id == user_call_permission.id)
                  .first())

        assert_that(result, none())

    def test_dissociate_user_call_permission_not_associated(self):
        user = self.add_user()
        call_permission = self.add_call_permission()

        user_call_permission_dao.dissociate(user, call_permission)

        result = (self.session.query(UserCallPermission)
                  .filter(UserCallPermission.id == user.id)
                  .first())

        assert_that(result, none())


class TestDissociateAllByUser(DAOTestCase):

    def test_dissociate_all_by_user(self):
        user = self.add_user()
        call_permission1 = self.add_call_permission()
        call_permission2 = self.add_call_permission()
        user_call_permission_dao.associate(user, call_permission1)
        user_call_permission_dao.associate(user, call_permission2)

        user_call_permission_dao.dissociate_all_by_user(user)

        result = (self.session.query(UserCallPermission)
                  .filter(UserCallPermission.user_id == user.id)
                  .first())

        assert_that(result, none())
