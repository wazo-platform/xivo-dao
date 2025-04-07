# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from hamcrest import (
    assert_that,
    contains_exactly,
    contains_inanyorder,
    empty,
    equal_to,
    none,
    not_,
)

from xivo_dao.alchemy.func_key_dest_paging import FuncKeyDestPaging
from xivo_dao.alchemy.paging import Paging
from xivo_dao.alchemy.paginguser import PagingUser
from xivo_dao.alchemy.userfeatures import UserFeatures as User
from xivo_dao.resources.func_key.tests.test_helpers import FuncKeyHelper
from xivo_dao.tests.test_dao import DAOTestCase


class TestUsersMember(DAOTestCase):
    def test_getter(self):
        paging = self.add_paging()
        user = self.add_user()
        self.add_paging_user(user_id=user.id, paging_id=paging.id, caller=0)

        row = self.session.query(Paging).filter_by(id=paging.id).first()
        assert_that(row, equal_to(paging))
        assert_that(row.users_member, contains_exactly(user))

    def test_setter(self):
        paging = self.add_paging()
        user1 = self.add_user()
        user2 = self.add_user()
        paging.users_member = [user1, user2]

        row = self.session.query(Paging).filter_by(id=paging.id).first()
        assert_that(row, equal_to(paging))

        self.session.expire_all()
        assert_that(row.users_member, contains_inanyorder(user1, user2))

    def test_deleter(self):
        paging = self.add_paging()
        user1 = self.add_user()
        user2 = self.add_user()
        paging.users_member = [user1, user2]
        self.session.flush()

        paging.users_member = []

        row = self.session.query(Paging).filter_by(id=paging.id).first()
        assert_that(row, equal_to(paging))
        assert_that(row.users_member, empty())

        row = self.session.query(User).first()
        assert_that(row, not_(none()))

        row = self.session.query(PagingUser).first()
        assert_that(row, none())


class TestUsersCaller(DAOTestCase):
    def test_getter(self):
        paging = self.add_paging()
        user = self.add_user()
        self.add_paging_user(user_id=user.id, paging_id=paging.id, caller=1)

        row = self.session.query(Paging).filter_by(id=paging.id).first()
        assert_that(row, equal_to(paging))
        assert_that(row.users_caller, contains_exactly(user))

    def test_setter(self):
        paging = self.add_paging()
        user1 = self.add_user()
        user2 = self.add_user()
        paging.users_caller = [user1, user2]

        row = self.session.query(Paging).filter_by(id=paging.id).first()
        assert_that(row, equal_to(paging))

        self.session.expire_all()
        assert_that(row.users_caller, contains_inanyorder(user1, user2))

    def test_deleter(self):
        paging = self.add_paging()
        user1 = self.add_user()
        user2 = self.add_user()
        paging.users_caller = [user1, user2]
        self.session.flush()

        paging.users_caller = []

        row = self.session.query(Paging).filter_by(id=paging.id).first()
        assert_that(row, equal_to(paging))
        assert_that(row.users_caller, empty())

        row = self.session.query(User).first()
        assert_that(row, not_(none()))

        row = self.session.query(PagingUser).first()
        assert_that(row, none())


class TestEnabled(unittest.TestCase):
    def test_getter_true(self):
        paging = Paging(commented=0)
        assert_that(paging.enabled, equal_to(True))

    def test_getter_false(self):
        paging = Paging(commented=1)
        assert_that(paging.enabled, equal_to(False))

    def test_setter_true(self):
        paging = Paging(enabled=True)
        assert_that(paging.commented, equal_to(0))

    def test_setter_false(self):
        paging = Paging(enabled=False)
        assert_that(paging.commented, equal_to(1))


class TestDuplexBool(unittest.TestCase):
    def test_getter_true(self):
        paging = Paging(duplex=1)
        assert_that(paging.duplex_bool, equal_to(True))

    def test_getter_false(self):
        paging = Paging(duplex=0)
        assert_that(paging.duplex_bool, equal_to(False))

    def test_setter_true(self):
        paging = Paging(duplex_bool=True)
        assert_that(paging.duplex, equal_to(1))

    def test_setter_false(self):
        paging = Paging(duplex_bool=False)
        assert_that(paging.duplex, equal_to(0))


class TestRecordBool(unittest.TestCase):
    def test_getter_true(self):
        paging = Paging(record=1)
        assert_that(paging.record_bool, equal_to(True))

    def test_getter_false(self):
        paging = Paging(record=0)
        assert_that(paging.record_bool, equal_to(False))

    def test_setter_true(self):
        paging = Paging(record_bool=True)
        assert_that(paging.record, equal_to(1))

    def test_setter_false(self):
        paging = Paging(record_bool=False)
        assert_that(paging.record, equal_to(0))


class TestIgnoreForward(unittest.TestCase):
    def test_getter_true(self):
        paging = Paging(ignore=1)
        assert_that(paging.ignore_forward, equal_to(True))

    def test_getter_false(self):
        paging = Paging(ignore=0)
        assert_that(paging.ignore_forward, equal_to(False))

    def test_setter_true(self):
        paging = Paging(ignore_forward=True)
        assert_that(paging.ignore, equal_to(1))

    def test_setter_false(self):
        paging = Paging(ignore_forward=False)
        assert_that(paging.ignore, equal_to(0))


class TestCallerNotification(unittest.TestCase):
    def test_getter_true(self):
        paging = Paging(quiet=0)
        assert_that(paging.caller_notification, equal_to(True))

    def test_getter_false(self):
        paging = Paging(quiet=1)
        assert_that(paging.caller_notification, equal_to(False))

    def test_setter_true(self):
        paging = Paging(caller_notification=True)
        assert_that(paging.quiet, equal_to(0))

    def test_setter_false(self):
        paging = Paging(caller_notification=False)
        assert_that(paging.quiet, equal_to(1))


class TestAnnounceCaller(unittest.TestCase):
    def test_getter_true(self):
        paging = Paging(announcement_caller=0)
        assert_that(paging.announce_caller, equal_to(True))

    def test_getter_false(self):
        paging = Paging(announcement_caller=1)
        assert_that(paging.announce_caller, equal_to(False))

    def test_setter_true(self):
        paging = Paging(announce_caller=True)
        assert_that(paging.announcement_caller, equal_to(0))

    def test_setter_false(self):
        paging = Paging(announce_caller=False)
        assert_that(paging.announcement_caller, equal_to(1))


class TestAnnounceSound(unittest.TestCase):
    def test_getter(self):
        paging = Paging(announcement_file='beep')
        assert_that(paging.announce_sound, equal_to('beep'))

    def test_setter(self):
        paging = Paging(announce_sound='beep')
        assert_that(paging.announcement_play, equal_to(1))
        assert_that(paging.announcement_file, equal_to('beep'))

    def test_setter_none(self):
        paging = Paging(announce_sound=None)
        assert_that(paging.announcement_play, equal_to(0))
        assert_that(paging.announcement_file, equal_to(None))


class TestDelete(DAOTestCase, FuncKeyHelper):
    def setUp(self):
        super().setUp()
        self.setup_funckeys()

    def test_funckeys_are_deleted(self):
        paging = self.add_paging()
        self.add_paging_destination(paging.id)

        self.session.delete(paging)
        self.session.flush()

        row = self.session.query(FuncKeyDestPaging).first()
        assert_that(row, none())
