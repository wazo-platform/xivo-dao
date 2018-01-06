# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest

from hamcrest import (
    assert_that,
    equal_to,
    none,
)

from ..callfilter import Callfilter as CallFilter


class TestEnabled(unittest.TestCase):

    def test_getter_true(self):
        call_filter = CallFilter(commented=0)
        assert_that(call_filter.enabled, equal_to(True))

    def test_getter_false(self):
        call_filter = CallFilter(commented=1)
        assert_that(call_filter.enabled, equal_to(False))

    def test_setter_true(self):
        call_filter = CallFilter(enabled=True)
        assert_that(call_filter.commented, equal_to(0))

    def test_setter_false(self):
        call_filter = CallFilter(enabled=False)
        assert_that(call_filter.commented, equal_to(1))


class TestTimeout(unittest.TestCase):

    def test_getter(self):
        call_filter = CallFilter(ringseconds=10)
        assert_that(call_filter.timeout, equal_to(10))

    def test_getter_none(self):
        call_filter = CallFilter(ringseconds=0)
        assert_that(call_filter.timeout, none())

    def test_setter(self):
        call_filter = CallFilter(timeout=10)
        assert_that(call_filter.ringseconds, equal_to(10))

    def test_setter_none(self):
        call_filter = CallFilter(timeout=None)
        assert_that(call_filter.ringseconds, equal_to(0))
