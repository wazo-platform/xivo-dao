# -*- coding: utf-8 -*-
# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import


def utcnow_with_tzinfo():
    from datetime import datetime
    try:
        from datetime import timezone
        return datetime.now(timezone.utc)
    except ImportError:
        # NOTE: Python2 this is unused anyway
        return datetime.now()