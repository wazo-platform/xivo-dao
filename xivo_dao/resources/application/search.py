# Copyright 2018-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.application import Application
from xivo_dao.resources.utils.search import SearchConfig, SearchSystem

config = SearchConfig(
    table=Application,
    columns={
        'uuid': Application.uuid,
        'name': Application.name,
    },
    default_sort='uuid',
)

application_search = SearchSystem(config)
