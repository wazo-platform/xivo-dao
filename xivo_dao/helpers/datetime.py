# Copyright 2022-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import datetime, timezone


def utcnow_with_tzinfo() -> datetime:
    return datetime.now(timezone.utc)
