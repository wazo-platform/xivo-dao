# -*- coding: utf-8 -*-
# Copyright 2007-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import unicode_literals

from collections import namedtuple
from sqlalchemy.sql import select, and_
from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_dao.helpers.db_manager import daosession


_Agent = namedtuple('_Agent', ['id', 'number', 'queues'])
_Queue = namedtuple('_Queue', ['id', 'name', 'penalty'])


@daosession
def find_agent_interface(session, agentid):
    try:
        return 'Agent/%s' % _get_one(session, agentid).number
    except LookupError:
        return None


def _get_one(session, agentid):
    # field id != field agentid used only for joining with staticagent table.
    if agentid is None:
        raise ValueError('Agent ID is None')
    result = session.query(AgentFeatures).filter(AgentFeatures.id == int(agentid)).first()
    if result is None:
        raise LookupError('No such agent')
    return result


@daosession
def agent_with_id(session, agent_id):
    agent = _get_agent(session, AgentFeatures.id == int(agent_id))
    _add_queues_to_agent(session, agent)
    return agent


@daosession
def agent_with_number(session, agent_number):
    agent = _get_agent(session, AgentFeatures.number == agent_number)
    _add_queues_to_agent(session, agent)
    return agent


def _get_agent(session, whereclause):
    query = select([AgentFeatures.id, AgentFeatures.number], whereclause)
    row = session.execute(query).first()
    if row is None:
        raise LookupError('no agent matching clause %s' % whereclause)
    return _Agent(row['id'], row['number'], [])


def _add_queues_to_agent(session, agent):
    query = select([QueueFeatures.id, QueueMember.queue_name, QueueMember.penalty],
                   and_(QueueMember.usertype == 'agent',
                        QueueMember.userid == agent.id,
                        QueueMember.queue_name == QueueFeatures.name))

    for row in session.execute(query):
        queue = _Queue(row['id'], row['queue_name'], row['penalty'])
        agent.queues.append(queue)


@daosession
def get(session, agentid):
    return session.query(AgentFeatures).filter(AgentFeatures.id == int(agentid)).first()


@daosession
def all(session):
    return session.query(AgentFeatures).all()
