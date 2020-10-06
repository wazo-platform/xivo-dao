# -*- coding: utf-8 -*-
# Copyright 2013-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import distinct

from xivo_dao.alchemy.stat_agent import StatAgent


def insert_missing_agents(session, confd_agents):
    old_agents = set(r[0] for r in session.query(distinct(StatAgent.name)))
    agents_by_name = {'Agent/{number}'.format(number=agent['number']): agent for agent in confd_agents}
    configured_agents = set(agents_by_name)

    missing_agents = configured_agents - old_agents
    for agent_name in missing_agents:
        new_agent = StatAgent()
        new_agent.name = agent_name
        new_agent.tenant_uuid = agents_by_name[agent_name]['tenant_uuid']
        new_agent.agent_id = agents_by_name[agent_name]['id']
        session.add(new_agent)


def clean_table(session):
    session.query(StatAgent).delete()
