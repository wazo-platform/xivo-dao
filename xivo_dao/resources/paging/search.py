# Copyright 2016-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.paging import Paging
from xivo_dao.resources.utils.search import SearchSystem
from xivo_dao.resources.utils.search import SearchConfig


config = SearchConfig(
    table=Paging,
    columns={
        'id': Paging.id,
        'name': Paging.name,
        'number': Paging.number,
        'announce_sound': Paging.announce_sound,
    },
    default_sort='name',
)

paging_search = SearchSystem(config)
