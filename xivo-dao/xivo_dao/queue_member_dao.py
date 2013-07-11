# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

from sqlalchemy import func, select
from xivo_dao import line_dao
from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.helpers.db_manager import daosession


@daosession
def add_agent_to_queue(session, agent_id, agent_number, queue_name):
    next_position = _get_next_position_for_queue(session, queue_name)
    queue_member = QueueMember()
    queue_member.queue_name = queue_name
    queue_member.interface = 'Agent/%s' % agent_number
    queue_member.usertype = 'agent'
    queue_member.userid = agent_id
    queue_member.channel = 'Agent'
    queue_member.category = 'queue'
    queue_member.position = next_position

    try:
        session.begin()
        session.add(queue_member)
        session.commit()
    except Exception:
        session.rollback()
        raise


@daosession
def remove_agent_from_queue(session, agent_id, queue_name):
    (session
     .query(QueueMember)
     .filter(QueueMember.queue_name == queue_name)
     .filter(QueueMember.usertype == 'agent')
     .filter(QueueMember.userid == agent_id)
     .delete())


def _get_next_position_for_queue(session, queue_name):
    result = (session
              .query(func.max(QueueMember.position).label('max'))
              .filter(QueueMember.queue_name == queue_name)
              .first())
    last_position = result.max
    if last_position is None:
        return 0
    else:
        return last_position + 1


@daosession
def get_queue_members_for_queues(session):
    queue_name_subquery = select([QueueFeatures.name])

    rows = (session
            .query(QueueMember.queue_name,
                   QueueMember.interface.label('member_name'),
                   QueueMember.penalty)
            .filter(QueueMember.category == 'queue')
            .filter(QueueMember.queue_name.in_(queue_name_subquery))
            .all())
    return rows


@daosession
def add_user_to_queue(session, user_id, queue):
    next_position = _get_next_position_for_queue(session, queue)
    queue_member = QueueMember()
    queue_member.queue_name = queue
    queue_member.interface = line_dao.get_interface_from_user_id(user_id)
    queue_member.usertype = 'user'
    queue_member.userid = user_id
    queue_member.channel = queue_member.interface.split('/', 1)[0]
    queue_member.category = 'queue'
    queue_member.position = next_position

    try:
        session.begin()
        session.add(queue_member)
        session.commit()
    except Exception:
        session.rollback()
        raise


@daosession
def delete_by_userid(session, userid):
    session.begin()
    try:
        (session.query(QueueMember)
                .filter(QueueMember.usertype == 'user')
                .filter(QueueMember.userid == userid)
                .delete())
        session.commit()
    except Exception:
        session.rollback()
        raise
