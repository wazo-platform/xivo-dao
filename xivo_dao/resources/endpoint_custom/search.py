# Copyright 2015-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.usercustom import UserCustom
from xivo_dao.resources.utils.search import SearchConfig, SearchSystem

config = SearchConfig(
    table=UserCustom,
    columns={
        'id': UserCustom.id,
        'interface': UserCustom.interface,
        'context': UserCustom.context,
    },
    default_sort='interface',
)

custom_search = SearchSystem(config)
