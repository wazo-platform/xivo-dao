# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from hamcrest import (
    assert_that,
    contains,
    equal_to,
    empty,
    has_properties,
    none,
)

from xivo_dao.tests.test_dao import DAOTestCase

from ..callerid import Callerid
from ..callfilter import Callfilter as CallFilter
from ..callfiltermember import Callfiltermember as CallFilterMember
from ..dialaction import Dialaction


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


class TestSurrogateTimeout(unittest.TestCase):

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


class TestRecipients(DAOTestCase):

    def test_create(self):
        recipient = CallFilterMember(bstype='boss', type='user')
        call_filter = self.add_call_filter()

        call_filter.recipients = [recipient]
        self.session.flush()

        self.session.expire_all()
        assert_that(call_filter.recipients, contains(recipient))

    def test_associate_order_by(self):
        call_filter = self.add_call_filter()
        recipient1 = self.add_call_filter_member(bstype='boss')
        recipient2 = self.add_call_filter_member(bstype='boss')
        recipient3 = self.add_call_filter_member(bstype='boss')

        call_filter.recipients = [recipient2, recipient3, recipient1]
        self.session.flush()

        self.session.expire_all()
        assert_that(call_filter.recipients, contains(recipient2, recipient3, recipient1))

    def test_dissociate(self):
        call_filter = self.add_call_filter()
        recipient1 = self.add_call_filter_member(bstype='boss')
        recipient2 = self.add_call_filter_member(bstype='boss')
        recipient3 = self.add_call_filter_member(bstype='boss')
        call_filter.recipients = [recipient2, recipient3, recipient1]
        self.session.flush()

        call_filter.recipients = []
        self.session.flush()

        self.session.expire_all()
        assert_that(call_filter.recipients, empty())

        row = self.session.query(CallFilterMember).first()
        assert_that(row, none())


class TestSurrogates(DAOTestCase):

    def test_create(self):
        surrogate = CallFilterMember(bstype='secretary', type='user')
        call_filter = self.add_call_filter()

        call_filter.surrogates = [surrogate]
        self.session.flush()

        self.session.expire_all()
        assert_that(call_filter.surrogates, contains(surrogate))

    def test_associate_order_by(self):
        call_filter = self.add_call_filter()
        surrogate1 = self.add_call_filter_member(bstype='secretary')
        surrogate2 = self.add_call_filter_member(bstype='secretary')
        surrogate3 = self.add_call_filter_member(bstype='secretary')

        call_filter.surrogates = [surrogate2, surrogate3, surrogate1]
        self.session.flush()

        self.session.expire_all()
        assert_that(call_filter.surrogates, contains(surrogate2, surrogate3, surrogate1))

    def test_dissociate(self):
        call_filter = self.add_call_filter()
        surrogate1 = self.add_call_filter_member(bstype='secretary')
        surrogate2 = self.add_call_filter_member(bstype='secretary')
        surrogate3 = self.add_call_filter_member(bstype='secretary')
        call_filter.surrogates = [surrogate2, surrogate3, surrogate1]
        self.session.flush()

        call_filter.surrogates = []
        self.session.flush()

        self.session.expire_all()
        assert_that(call_filter.surrogates, empty())

        row = self.session.query(CallFilterMember).first()
        assert_that(row, none())


class TestFallbacks(DAOTestCase):

    def test_getter(self):
        call_filter = self.add_call_filter()
        dialaction = self.add_dialaction(event='key', category='callfilter', categoryval=str(call_filter.id))

        assert_that(call_filter.fallbacks['key'], equal_to(dialaction))


class TestCallFilterDialactions(DAOTestCase):

    def test_getter(self):
        call_filter = self.add_call_filter()
        dialaction = self.add_dialaction(event='key', category='callfilter', categoryval=str(call_filter.id))

        assert_that(call_filter.callfilter_dialactions['key'], equal_to(dialaction))

    def test_setter(self):
        call_filter = self.add_call_filter()
        dialaction = Dialaction(event='key', category='callfilter', action='none')

        call_filter.callfilter_dialactions['key'] = dialaction
        self.session.flush()

        self.session.expire_all()
        assert_that(call_filter.callfilter_dialactions['key'], has_properties(action='none'))


class TestDelete(DAOTestCase):

    def test_caller_id_is_deleted(self):
        call_filter = self.add_call_filter()
        self.add_callerid(type='callfilter', typeval=call_filter.id)

        self.session.delete(call_filter)
        self.session.flush()

        row = self.session.query(Callerid).first()
        assert_that(row, none())

    def test_recipients_are_deleted(self):
        call_filter = self.add_call_filter()
        self.add_call_filter_member(bstype='boss', callfilterid=call_filter.id)
        self.add_call_filter_member(bstype='boss', callfilterid=call_filter.id)

        self.session.delete(call_filter)
        self.session.flush()

        row = self.session.query(CallFilterMember).first()
        assert_that(row, none())

    def test_surrogates_are_deleted(self):
        call_filter = self.add_call_filter()
        self.add_call_filter_member(bstype='secretary', callfilterid=call_filter.id)
        self.add_call_filter_member(bstype='secretary', callfilterid=call_filter.id)

        self.session.delete(call_filter)
        self.session.flush()

        row = self.session.query(CallFilterMember).first()
        assert_that(row, none())
