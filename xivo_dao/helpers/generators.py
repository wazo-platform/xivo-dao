# -*- coding: utf-8 -*-

# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+

import string
import random
import six

ALPHANUMERIC_POOL = string.ascii_lowercase + string.digits


def find_unused_hash(already_exists_predicate):
    while True:
        data = generate_hash()
        if not already_exists_predicate(data):
            return data


def generate_hash(length=8):
    return ''.join(random.choice(ALPHANUMERIC_POOL) for _ in six.moves.range(length))
