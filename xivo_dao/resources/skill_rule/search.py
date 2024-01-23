# Copyright 2018-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.queueskillrule import QueueSkillRule
from xivo_dao.resources.utils.search import SearchSystem
from xivo_dao.resources.utils.search import SearchConfig


config = SearchConfig(
    table=QueueSkillRule,
    columns={
        'id': QueueSkillRule.id,
        'name': QueueSkillRule.name,
    },
    default_sort='name',
)

skill_rule_search = SearchSystem(config)
