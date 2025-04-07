# Copyright 2018-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.agentfeatures import AgentFeatures as Agent
from xivo_dao.resources.utils.search import SearchConfig, SearchSystem

config = SearchConfig(
    table=Agent,
    columns={
        'id': Agent.id,
        'firstname': Agent.firstname,
        'lastname': Agent.lastname,
        'number': Agent.number,
        'preprocess_subroutine': Agent.preprocess_subroutine,
    },
    default_sort='id',
)

agent_search = SearchSystem(config)
