# -*- coding: utf-8 -*-
# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from hamcrest import (
    assert_that,
    contains,
    equal_to,
    empty,
    none,
)

from xivo_dao.tests.test_dao import DAOTestCase

from ..pickup import Pickup
from ..pickupmember import PickupMember


class TestEnabled(unittest.TestCase):

    def test_getter_true(self):
        pickup = Pickup(commented=0)
        assert_that(pickup.enabled, equal_to(True))

    def test_getter_false(self):
        pickup = Pickup(commented=1)
        assert_that(pickup.enabled, equal_to(False))

    def test_setter_true(self):
        pickup = Pickup(enabled=True)
        assert_that(pickup.commented, equal_to(0))

    def test_setter_false(self):
        pickup = Pickup(enabled=False)
        assert_that(pickup.commented, equal_to(1))


class TestPickupmemberUserTargets(DAOTestCase):

    def test_create(self):
        target = PickupMember(category='pickup', membertype='user', memberid=0)
        pickup = self.add_pickup()

        pickup.pickupmember_user_targets = [target]
        self.session.flush()

        self.session.expire_all()
        assert_that(pickup.pickupmember_user_targets, contains(target))

    def test_dissociate(self):
        pickup = self.add_pickup()
        target1 = self.add_pickup_member(category='pickup')
        target2 = self.add_pickup_member(category='pickup')
        target3 = self.add_pickup_member(category='pickup')
        pickup.pickupmember_user_targets = [target2, target3, target1]
        self.session.flush()

        pickup.pickupmember_user_targets = []
        self.session.flush()

        self.session.expire_all()
        assert_that(pickup.pickupmember_user_targets, empty())

        row = self.session.query(PickupMember).first()
        assert_that(row, none())


class TestPickupmemberUserInterceptors(DAOTestCase):

    def test_create(self):
        interceptor = PickupMember(category='member', membertype='user', memberid=0)
        pickup = self.add_pickup()

        pickup.pickupmember_user_interceptors = [interceptor]
        self.session.flush()

        self.session.expire_all()
        assert_that(pickup.pickupmember_user_interceptors, contains(interceptor))

    def test_dissociate(self):
        pickup = self.add_pickup()
        interceptor1 = self.add_pickup_member(category='pickup')
        interceptor2 = self.add_pickup_member(category='pickup')
        interceptor3 = self.add_pickup_member(category='pickup')
        pickup.pickupmember_user_interceptors = [interceptor2, interceptor3, interceptor1]
        self.session.flush()

        pickup.pickupmember_user_interceptors = []
        self.session.flush()

        self.session.expire_all()
        assert_that(pickup.pickupmember_user_interceptors, empty())

        row = self.session.query(PickupMember).first()
        assert_that(row, none())


class TestPickupmemberGroupTargets(DAOTestCase):

    def test_create(self):
        target = PickupMember(category='pickup', membertype='group', memberid=0)
        pickup = self.add_pickup()

        pickup.pickupmember_group_targets = [target]
        self.session.flush()

        self.session.expire_all()
        assert_that(pickup.pickupmember_group_targets, contains(target))

    def test_dissociate(self):
        pickup = self.add_pickup()
        target1 = self.add_pickup_member(category='pickup')
        target2 = self.add_pickup_member(category='pickup')
        target3 = self.add_pickup_member(category='pickup')
        pickup.pickupmember_group_targets = [target2, target3, target1]
        self.session.flush()

        pickup.pickupmember_group_targets = []
        self.session.flush()

        self.session.expire_all()
        assert_that(pickup.pickupmember_group_targets, empty())

        row = self.session.query(PickupMember).first()
        assert_that(row, none())


class TestPickupmemberGroupInterceptors(DAOTestCase):

    def test_create(self):
        interceptor = PickupMember(category='member', membertype='group', memberid=0)
        pickup = self.add_pickup()

        pickup.pickupmember_group_interceptors = [interceptor]
        self.session.flush()

        self.session.expire_all()
        assert_that(pickup.pickupmember_group_interceptors, contains(interceptor))

    def test_dissociate(self):
        pickup = self.add_pickup()
        interceptor1 = self.add_pickup_member(category='member')
        interceptor2 = self.add_pickup_member(category='member')
        interceptor3 = self.add_pickup_member(category='member')
        pickup.pickupmember_group_interceptors = [interceptor2, interceptor3, interceptor1]
        self.session.flush()

        pickup.pickupmember_group_interceptors = []
        self.session.flush()

        self.session.expire_all()
        assert_that(pickup.pickupmember_group_interceptors, empty())

        row = self.session.query(PickupMember).first()
        assert_that(row, none())


class TestUserInterceptors(DAOTestCase):

    def test_get_when_group(self):
        pickup = self.add_pickup()
        group = self.add_group()
        pickup.group_interceptors = [group]
        self.session.flush()

        self.session.expire_all()
        assert_that(pickup.user_interceptors, empty())

    def test_create(self):
        pickup = self.add_pickup()
        user = self.add_user()

        pickup.user_interceptors = [user]
        self.session.flush()

        self.session.expire_all()
        assert_that(pickup.user_interceptors, contains(user))

    def test_delete(self):
        pickup = self.add_pickup()
        user = self.add_user()
        pickup.user_interceptors = [user]
        self.session.flush()

        pickup.user_interceptors = []
        self.session.flush()

        self.session.expire_all()
        assert_that(pickup.user_interceptors, empty())


