# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


import unittest

from hamcrest import assert_that, equal_to

from xivo_dao.alchemy.contextnumbers import ContextNumbers


class TestContextNumbers(unittest.TestCase):

    def test_in_range(self):
        context_numbers = ContextNumbers(context='toto',
                                         type='incall',
                                         start='1000',
                                         end='1999',
                                         did_length=0)

        assert_that(context_numbers.in_range('1500'))

    def test_in_range_when_outside(self):
        context_numbers = ContextNumbers(context='toto',
                                         type='incall',
                                         start='1000',
                                         end='1999',
                                         did_length=0)

        assert_that(context_numbers.in_range('2000'), equal_to(False))

    def test_in_range_with_no_end(self):
        context_numbers = ContextNumbers(context='toto',
                                         type='incall',
                                         start='1000',
                                         numberend='',
                                         did_length=0)

        assert_that(context_numbers.in_range('1000'))

    def test_in_range_with_no_end_when_outside(self):
        context_numbers = ContextNumbers(context='toto',
                                         type='incall',
                                         start='1000',
                                         numberend='',
                                         did_length=0)

        assert_that(context_numbers.in_range('1001'), equal_to(False))

    def test_in_range_when_negative(self):
        context_numbers = ContextNumbers(context='toto',
                                         type='incall',
                                         start='1000',
                                         end='1999',
                                         did_length=0)

        assert_that(context_numbers.in_range('-1500'), equal_to(False))
