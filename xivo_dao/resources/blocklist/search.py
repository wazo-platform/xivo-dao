# Copyright 2024-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.blocklist import BlocklistNumber
from xivo_dao.resources.utils.search import SearchSystem, SearchConfig


config = SearchConfig(
    table=BlocklistNumber,
    columns={
        'number': BlocklistNumber.number,
        'label': BlocklistNumber.label,
        'user_uuid': BlocklistNumber.user_uuid,
    },
    default_sort='number',
)

search_system = SearchSystem(config)
