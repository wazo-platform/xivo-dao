# -*- coding: utf-8 -*-
# Copyright 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

# taken from the definition of the "ast_true" function in Asterisk source code
_TRUTH_VALUES = [
    'yes',
    'true',
    'y',
    't',
    '1',
    'on',
]


def convert_ast_true_to_int(value):
    return int(value in _TRUTH_VALUES)


def convert_int_to_ast_true(value):
    if value:
        return 'yes'
    return 'no'
