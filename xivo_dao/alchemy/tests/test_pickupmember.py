# Copyright 2019-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, contains_inanyorder

from xivo_dao.tests.test_dao import DAOTestCase


class TestUsersFromGroup(DAOTestCase):
    def test_getter(self):
        user1 = self.add_user()
        user2 = self.add_user()
        group = self.add_group()
        self.add_queue_member(
            queue_name=group.name,
            category='group',
            usertype='user',
            userid=user1.id,
        )
        self.add_queue_member(
            queue_name=group.name,
            category='group',
            usertype='user',
            userid=user2.id,
        )
        call_pickup = self.add_pickup()
        pickup_member = self.add_pickup_member(
            pickupid=call_pickup.id,
            membertype='group',
            memberid=group.id,
        )
        assert_that(pickup_member.users_from_group, contains_inanyorder(user1, user2))
