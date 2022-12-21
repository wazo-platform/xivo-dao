# Copyright 2013-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import distinct
from sqlalchemy.sql.expression import or_

from xivo_dao.alchemy.stat_agent import StatAgent


def insert_missing_agents(session, confd_agents):
    confd_agents_by_name = {
        'Agent/{number}'.format(number=agent['number']): agent for agent in confd_agents
    }
    _mark_recreated_agents_with_same_number_as_deleted(session, confd_agents_by_name)
    _mark_non_confd_agents_as_deleted(session, confd_agents)
    _create_missing_agents(session, confd_agents_by_name)
    _rename_deleted_agents_with_duplicate_name(session, confd_agents_by_name)


def _mark_recreated_agents_with_same_number_as_deleted(session, confd_agents_by_name):
    db_agent_query = session.query(StatAgent).filter(StatAgent.deleted.is_(False))
    db_agents_by_name = {agent.name: agent for agent in db_agent_query.all()}

    confd_agent_names = set(list(confd_agents_by_name.keys()))
    db_agent_names = set(list(db_agents_by_name.keys()))

    not_missing_agents = confd_agent_names.intersection(db_agent_names)
    for agent_name in not_missing_agents:
        confd_agent = confd_agents_by_name[agent_name]
        db_agent = db_agents_by_name[agent_name]
        if db_agent.agent_id != confd_agent['id']:
            db_agent.deleted = True
            session.flush()


def _mark_non_confd_agents_as_deleted(session, confd_agents):
    active_agent_ids = set([agent['id'] for agent in confd_agents])
    all_agent_ids = set(r[0] for r in session.query(distinct(StatAgent.agent_id)))
    deleted_agents = [agent for agent in list(all_agent_ids - active_agent_ids) if agent]
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


def _create_missing_agents(session, confd_agents_by_name):
    new_agent_names = set(confd_agents_by_name.keys())
    db_agent_query = session.query(StatAgent).filter(StatAgent.deleted.is_(False))
    old_agent_names = set(agent.name for agent in db_agent_query.all())
    missing_agents = list(new_agent_names - old_agent_names)
    for agent_name in missing_agents:
        agent = confd_agents_by_name[agent_name]
        new_agent = StatAgent()
        new_agent.name = agent_name
        new_agent.tenant_uuid = agent['tenant_uuid']
        new_agent.agent_id = agent['id']
        new_agent.deleted = False
        session.add(new_agent)
        session.flush()


def _rename_deleted_agents_with_duplicate_name(session, confd_agents_by_name):
    db_agent_query = session.query(StatAgent).filter(StatAgent.deleted.is_(True))
    for agent in db_agent_query.all():
        if agent.name in confd_agents_by_name:
            agent.name = _find_next_available_name(session, agent.name)
            session.flush()


def _find_next_available_name(session, name):
    query = session.query(StatAgent).filter(StatAgent.name == name)
    if query.first():
        next_name = '{}_'.format(name)
        return _find_next_available_name(session, next_name)
    return name


def clean_table(session):
    session.query(StatAgent).delete()
