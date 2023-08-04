# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from hamcrest import assert_that, equal_to
from xivo_dao.helpers.asterisk import convert_ast_true_to_int, convert_int_to_ast_true


class TestASTTrue(unittest.TestCase):

    def test_convert_ast_true_truth_values(self):
        values = [
            'yes',
            'true',
            'y',
            't',
            '1',
            'on',
        ]

        for value in values:
            assert_that(convert_ast_true_to_int(value), equal_to(1))

    def test_convert_ast_true_false_values(self):
        values = [
            'no',
            'false',
            'n',
            'f',
            '0',
            'off',
            '',
        ]

        for value in values:
            assert_that(convert_ast_true_to_int(value), equal_to(0))

    def test_convert_int(self):
        assert_that(convert_int_to_ast_true(1), equal_to('yes'))
        assert_that(convert_int_to_ast_true(75), equal_to('yes'))
        assert_that(convert_int_to_ast_true(0), equal_to('no'))
