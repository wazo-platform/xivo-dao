# -*- coding: utf-8 -*-

# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+

from __future__ import absolute_import

from uuid import uuid4


def new_uuid():
    return str(uuid4())
