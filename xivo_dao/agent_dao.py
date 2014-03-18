# -*- coding: utf-8 -*-

# Copyright (C) 2007-2014 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from collections import namedtuple
from sqlalchemy.sql import select, and_
from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_dao.helpers.db_manager import daosession


_Agent = namedtuple('_Agent', ['id', 'number', 'queues'])
_Queue = namedtuple('_Queue', ['id', 'name', 'penalty'])


@daosession
def agent_number(session, agentid):
    return _get_one(session, agentid).number


@daosession
def agent_context(session, agentid):
    return _get_one(session, agentid).context


@daosession
def agent_interface(session, agentid):
    try:
        return 'Agent/%s' % _get_one(session, agentid).number
    except LookupError:
        return None


@daosession
def agent_id(session, agent_number):
    if agent_number is None:
        raise ValueError('Agent number is None')
    result = session.query(AgentFeatures.id).filter(AgentFeatures.number == agent_number).first()
    if result is None:
        raise LookupError('No such agent')
    return str(result.id)


def _get_one(session, agentid):
    # field id != field agentid used only for joining with staticagent table.
    if agentid is None:
        raise ValueError('Agent ID is None')
    result = session.query(AgentFeatures).filter(AgentFeatures.id == int(agentid)).first()
    if result is None:
        raise LookupError('No such agent')
    return result


@daosession
def add_agent(session, agent_features):
    if type(agent_features) != AgentFeatures:
        raise ValueError('Wrong object passed')

    session.begin()
    session.add(agent_features)
    session.commit()

    return agent_features.id


@daosession
def del_agent(session, agentid):
    if agentid is None:
        raise ValueError('Agent ID is None')
    try:
        session.begin()
        session.query(AgentFeatures)\
            .filter(AgentFeatures.id == agentid)\
            .delete()
        session.commit()
    except Exception as e:
        session.rollback()
        raise e


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
                   and_(QueueMember.usertype == u'agent',
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
