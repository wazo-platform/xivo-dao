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

from collections import namedtuple
from sqlalchemy.sql.expression import case
from xivo_dao.alchemy import dbconnection
from xivo_dao.alchemy.agent_login_status import AgentLoginStatus
from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_dao.alchemy.agent_membership_status import AgentMembershipStatus

_DB_NAME = 'asterisk'


_Queue = namedtuple('_Queue', ['id', 'name'])

def _session():
    connection = dbconnection.get_connection(_DB_NAME)
    return connection.get_session()


def get_status(agent_id):
    agent_status = _get_agent_status(agent_id)
    if agent_status:
        agent_status.queues = _get_queues_for_agent(agent_id)
    return agent_status


def _get_agent_status(agent_id):
    return _session().query(AgentLoginStatus).get(agent_id)


def _get_queues_for_agent(agent_id):
    query = _session().query(
                AgentMembershipStatus.queue_id.label('queue_id'),
                AgentMembershipStatus.queue_name.label('queue_name')
            ).filter(AgentMembershipStatus.agent_id == agent_id)

    return [_Queue(q.queue_id, q.queue_name) for q in query]


def get_statuses():
    return _session().query(
        AgentFeatures.id.label('agent_id'),
        AgentFeatures.number.label('agent_number'),
        AgentLoginStatus.extension.label('extension'),
        AgentLoginStatus.context.label('context'),
        case([(AgentLoginStatus.agent_id == None, False)], else_=True).label('logged')
    ).outerjoin((AgentLoginStatus, AgentFeatures.id == AgentLoginStatus.agent_id)).all()


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


def log_in_agent(agent_id, extension, context, interface, state_interface):
    agent = AgentLoginStatus()
    agent.agent_id = agent_id
    agent.extension = extension
    agent.context = context
    agent.interface = interface
    agent.state_interface = state_interface

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


def add_agent_to_queues(agent_id, queues):
    session = _session()
    for queue in queues:
        agent_membership_status = AgentMembershipStatus(agent_id=agent_id,
                                                        queue_id=queue.id,
                                                        queue_name=queue.name)
        session.add(agent_membership_status)

    session.commit()


def remove_agent_from_queues(agent_id, queues):
    session = _session()

    queue_ids = [q.id for q in queues]
    queue_names = [q.name for q in queues]

    (session
        .query(AgentMembershipStatus)
        .filter(AgentMembershipStatus.agent_id == agent_id)
        .filter(AgentMembershipStatus.queue_id.in_(queue_ids))
        .filter(AgentMembershipStatus.queue_name.in_(queue_names))
        .delete(synchronize_session=False))

    session.commit()


def remove_agent_from_all_queues(agent_id):
    session = _session()

    (session
        .query(AgentMembershipStatus)
        .filter(AgentMembershipStatus.agent_id == agent_id)
        .delete(synchronize_session=False))

    session.commit()
