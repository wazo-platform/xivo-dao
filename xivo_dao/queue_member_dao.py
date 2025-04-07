# Copyright 2013-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import func

from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.helpers.db_utils import flush_session


@daosession
def add_agent_to_queue(session, agent_id, agent_number, queue_name):
    next_position = _get_next_position_for_queue(session, queue_name)
    queue_member = QueueMember()
    queue_member.queue_name = queue_name
    queue_member.interface = f'Agent/{agent_number}'
    queue_member.usertype = 'agent'
    queue_member.userid = agent_id
    queue_member.channel = 'Agent'
    queue_member.category = 'queue'
    queue_member.position = next_position

    with flush_session(session):
        session.add(queue_member)


@daosession
def remove_agent_from_queue(session, agent_id, queue_name):
    (
        session.query(QueueMember)
        .filter(QueueMember.queue_name == queue_name)
        .filter(QueueMember.usertype == 'agent')
        .filter(QueueMember.userid == agent_id)
        .delete()
    )


def _get_next_position_for_queue(session, queue_name):
    result = (
        session.query(func.max(QueueMember.position).label('max'))
        .filter(QueueMember.queue_name == queue_name)
        .first()
    )
    last_position = result.max
    if last_position is None:
        return 0
    else:
        return last_position + 1
