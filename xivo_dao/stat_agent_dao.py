# Copyright 2013-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from collections import namedtuple

from sqlalchemy import distinct
from sqlalchemy.sql.expression import or_

from xivo_dao.alchemy.stat_agent import StatAgent

AgentKey = namedtuple('AgentKey', ['name', 'tenant_uuid'])


def insert_missing_agents(session, confd_agents):
    confd_agents_by_key = {
        AgentKey(f'Agent/{agent["number"]}', agent['tenant_uuid']): agent
        for agent in confd_agents
    }
    _mark_recreated_agents_with_same_number_as_deleted(session, confd_agents_by_key)
    _mark_non_confd_agents_as_deleted(session, confd_agents_by_key)
    _create_missing_agents(session, confd_agents_by_key)
    _rename_deleted_agents_with_duplicate_name(session, confd_agents_by_key)


def _mark_recreated_agents_with_same_number_as_deleted(session, confd_agents_by_key):
    db_agent_query = session.query(StatAgent).filter(StatAgent.deleted.is_(False))
    db_agents_by_name = {
        AgentKey(agent.name, agent.tenant_uuid): agent for agent in db_agent_query.all()
    }

    existing_in_confd = set(list(confd_agents_by_key.keys()))
    existing_in_stat_agent = set(list(db_agents_by_name.keys()))

    not_missing_agents = existing_in_confd.intersection(existing_in_stat_agent)
    for agent_key in not_missing_agents:
        confd_agent = confd_agents_by_key[agent_key]
        db_agent = db_agents_by_name[agent_key]
        if db_agent.agent_id != confd_agent['id']:
            db_agent.deleted = True
            session.flush()


def _mark_non_confd_agents_as_deleted(session, confd_agents_by_key):
    active_agent_ids = {agent['id'] for agent in confd_agents_by_key.values()}
    all_agent_ids = {r[0] for r in session.query(distinct(StatAgent.agent_id))}
    deleted_agents = [
        agent for agent in list(all_agent_ids - active_agent_ids) if agent
    ]
    (
        session.query(StatAgent)
        .filter(
            or_(
                StatAgent.agent_id.in_(deleted_agents),
                StatAgent.agent_id.is_(None),
            )
        )
        .update({'deleted': True}, synchronize_session=False)
    )
    session.flush()


def _create_missing_agents(session, confd_agents_by_key):
    new_agent_keys = set(confd_agents_by_key.keys())
    db_agent_query = session.query(StatAgent).filter(StatAgent.deleted.is_(False))
    old_agent_keys = {
        AgentKey(agent.name, agent.tenant_uuid) for agent in db_agent_query.all()
    }
    missing_agents = list(new_agent_keys - old_agent_keys)
    for agent_key in missing_agents:
        agent = confd_agents_by_key[agent_key]
        new_agent = StatAgent()
        new_agent.name = agent_key.name
        new_agent.tenant_uuid = agent['tenant_uuid']
        new_agent.agent_id = agent['id']
        new_agent.deleted = False
        session.add(new_agent)
        session.flush()


def _rename_deleted_agents_with_duplicate_name(session, confd_agents_by_key):
    db_agent_query = session.query(StatAgent).filter(StatAgent.deleted.is_(True))
    for agent in db_agent_query.all():
        if AgentKey(agent.name, agent.tenant_uuid) in confd_agents_by_key:
            agent.name = _find_next_available_name(
                session, agent.name, agent.tenant_uuid
            )
            session.flush()


def _find_next_available_name(session, name, tenant_uuid):
    query = session.query(StatAgent).filter(
        StatAgent.name == name,
        StatAgent.tenant_uuid == tenant_uuid,
    )
    if query.first():
        next_name = f'{name}_'
        return _find_next_available_name(session, next_name, tenant_uuid)
    return name


def clean_table(session):
    session.query(StatAgent).delete()
