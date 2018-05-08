# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

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


class TestTargets(DAOTestCase):

    def test_create(self):
        target = PickupMember(category='member', membertype='user', memberid=0)
        pickup = self.add_pickup()

        pickup.targets = [target]
        self.session.flush()

        self.session.expire_all()
        assert_that(pickup.targets, contains(target))

    def test_dissociate(self):
        pickup = self.add_pickup()
        target1 = self.add_pickup_member(category='member')
        target2 = self.add_pickup_member(category='member')
        target3 = self.add_pickup_member(category='member')
        pickup.targets = [target2, target3, target1]
        self.session.flush()

        pickup.targets = []
        self.session.flush()

        self.session.expire_all()
        assert_that(pickup.targets, empty())

        row = self.session.query(PickupMember).first()
        assert_that(row, none())


class TestInterceptors(DAOTestCase):

    def test_create(self):
        interceptor = PickupMember(category='pickup', membertype='user', memberid=0)
        pickup = self.add_pickup()

        pickup.interceptors = [interceptor]
        self.session.flush()

        self.session.expire_all()
        assert_that(pickup.interceptors, contains(interceptor))

    def test_dissociate(self):
        pickup = self.add_pickup()
        interceptor1 = self.add_pickup_member(category='pickup')
        interceptor2 = self.add_pickup_member(category='pickup')
        interceptor3 = self.add_pickup_member(category='pickup')
        pickup.interceptors = [interceptor2, interceptor3, interceptor1]
        self.session.flush()

        pickup.interceptors = []
        self.session.flush()

        self.session.expire_all()
        assert_that(pickup.interceptors, empty())

        row = self.session.query(PickupMember).first()
        assert_that(row, none())


class TestDelete(DAOTestCase):

    def test_targets_are_deleted(self):
        pickup = self.add_pickup()
        self.add_pickup_member(category='member', pickupid=pickup.id)
        self.add_pickup_member(category='member', pickupid=pickup.id)

        self.session.delete(pickup)
        self.session.flush()

        row = self.session.query(PickupMember).first()
        assert_that(row, none())

    def test_interceptors_are_deleted(self):
        pickup = self.add_pickup()
        self.add_pickup_member(category='pickup', pickupid=pickup.id)
        self.add_pickup_member(category='pickup', pickupid=pickup.id)

        self.session.delete(pickup)
        self.session.flush()

        row = self.session.query(PickupMember).first()
        assert_that(row, none())
