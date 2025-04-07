# Copyright 2018-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.queueskill import QueueSkill
from xivo_dao.resources.utils.search import SearchConfig, SearchSystem

config = SearchConfig(
    table=QueueSkill,
    columns={
        'id': QueueSkill.id,
        'name': QueueSkill.name,
        'description': QueueSkill.description,
    },
    default_sort='name',
)

skill_search = SearchSystem(config)
