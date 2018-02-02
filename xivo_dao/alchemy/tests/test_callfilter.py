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


class TestStrategy(unittest.TestCase):

    def test_getter_all_recipients_then_linear_surrogates(self):
        call_filter = CallFilter(bosssecretary='bossfirst-serial')
        assert_that(call_filter.strategy, equal_to('all-recipients-then-linear-surrogates'))

    def test_getter_all_recipients_then_all_surrogates(self):
        call_filter = CallFilter(bosssecretary='bossfirst-simult')
        assert_that(call_filter.strategy, equal_to('all-recipients-then-all-surrogates'))

    def test_getter_linear_surrogates_then_all_recipients(self):
        call_filter = CallFilter(bosssecretary='secretary-serial')
        assert_that(call_filter.strategy, equal_to('linear-surrogates-then-all-recipients'))

    def test_getter_all_surrogates_then_all_recipients(self):
        call_filter = CallFilter(bosssecretary='secretary-simult')
        assert_that(call_filter.strategy, equal_to('all-surrogates-then-all-recipients'))

    def test_getter_all(self):
        call_filter = CallFilter(bosssecretary='all')
        assert_that(call_filter.strategy, equal_to('all'))

    def test_setter_all_recipients_then_linear_surrogates(self):
        call_filter = CallFilter(strategy='all-recipients-then-linear-surrogates')
        assert_that(call_filter.bosssecretary, equal_to('bossfirst-serial'))

    def test_setter_all_recipients_then_all_surrogates(self):
        call_filter = CallFilter(strategy='all-recipients-then-all-surrogates')
        assert_that(call_filter.bosssecretary, equal_to('bossfirst-simult'))

    def test_setter_linear_surrogates_then_all_recipients(self):
        call_filter = CallFilter(strategy='linear-surrogates-then-all-recipients')
        assert_that(call_filter.bosssecretary, equal_to('secretary-serial'))

    def test_setter_all_surrogates_then_all_recipients(self):
        call_filter = CallFilter(strategy='all-surrogates-then-all-recipients')
        assert_that(call_filter.bosssecretary, equal_to('secretary-simult'))

    def test_setter_all(self):
        call_filter = CallFilter(strategy='all')
        assert_that(call_filter.bosssecretary, equal_to('all'))


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
        assert_that(call_filter.surrogates_timeout, equal_to(10))

    def test_getter_none(self):
        call_filter = CallFilter(ringseconds=0)
        assert_that(call_filter.surrogates_timeout, none())

    def test_setter(self):
        call_filter = CallFilter(surrogates_timeout=10)
        assert_that(call_filter.ringseconds, equal_to(10))

    def test_setter_none(self):
        call_filter = CallFilter(surrogates_timeout=None)
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
