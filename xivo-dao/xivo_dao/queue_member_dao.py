# vim: set fileencoding=utf-8 :
# XiVO CTI Server

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
from xivo_dao.alchemy.queuemember import QueueMember
from sqlalchemy import func

_DB_NAME = 'asterisk'


def _session():
    connection = dbconnection.get_connection(_DB_NAME)
    return connection.get_session()


def add_agent_to_queue(agent_id, agent_number, queue_name):
    next_position = _get_next_position_for_queue(queue_name)
    queue_member = QueueMember()
    queue_member.queue_name = queue_name
    queue_member.interface = 'Agent/%s' % agent_number
    queue_member.usertype = 'agent'
    queue_member.userid = agent_id
    queue_member.channel = 'Agent'
    queue_member.category = 'queue'
    queue_member.skills = 'agent-%s' % agent_id
    queue_member.position = next_position

    try:
        _session().add(queue_member)
        _session().commit()
    except Exception:
        _session().rollback()
        raise


def remove_agent_from_queue(agent_id, queue_name):
    print 'removing agent from %r %r' % (agent_id, queue_name)
    (_session()
     .query(QueueMember)
     .filter(QueueMember.queue_name == queue_name)
     .filter(QueueMember.usertype == 'agent')
     .filter(QueueMember.userid == agent_id)
     .delete())
    _session().commit()


def _get_next_position_for_queue(queue_name):
    result = (_session()
              .query(func.max(QueueMember.position).label('max'))
              .filter(QueueMember.queue_name == queue_name)
              .first())
    last_position = result.max
    if last_position is None:
        return 0
    else:
        return last_position + 1


def get_queue_members_for_queues():
    rows = (_session()
            .query(QueueMember.queue_name,
                   QueueMember.interface.label('member_name'),
                   QueueMember.penalty)
            .filter(QueueMember.category == 'queue')
            .all())
    return rows
