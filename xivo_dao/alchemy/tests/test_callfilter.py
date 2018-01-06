# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest

from hamcrest import (
    assert_that,
    equal_to,
    has_properties,
    none,
)

from xivo_dao.tests.test_dao import DAOTestCase

from ..callfilter import Callfilter as CallFilter
from ..callerid import Callerid


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


class TestCallerIdMode(DAOTestCase):

    def test_getter(self):
        call_filter = self.add_call_filter(caller_id_mode='prepend')
        assert_that(call_filter.caller_id_mode, equal_to('prepend'))

    def test_creator(self):
        call_filter = self.add_call_filter()

        call_filter.caller_id_mode = 'prepend'
        self.session.flush()

        self.session.expire_all()
        assert_that(call_filter.caller_id, has_properties(
            type='callfilter',
            typeval=call_filter.id,
            mode='prepend',
            name=None,
        ))


class TestCallerIdName(DAOTestCase):

    def test_getter(self):
        call_filter = self.add_call_filter(caller_id_name='toto')
        assert_that(call_filter.caller_id_name, equal_to('toto'))

    def test_creator(self):
        call_filter = self.add_call_filter()

        call_filter.caller_id_name = 'toto'
        self.session.flush()

        self.session.expire_all()
        assert_that(call_filter.caller_id, has_properties(
            type='callfilter',
            typeval=call_filter.id,
            mode=None,
            name='toto',
        ))


class TestDelete(DAOTestCase):

    def test_caller_id_is_deleted(self):
        call_filter = self.add_call_filter()
        self.add_callerid(type='callfilter', typeval=call_filter.id)

        self.session.delete(call_filter)
        self.session.flush()

        row = self.session.query(Callerid).first()
        assert_that(row, none())
