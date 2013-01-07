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

from xivo_dao.alchemy import dbconnection
from xivo_dao.alchemy.agentfeatures import AgentFeatures


class AgentFeaturesDAO(object):

    def __init__(self, session):
        self._session = session

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
        result = self._session.query(AgentFeatures.id).filter(AgentFeatures.number == agent_number).first()
        if result is None:
            raise LookupError('No such agent')
        return str(result.id)

    def _get_one(self, agentid):
        # field id != field agentid used only for joining with staticagent table.
        if agentid is None:
            raise ValueError('Agent ID is None')
        result = self._session.query(AgentFeatures).filter(AgentFeatures.id == int(agentid)).first()
        if result is None:
            raise LookupError('No such agent')
        return result

    def add_agent(self, agent_features):
        if type(agent_features) != AgentFeatures:
            raise ValueError('Wrong object passed')

        self._session.add(agent_features)
        self._session.commit()

    @classmethod
    def new_from_uri(cls, uri):
        connection = dbconnection.get_connection(uri)
        return cls(connection.get_session())
