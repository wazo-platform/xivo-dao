# -*- coding: utf-8 -*-

# Copyright (C) 2016 Proformatique Inc.
#
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import (assert_that,
                      equal_to)

from xivo_dao.tests.test_dao import DAOTestCase


class TestName(DAOTestCase):

    def test_getter(self):
        callerid = self.add_callerid(callerdisplay='Bob')

        assert_that(callerid.name, equal_to('Bob'))

    def test_getter_when_empty_string(self):
        callerid = self.add_callerid(callerdisplay='')

        assert_that(callerid.name, equal_to(None))

    def test_setter(self):
        callerid = self.add_callerid(callerdisplay='')
        callerid.name = 'Bob'

        assert_that(callerid.callerdisplay, equal_to('Bob'))

    def test_setter_to_none(self):
        callerid = self.add_callerid(callerdisplay='Bob')
        callerid.name = None

        assert_that(callerid.callerdisplay, equal_to(''))
