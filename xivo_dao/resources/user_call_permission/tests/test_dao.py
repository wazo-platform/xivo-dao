# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from hamcrest import (assert_that,
                      equal_to,
                      has_properties,
                      none,
                      has_items,
                      contains,
                      has_length)

from xivo_dao.alchemy.rightcallmember import RightCallMember as UserCallPermission
from xivo_dao.resources.user_call_permission import dao as user_call_permission_dao
from xivo_dao.tests.test_dao import DAOTestCase


class TestUserCallPermissionFindAllByUserId(DAOTestCase):

    def test_find_all_by_user_id_no_user_call_permission(self):
        expected_result = []
        result = user_call_permission_dao.find_all_by_user_id(1)

        assert_that(result, equal_to(expected_result))

    def test_find_all_by_user_id(self):
        user_call_permission = self.add_user_call_permission_with_user_and_call_permission()

        result = user_call_permission_dao.find_all_by_user_id(user_call_permission.user_id)

        assert_that(result, contains(user_call_permission))

    def test_find_all_by_user_id_two_user_call_permissions(self):
        user = self.add_user()
        call_permission1 = self.add_call_permission()
        call_permission2 = self.add_call_permission()
        self.add_user_call_permission(user_id=user.id,
                                      call_permission_id=call_permission1.id)
        self.add_user_call_permission(user_id=user.id,
                                      call_permission_id=call_permission2.id)

        result = user_call_permission_dao.find_all_by_user_id(user.id)

        assert_that(result, has_items(
            has_properties({'user_id': user.id,
                            'call_permission_id': call_permission2.id}),
            has_properties({'user_id': user.id,
                            'call_permission_id': call_permission1.id}),
        ))


class TestUserCallPermissionFindAllByCallPermissionId(DAOTestCase):

    def test_find_all_by_call_permission_id_no_user_call_permission(self):
        result = user_call_permission_dao.find_all_by_call_permission_id(1)

        assert_that(result, has_length(0))

    def test_find_all_by_call_permission_id(self):
        user_call_permission = self.add_user_call_permission_with_user_and_call_permission()

        result = user_call_permission_dao.find_all_by_call_permission_id(user_call_permission.call_permission_id)

        assert_that(result, contains(user_call_permission))

    def test_find_all_by_call_permission_id_two_user_call_permissions(self):
        call_permission = self.add_call_permission()
        user1 = self.add_user()
        user2 = self.add_user()
        self.add_user_call_permission(user_id=user1.id,
                                      call_permission_id=call_permission.id)
        self.add_user_call_permission(user_id=user2.id,
                                      call_permission_id=call_permission.id)

        result = user_call_permission_dao.find_all_by_call_permission_id(call_permission.id)

        assert_that(result, has_items(
            has_properties({'user_id': user1.id,
                            'call_permission_id': call_permission.id}),
            has_properties({'user_id': user2.id,
                            'call_permission_id': call_permission.id}),
        ))


class TestAssociateUserCallPermission(DAOTestCase):

    def test_associate_user_with_call_permission(self):
        user = self.add_user()
        call_permission = self.add_call_permission()

        result = user_call_permission_dao.associate(user, call_permission)

        assert_that(result, has_properties({'user_id': user.id,
                                            'call_permission_id': call_permission.id}))


class TestDissociateUserLine(DAOTestCase):

    def test_dissociate_user_call_permission(self):
        user_call_permission = self.add_user_call_permission_with_user_and_call_permission()

        user_call_permission_dao.dissociate(user_call_permission.user, user_call_permission.call_permission)

        result = (self.session.query(UserCallPermission)
                  .filter(UserCallPermission.id == user_call_permission.id)
                  .first())

        assert_that(result, none())
