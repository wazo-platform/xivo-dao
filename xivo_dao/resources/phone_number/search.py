# Copyright 2024-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.phone_number import PhoneNumber
from xivo_dao.resources.utils.search import SearchConfig, SearchSystem

config = SearchConfig(
    table=PhoneNumber,
    columns={
        'number': PhoneNumber.number,
        'caller_id_name': PhoneNumber.caller_id_name,
        'shared': PhoneNumber.shared,
        'main': PhoneNumber.main,
    },
    default_sort='number',
)

search_system = SearchSystem(config)
