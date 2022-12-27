# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.context import Context
from xivo_dao.resources.utils.search import SearchSystem, SearchConfig


config = SearchConfig(
    table=Context,
    columns={
        'id': Context.id,
        'description': Context.description,
        'name': Context.name,
        'label': Context.label,
        'type': Context.type,
    },
    default_sort='id',
)

context_search = SearchSystem(config)
