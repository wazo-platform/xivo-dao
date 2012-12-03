# -*- coding: utf-8 -*-

# XiVO CTI Server
# Copyright (C) 2007-2012  Avencall'
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall. See the LICENSE file at top of the source tree
# or delivered in the installable package in which XiVO CTI Server is
# distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from xivo_dao.alchemy import dbconnection
from xivo_dao.alchemy.agent_login_status import AgentLoginStatus

_DB_NAME = 'asterisk'


def _session():
    connection = dbconnection.get_connection(_DB_NAME)
    return connection.get_session()


def get_status(agent_id):
    return _session().query(AgentLoginStatus).get(agent_id)


def is_agent_logged_in(agent_id):
    count = (_session()
    .query(AgentLoginStatus)
    .filter(AgentLoginStatus.agent_id == agent_id)
    .count())

    return count > 0


def is_extension_in_use(extension, context):
    count = (_session()
           .query(AgentLoginStatus)
           .filter(AgentLoginStatus.extension == extension)
           .filter(AgentLoginStatus.context == context)
           .count())

    return count > 0


def log_in_agent(agent_id, extension, context, interface):
    agent = AgentLoginStatus()
    agent.agent_id = agent_id
    agent.extension = extension
    agent.context = context
    agent.interface = interface

    session = _session()
    try:
        session.add(agent)
        session.commit()
    except Exception:
        session.rollback()
        raise


def log_off_agent(agent_id):
    session = _session()
    (session
        .query(AgentLoginStatus)
        .filter(AgentLoginStatus.agent_id == agent_id)
        .delete(synchronize_session=False))
    session.commit()
