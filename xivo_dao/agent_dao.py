# -*- coding: utf-8 -*-
# Copyright 2007-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import unicode_literals

from collections import namedtuple
from sqlalchemy.sql import select, and_
from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_dao.helpers.db_manager import daosession


_Agent = namedtuple('_Agent', ['id', 'tenant_uuid', 'number', 'queues'])
_Queue = namedtuple('_Queue', ['id', 'tenant_uuid', 'name', 'penalty'])


@daosession
def find_agent_interface(session, agentid, tenant_uuids=None):
    try:
        return 'Agent/%s' % _get_one(session, agentid, tenant_uuids).number
    except LookupError:
        return None


def _get_one(session, agentid, tenant_uuids=None):
    # field id != field agentid used only for joining with staticagent table.
    if agentid is None:
        raise ValueError('Agent ID is None')
    query = session.query(AgentFeatures).filter(AgentFeatures.id == int(agentid))
    if tenant_uuids is not None:
        query = query.filter(AgentFeatures.tenant_uuid.in_(tenant_uuids))

    result = query.first()
    if result is None:
        raise LookupError('No such agent')
    return result


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


def _get_agent(session, whereclause, tenant_uuids=None):
    query = session.query(AgentFeatures).filter(whereclause)
    if tenant_uuids is not None:
        query = query.filter(AgentFeatures.tenant_uuid.in_(tenant_uuids))
    agent = query.first()
    if agent is None:
        raise LookupError('no agent matching clause %s' % whereclause)
    return _Agent(agent.id, agent.tenant_uuid, agent.number, [])


def _add_queues_to_agent(session, agent):
    query = select([QueueFeatures.id, QueueFeatures.tenant_uuid, QueueMember.queue_name, QueueMember.penalty],
                   and_(QueueMember.usertype == 'agent',
                        QueueMember.userid == agent.id,
                        QueueMember.queue_name == QueueFeatures.name))

    for row in session.execute(query):
        queue = _Queue(row['id'], row['tenant_uuid'], row['queue_name'], row['penalty'])
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
