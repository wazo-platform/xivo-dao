# Copyright 2007-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import NamedTuple

from sqlalchemy.sql import and_, select

from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.helpers.db_manager import daosession


class _Agent(NamedTuple):
    id: int
    tenant_uuid: str
    number: str
    queues: list[QueueFeatures]
    user_ids: list[int]


class _Queue(NamedTuple):
    id: int
    tenant_uuid: str
    name: str
    penalty: int
    label: str


@daosession
def agent_with_id(session, agent_id, tenant_uuids=None):
    agent = _get_agent(session, AgentFeatures.id == int(agent_id), tenant_uuids)
    _add_queues_to_agent(session, agent)
    return agent


@daosession
def agent_with_number(session, agent_number, tenant_uuids=None):
    agent = _get_agent(session, AgentFeatures.number == agent_number, tenant_uuids)
    _add_queues_to_agent(session, agent)
    return agent


@daosession
def agent_with_user_uuid(session, user_uuid, tenant_uuids=None):
    query = (
        session.query(AgentFeatures)
        .join(UserFeatures, AgentFeatures.id == UserFeatures.agentid)
        .filter(UserFeatures.uuid == user_uuid)
    )
    if tenant_uuids is not None:
        query = query.filter(AgentFeatures.tenant_uuid.in_(tenant_uuids))

    agent_row = query.first()
    if agent_row is None:
        raise LookupError(f'no agent found for user {user_uuid}')
    agent = _Agent(
        agent_row.id,
        agent_row.tenant_uuid,
        agent_row.number,
        [],
        [user.id for user in agent_row.users],
    )
    _add_queues_to_agent(session, agent)
    return agent


def _get_agent(session, whereclause, tenant_uuids=None):
    query = session.query(AgentFeatures).filter(whereclause)
    if tenant_uuids is not None:
        query = query.filter(AgentFeatures.tenant_uuid.in_(tenant_uuids))
    agent = query.first()
    if agent is None:
        raise LookupError(f'no agent matching clause {whereclause.compile().params}')
    return _Agent(
        agent.id, agent.tenant_uuid, agent.number, [], [user.id for user in agent.users]
    )


def _add_queues_to_agent(session, agent):
    query = select(
        [
            QueueFeatures.id,
            QueueFeatures.tenant_uuid,
            QueueFeatures.displayname,
            QueueMember.queue_name,
            QueueMember.penalty,
        ],
        and_(
            QueueMember.usertype == 'agent',
            QueueMember.userid == agent.id,
            QueueMember.queue_name == QueueFeatures.name,
        ),
    )

    for row in session.execute(query):
        queue = _Queue(
            row['id'],
            row['tenant_uuid'],
            row['queue_name'],
            row['penalty'],
            row['displayname'],
        )
        agent.queues.append(queue)


@daosession
def get(session, agentid, tenant_uuids=None):
    query = session.query(AgentFeatures).filter(AgentFeatures.id == int(agentid))
    if tenant_uuids is not None:
        query = query.filter(AgentFeatures.tenant_uuid.in_(tenant_uuids))
    return query.first()


@daosession
def all(session, tenant_uuids=None):
    query = session.query(AgentFeatures)
    if tenant_uuids is not None:
        query = query.filter(AgentFeatures.tenant_uuid.in_(tenant_uuids))
    return query.all()
