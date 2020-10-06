# -*- coding: utf-8 -*-
# Copyright 2013-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import distinct

from xivo_dao.helpers.db_manager import daosession
from xivo_dao.alchemy.stat_agent import StatAgent


def insert_missing_agents(session, confd_agents):
    old_agents = set(r[0] for r in session.query(distinct(StatAgent.name)))
    agent_tenants = {'Agent/{number}'.format(number=agent['number']): agent['tenant_uuid'] for agent in confd_agents}
    configured_agents = set(agent_tenants)

    missing_agents = configured_agents - old_agents
    for agent_name in missing_agents:
        new_agent = StatAgent()
        new_agent.name = agent_name
        new_agent.tenant_uuid = agent_tenants[agent_name]
        session.add(new_agent)


@daosession
def id_from_name(session, agent_name):
    return session.query(StatAgent.id).filter(StatAgent.name == agent_name).first().id


def clean_table(session):
    session.query(StatAgent).delete()
