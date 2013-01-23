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
from sqlalchemy.sql.expression import case
from xivo_dao.alchemy import dbconnection
from xivo_dao.alchemy.agent_login_status import AgentLoginStatus
from xivo_dao.alchemy.agent_membership_status import AgentMembershipStatus
from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.alchemy.queuefeatures import QueueFeatures


_DB_NAME = 'asterisk'


_Queue = namedtuple('_Queue', ['id', 'name'])
_AgentStatus = namedtuple('_AgentStatus', ['agent_id', 'agent_number', 'extension',
                                           'context', 'interface', 'state_interface',
                                           'login_at', 'queues'])


def _session():
    connection = dbconnection.get_connection(_DB_NAME)
    return connection.get_session()


def get_status(agent_id):
    agent_login_status = _get_agent_login_status(agent_id)

    if not agent_login_status:
        return None

    return _to_agent_status(agent_login_status, _get_queues_for_agent(agent_id))


def _get_agent_login_status(agent_id):
    agent_login_status = (_session()
        .query(AgentLoginStatus)
        .get(agent_id)
    )
    return agent_login_status


def _get_queues_for_agent(agent_id):
    query = (_session()
        .query(AgentMembershipStatus.queue_id.label('queue_id'),
               AgentMembershipStatus.queue_name.label('queue_name'))
        .filter(AgentMembershipStatus.agent_id == agent_id)
    )

    return [_Queue(q.queue_id, q.queue_name) for q in query]


def get_statuses():
    return (_session()
        .query(AgentFeatures.id.label('agent_id'),
               AgentFeatures.number.label('agent_number'),
               AgentLoginStatus.extension.label('extension'),
               AgentLoginStatus.context.label('context'),
               case([(AgentLoginStatus.agent_id == None, False)], else_=True).label('logged'))
        .outerjoin((AgentLoginStatus, AgentFeatures.id == AgentLoginStatus.agent_id))
        .all()
    )


def get_statuses_of_logged_agent_for_queue(queue_id):
    session = _session()

    subquery = (session
        .query(QueueMember.userid)
        .filter(QueueFeatures.name == QueueMember.queue_name)
        .filter(QueueFeatures.id == queue_id)
        .filter(QueueMember.usertype == 'agent')
    )
    query = (session
        .query(AgentLoginStatus)
        .filter(AgentLoginStatus.agent_id.in_(subquery))
    )

    return [_to_agent_status(q, None) for q in query]


def get_statuses_to_add_to_queue(queue_id):
    # XXX name could be better
    session = _session()

    q1 = (session
        .query(AgentLoginStatus.agent_id)
    )
    q2 = (session
        .query(QueueMember.userid)
        .filter(QueueFeatures.name == QueueMember.queue_name)
        .filter(QueueFeatures.id == queue_id)
        .filter(QueueMember.usertype == 'agent')
    )
    q3 = (session
        .query(AgentMembershipStatus.agent_id)
        .filter(AgentMembershipStatus.queue_id == queue_id)
    )
    agent_ids_to_add = q1.intersect(q2).except_(q3)
    query = (session
        .query(AgentLoginStatus)
        .filter(AgentLoginStatus.agent_id.in_(agent_ids_to_add))
    )

    return [_to_agent_status(q, None) for q in query]


def get_statuses_to_remove_from_queue(queue_id):
    # XXX name could be better
    session = _session()

    q1 = (session
        .query(AgentMembershipStatus.agent_id)
        .filter(AgentMembershipStatus.queue_id == queue_id)
    )
    q2 = (session
        .query(QueueMember.userid)
        .filter(QueueFeatures.name == QueueMember.queue_name)
        .filter(QueueFeatures.id == queue_id)
        .filter(QueueMember.usertype == 'agent')
    )
    agent_ids_to_remove = q1.except_(q2)
    query = (session
        .query(AgentLoginStatus)
        .filter(AgentLoginStatus.agent_id.in_(agent_ids_to_remove))
    )

    return [_to_agent_status(q, None) for q in query]


def _to_agent_status(agent_login_status, queues):
    return _AgentStatus(agent_login_status.agent_id,
                        agent_login_status.agent_number,
                        agent_login_status.extension,
                        agent_login_status.context,
                        agent_login_status.interface,
                        agent_login_status.state_interface,
                        agent_login_status.login_at,
                        queues)


def is_agent_logged_in(agent_id):
    count = (_session()
        .query(AgentLoginStatus)
        .filter(AgentLoginStatus.agent_id == agent_id)
        .count()
    )
    return count > 0


def is_extension_in_use(extension, context):
    count = (_session()
        .query(AgentLoginStatus)
        .filter(AgentLoginStatus.extension == extension)
        .filter(AgentLoginStatus.context == context)
        .count()
    )
    return count > 0


def log_in_agent(agent_id, agent_number, extension, context, interface, state_interface):
    agent = AgentLoginStatus()
    agent.agent_id = agent_id
    agent.agent_number = agent_number
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


def remove_agent_from_queues(agent_id, queue_ids):
    session = _session()

    (session
        .query(AgentMembershipStatus)
        .filter(AgentMembershipStatus.agent_id == agent_id)
        .filter(AgentMembershipStatus.queue_id.in_(queue_ids))
        .delete(synchronize_session=False))

    session.commit()


def remove_agent_from_all_queues(agent_id):
    session = _session()

    (session
        .query(AgentMembershipStatus)
        .filter(AgentMembershipStatus.agent_id == agent_id)
        .delete(synchronize_session=False))

    session.commit()


def remove_all_agents_from_queue(queue_id):
    session = _session()

    (session
        .query(AgentMembershipStatus)
        .filter(AgentMembershipStatus.queue_id == queue_id)
        .delete(synchronize_session=False))

    session.commit()
