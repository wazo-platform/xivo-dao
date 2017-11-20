# -*- coding: UTF-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_dao.helpers.db_manager import daosession


@daosession
def exists(session, agent_id):
    query = (session.query(AgentFeatures)
             .filter(AgentFeatures.id == agent_id)
             )

    return query.count() > 0
