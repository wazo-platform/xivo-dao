# -*- coding: UTF-8 -*-

# Copyright (C) 2007-2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Pro-formatique SARL. See the LICENSE file at top of the
# source tree or delivered in the installable package in which XiVO CTI Server
# is distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from collections import namedtuple
from sqlalchemy.sql import select, and_
from xivo_dao.alchemy import dbconnection
from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_dao.alchemy.queuemember import QueueMember

_DB_NAME = 'asterisk'

_Agent = namedtuple('_Agent', ['id', 'number', 'queues'])
_Queue = namedtuple('_Queue', ['name'])


def _session():
    connection = dbconnection.get_connection(_DB_NAME)
    return connection.get_session()


def _engine():
    connection = dbconnection.get_connection(_DB_NAME)
    return connection.get_engine()


class AgentFeaturesDAO(object):

    def __init__(self):
        pass

    def agent_number(self, agentid):
        return self._get_one(agentid).number

    def agent_context(self, agentid):
        return self._get_one(agentid).context

    def agent_interface(self, agentid):
        try:
            return 'Agent/%s' % self._get_one(agentid).number
        except LookupError:
            return None

    def agent_id(self, agent_number):
        if agent_number is None:
            raise ValueError('Agent number is None')
        result = _session().query(AgentFeatures.id).filter(AgentFeatures.number == agent_number).first()
        if result is None:
            raise LookupError('No such agent')
        return str(result.id)

    def _get_one(self, agentid):
        # field id != field agentid used only for joining with staticagent table.
        if agentid is None:
            raise ValueError('Agent ID is None')
        result = _session().query(AgentFeatures).filter(AgentFeatures.id == int(agentid)).first()
        if result is None:
            raise LookupError('No such agent')
        return result

    def agent_with_id(self, agent_id):
        conn = _engine().connect()
        try:
            agent = self._get_agent(conn, AgentFeatures.id == int(agent_id))
            self._add_queues_to_agent(conn, agent)
            return agent
        finally:
            conn.close()

    def agent_with_number(self, agent_number):
        conn = _engine().connect()
        try:
            agent = self._get_agent(conn, AgentFeatures.number == agent_number)
            self._add_queues_to_agent(conn, agent)
            return agent
        finally:
            conn.close()

    def _get_agent(self, conn, whereclause):
        query = select([AgentFeatures.id, AgentFeatures.number], whereclause)
        row = conn.execute(query).first()
        if row is None:
            raise LookupError('no agent matching clause %s' % whereclause)
        return _Agent(row['id'], row['number'], [])

    def _add_queues_to_agent(self, conn, agent):
        query = select([QueueMember.queue_name],
                       and_(QueueMember.usertype == u'agent',
                            QueueMember.userid == agent.id))
        for row in conn.execute(query):
            queue = _Queue(row['queue_name'])
            agent.queues.append(queue)


def get(self, agentid):
    return _session().query(AgentFeatures).filter(AgentFeatures.id == int(agentid)).first()


def all():
    return _session().query(AgentFeatures).all()
