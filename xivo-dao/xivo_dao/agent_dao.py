# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 Avencall
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
from xivo_dao.helpers.db_manager import DbSession


_Agent = namedtuple('_Agent', ['id', 'number', 'queues'])
_Queue = namedtuple('_Queue', ['id', 'name', 'penalty', 'skills'])


def agent_number(agentid):
    return _get_one(agentid).number


def agent_context(agentid):
    return _get_one(agentid).context


def agent_interface(agentid):
    try:
        return 'Agent/%s' % _get_one(agentid).number
    except LookupError:
        return None


def agent_id(agent_number):
    if agent_number is None:
        raise ValueError('Agent number is None')
    result = DbSession().query(AgentFeatures.id).filter(AgentFeatures.number == agent_number).first()
    if result is None:
        raise LookupError('No such agent')
    return str(result.id)


def _get_one(agentid):
    # field id != field agentid used only for joining with staticagent table.
    if agentid is None:
        raise ValueError('Agent ID is None')
    result = DbSession().query(AgentFeatures).filter(AgentFeatures.id == int(agentid)).first()
    if result is None:
        raise LookupError('No such agent')
    return result


def agent_with_id(agent_id):
    agent = _get_agent(AgentFeatures.id == int(agent_id))
    _add_queues_to_agent(agent)
    return agent


def agent_with_number(agent_number):
    agent = _get_agent(AgentFeatures.number == agent_number)
    _add_queues_to_agent(agent)
    return agent


def _get_agent(whereclause):
    query = select([AgentFeatures.id, AgentFeatures.number], whereclause)
    row = DbSession().execute(query).first()
    if row is None:
        raise LookupError('no agent matching clause %s' % whereclause)
    return _Agent(row['id'], row['number'], [])


def _add_queues_to_agent(agent):
    query = select([QueueFeatures.id, QueueMember.queue_name, QueueMember.penalty, QueueMember.skills],
                   and_(QueueMember.usertype == u'agent',
                        QueueMember.userid == agent.id,
                        QueueMember.queue_name == QueueFeatures.name))

    for row in DbSession().execute(query):
        queue = _Queue(row['id'], row['queue_name'], row['penalty'], row['skills'])
        agent.queues.append(queue)


def get(agentid):
    return DbSession().query(AgentFeatures).filter(AgentFeatures.id == int(agentid)).first()


def all():
    return DbSession().query(AgentFeatures).all()