class TestGroupInterceptors(DAOTestCase):

    def test_get_when_user(self):
        pickup = self.add_pickup()
        user = self.add_user()
        pickup.user_interceptors = [user]
        self.session.flush()

        self.session.expire_all()
        assert_that(pickup.group_interceptors, empty())

    def test_create(self):
        pickup = self.add_pickup()
        group = self.add_group()

        pickup.group_interceptors = [group]
        self.session.flush()

        self.session.expire_all()
        assert_that(pickup.group_interceptors, contains(group))

    def test_delete(self):
        pickup = self.add_pickup()
        group = self.add_group()
        pickup.group_interceptors = [group]
        self.session.flush()

        pickup.group_interceptors = []
        self.session.flush()

        self.session.expire_all()
        assert_that(pickup.group_interceptors, empty())


class TestUserTargets(DAOTestCase):

    def test_get_when_group(self):
        pickup = self.add_pickup()
        group = self.add_group()
        pickup.group_targets = [group]
        self.session.flush()

        self.session.expire_all()
        assert_that(pickup.user_targets, empty())

    def test_create(self):
        pickup = self.add_pickup()
        user = self.add_user()

        pickup.user_targets = [user]
        self.session.flush()

        self.session.expire_all()
        assert_that(pickup.user_targets, contains(user))

    def test_delete(self):
        pickup = self.add_pickup()
        user = self.add_user()
        pickup.user_targets = [user]
        self.session.flush()

        pickup.user_targets = []
        self.session.flush()

        self.session.expire_all()
        assert_that(pickup.user_targets, empty())


class TestGroupTargets(DAOTestCase):

    def test_get_when_user(self):
        pickup = self.add_pickup()
        user = self.add_user()
        pickup.user_targets = [user]
        self.session.flush()

        self.session.expire_all()
        assert_that(pickup.group_targets, empty())

    def test_create(self):
        pickup = self.add_pickup()
        group = self.add_group()

        pickup.group_targets = [group]
        self.session.flush()

        self.session.expire_all()
        assert_that(pickup.group_targets, contains(group))

    def test_delete(self):
        pickup = self.add_pickup()
        group = self.add_group()
        pickup.group_targets = [group]
        self.session.flush()

        pickup.group_targets = []
        self.session.flush()

        self.session.expire_all()
        assert_that(pickup.group_targets, empty())


class TestDelete(DAOTestCase):

    def test_pickupmember_group_targets_are_deleted(self):
        pickup = self.add_pickup()
        self.add_pickup_member(category='pickup', membertype='group', pickupid=pickup.id)
        self.add_pickup_member(category='pickup', membertype='group', pickupid=pickup.id)

        self.session.delete(pickup)
        self.session.flush()

        row = self.session.query(PickupMember).first()
        assert_that(row, none())

    def test_pickupmember_group_interceptors_are_deleted(self):
        pickup = self.add_pickup()
        self.add_pickup_member(category='member', membertype='group', pickupid=pickup.id)
        self.add_pickup_member(category='member', membertype='group', pickupid=pickup.id)

        self.session.delete(pickup)
        self.session.flush()

        row = self.session.query(PickupMember).first()
        assert_that(row, none())

    def test_pickupmember_queue_targets_are_deleted(self):
        pickup = self.add_pickup()
        self.add_pickup_member(category='pickup', membertype='queue', pickupid=pickup.id)
        self.add_pickup_member(category='pickup', membertype='queue', pickupid=pickup.id)

        self.session.delete(pickup)
        self.session.flush()

        row = self.session.query(PickupMember).first()
        assert_that(row, none())

    def test_pickupmember_queue_interceptors_are_deleted(self):
        pickup = self.add_pickup()
        self.add_pickup_member(category='member', membertype='queue', pickupid=pickup.id)
        self.add_pickup_member(category='member', membertype='queue', pickupid=pickup.id)

        self.session.delete(pickup)
        self.session.flush()

        row = self.session.query(PickupMember).first()
        assert_that(row, none())

    def test_pickupmember_user_targets_are_deleted(self):
        pickup = self.add_pickup()
        self.add_pickup_member(category='pickup', membertype='user', pickupid=pickup.id)
        self.add_pickup_member(category='pickup', membertype='user', pickupid=pickup.id)

        self.session.delete(pickup)
        self.session.flush()

        row = self.session.query(PickupMember).first()
        assert_that(row, none())

    def test_pickupmember_user_interceptors_are_deleted(self):
        pickup = self.add_pickup()
        self.add_pickup_member(category='member', membertype='user', pickupid=pickup.id)
        self.add_pickup_member(category='member', membertype='user', pickupid=pickup.id)

        self.session.delete(pickup)
        self.session.flush()

        row = self.session.query(PickupMember).first()
        assert_that(row, none())
