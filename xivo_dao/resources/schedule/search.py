# Copyright 2017-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.schedule import Schedule
from xivo_dao.resources.utils.search import SearchSystem
from xivo_dao.resources.utils.search import SearchConfig


config = SearchConfig(
    table=Schedule,
    columns={'id': Schedule.id, 'name': Schedule.name, 'timezone': Schedule.timezone},
    default_sort='name',
)

schedule_search = SearchSystem(config)
