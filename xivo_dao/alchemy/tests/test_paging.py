# -*- coding: utf-8 -*-
#
# Copyright 2016 The Wazo Authors  (see the AUTHORS file)
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

import unittest

from hamcrest import assert_that, equal_to

from xivo_dao.alchemy.paging import Paging


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
