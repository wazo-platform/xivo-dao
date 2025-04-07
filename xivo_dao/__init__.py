# Copyright 2013-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_manager import default_config, init_db, init_db_from_config

__all__ = [
    'init_db',
    'init_db_from_config',
    'default_config',
]
