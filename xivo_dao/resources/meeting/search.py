# Copyright 2021-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.meeting import Meeting
from xivo_dao.resources.utils.search import SearchConfig, SearchSystem

config = SearchConfig(
    table=Meeting,
    columns={
        'name': Meeting.name,
        'persistent': Meeting.persistent,
        'require_authorization': Meeting.require_authorization,
        'creation_time': Meeting.created_at,
    },
    search=['name'],
    default_sort='name',
)

meeting_search = SearchSystem(config)
