# -*- coding: utf-8 -*-

# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

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
