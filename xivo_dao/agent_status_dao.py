# Copyright 2007-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from datetime import datetime
from typing import NamedTuple

from sqlalchemy import and_, text
from sqlalchemy.sql import func, select

from xivo_dao.alchemy.agent_login_status import AgentLoginStatus
from xivo_dao.alchemy.agent_membership_status import AgentMembershipStatus
from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.helpers.db_utils import flush_session


class _Queue(NamedTuple):
    id: int
    name: str
    display_name: str
    penalty: int
    logged: bool
    paused: bool
    paused_reason: str | None
    login_at: datetime


class _AgentStatus(NamedTuple):
    agent_id: int
    tenant_uuid: str
    agent_number: str
    extension: str
    context: str
    interface: str
    state_interface: str
    logged: bool
    login_at: datetime
    paused: bool
    paused_reason: str | None
    queues: list[_Queue]
    user_ids: list[int]


@daosession
def get_status(session, agent_id, tenant_uuids=None):
    statuses = _get_statuses(session, tenant_uuids=tenant_uuids, agent_id=agent_id)

    if not statuses:
        return None

    status = statuses[0]
    if not status.logged:
        return None

    return status


@daosession
def get_status_by_number(session, agent_number, tenant_uuids=None):
    return _get_login_status_by_number(session, agent_number, tenant_uuids=tenant_uuids)


@daosession
def get_status_by_user(session, user_uuid, tenant_uuids=None):
    statuses = _get_statuses(session, tenant_uuids=tenant_uuids, user_uuid=user_uuid)

    if not statuses:
        return None

    if not statuses[0].logged:
        return None

    return statuses[0]


def _get_login_status_by_number(session, agent_number, tenant_uuids=None):
    statuses = _get_statuses(
        session, tenant_uuids=tenant_uuids, agent_number=agent_number
    )

    if not statuses:
        return None

    status = statuses[0]
    if not status.logged:
        return None

    return statuses[0]


@daosession
def get_agent_login_status_by_id_for_logoff(
    session, agent_id: int
) -> _AgentStatus | None:
    # NOTE(clanglois): Used for cleanup
    status = (
        session.query(AgentLoginStatus)
        .filter(AgentLoginStatus.agent_id == agent_id)
        .first()
    )
    if not status:
        return None
    queues = (
        session.query(QueueFeatures)
        .join(AgentMembershipStatus, AgentMembershipStatus.queue_id == QueueFeatures.id)
        .filter(AgentMembershipStatus.agent_id == agent_id)
        .all()
    )
    agent = status.agent
    user_ids = [user.id for user in agent.users] if agent else []
    return _AgentStatus(
        agent_id=status.agent_id,
        tenant_uuid="",
        agent_number=status.agent_number,
        extension=status.extension,
        context=status.context,
        interface=status.interface,
        state_interface=status.state_interface,
        login_at=status.login_at,
        paused=status.paused,
        paused_reason=status.paused_reason,
        queues=queues,
        user_ids=user_ids,
        logged=True,
    )


@daosession
def get_extension_from_agent_id(session, agent_id):
    login_status_row = (
        session.query(AgentLoginStatus.extension, AgentLoginStatus.context)
        .filter(AgentLoginStatus.agent_id == agent_id)
        .first()
    )

    if not login_status_row:
        raise LookupError(f'agent with id {agent_id} is not logged')

    return login_status_row.extension, login_status_row.context


@daosession
def get_agent_id_from_extension(session, extension, context):
    login_status = (
        session.query(AgentLoginStatus)
        .filter(AgentLoginStatus.extension == extension)
        .filter(AgentLoginStatus.context == context)
        .first()
    )
    if not login_status:
        raise LookupError(f'No agent logged onto extension {extension}@{context}')
    return login_status.agent_id


def _get_statuses(session, tenant_uuids=None, **kwargs):
    available_queues = (
        select(
            QueueMember.userid.label('agent_id'),
            QueueFeatures.id.label('queue_id'),
            func.coalesce(AgentMembershipStatus.penalty, 0).label('queue_penalty'),
            QueueFeatures.name.label('queue_name'),
            QueueFeatures.displayname.label('queue_displayname'),
            AgentMembershipStatus.queue_id.is_not(None).label('queue_active'),
        )
        .join(
            QueueMember,
            and_(
                QueueMember.usertype == 'agent',
                QueueMember.queue_name == QueueFeatures.name,
            ),
        )
        .outerjoin(
            AgentMembershipStatus,
            and_(
                AgentMembershipStatus.queue_id == QueueFeatures.id,
                AgentMembershipStatus.agent_id == QueueMember.userid,
            ),
        )
        .subquery()
    )

    query = (
        session.query(
            AgentFeatures.id.label('agent_id'),
            AgentFeatures.tenant_uuid,
            AgentFeatures.number,
            available_queues.c.queue_id,
            available_queues.c.queue_penalty,
            available_queues.c.queue_name,
            available_queues.c.queue_displayname,
            available_queues.c.queue_active,
            AgentLoginStatus,
        )
        .outerjoin(available_queues, available_queues.c.agent_id == AgentFeatures.id)
        .outerjoin(
            AgentLoginStatus,
            AgentLoginStatus.agent_id == AgentFeatures.id,
        )
    )

    if agent_id := kwargs.get('agent_id'):
        query = query.filter(AgentFeatures.id == agent_id)
    if agent_number := kwargs.get('agent_number'):
        query = query.filter(AgentFeatures.number == agent_number)
    if user_uuid := kwargs.get('user_uuid'):
        query = query.join(UserFeatures, AgentFeatures.id == UserFeatures.agentid)
        query = query.filter(UserFeatures.uuid == user_uuid)
    if queue_id := kwargs.get('queue_id'):
        query = query.filter(available_queues.c.queue_id == queue_id)
    if tenant_uuids is not None:
        if not tenant_uuids:
            query = query.filter(text('false'))
        else:
            query = query.filter(
                AgentFeatures.tenant_uuid.in_(tenant_uuids),
            )

    agents = {}
    for row in query.all():
        if row.agent_id not in agents:
            status_kwargs = {
                'agent_id': row.agent_id,
                'tenant_uuid': row.tenant_uuid,
                'agent_number': row.number,
                'queues': [],
                'extension': None,
                'context': None,
                'state_interface': None,
                'interface': None,
                'logged': False,
                'paused': False,
                'paused_reason': None,
                'user_ids': [],
                'login_at': None,
            }
            if row.AgentLoginStatus:
                status_kwargs['logged'] = True
                status_kwargs['extension'] = row.AgentLoginStatus.extension
                status_kwargs['context'] = row.AgentLoginStatus.context
                status_kwargs['interface'] = row.AgentLoginStatus.interface
                status_kwargs['state_interface'] = row.AgentLoginStatus.state_interface
                status_kwargs['paused'] = row.AgentLoginStatus.paused
                status_kwargs['paused_reason'] = row.AgentLoginStatus.paused_reason
                status_kwargs['login_at'] = row.AgentLoginStatus.login_at
                status_kwargs['user_ids'] = [
                    user.id for user in row.AgentLoginStatus.agent.users
                ]
            agents[row.agent_id] = _AgentStatus(**status_kwargs)

        agent_info = agents[row.agent_id]
        if row.queue_id:
            queue_kwargs = {
                'id': row.queue_id,
                'name': row.queue_name,
                'display_name': row.queue_displayname,
                'penalty': row.queue_penalty,
                'logged': False,
                'paused': False,
                'paused_reason': None,
                'login_at': None,
            }
            if row.AgentLoginStatus:
                queue_kwargs['logged'] = row.queue_active
                queue_kwargs['paused'] = row.AgentLoginStatus.paused
                queue_kwargs['paused_reason'] = row.AgentLoginStatus.paused_reason
                queue_kwargs['login_at'] = row.AgentLoginStatus.login_at
            agent_info.queues.append(_Queue(**queue_kwargs))
    return list(agents.values())


@daosession
def get_statuses(session, tenant_uuids=None):
    return _get_statuses(session, tenant_uuids=tenant_uuids)


@daosession
def get_statuses_for_queue(session, queue_id):
    return _get_statuses(session, queue_id=queue_id)


@daosession
def get_statuses_to_add_to_queue(session, queue_id):
    q1 = (
        session.query(QueueMember.userid)
        .filter(QueueFeatures.name == QueueMember.queue_name)
        .filter(QueueFeatures.id == queue_id)
        .filter(QueueMember.usertype == 'agent')
    )
    q2 = session.query(AgentMembershipStatus.agent_id).filter(
        AgentMembershipStatus.queue_id == queue_id
    )
    agent_ids_to_add = q1.except_(q2)
    query = session.query(AgentLoginStatus).filter(
        AgentLoginStatus.agent_id.in_(agent_ids_to_add)
    )

    return [_to_agent_status(q, None) for q in query]


@daosession
def get_statuses_to_remove_from_queue(session, queue_id):
    q1 = session.query(AgentMembershipStatus.agent_id).filter(
        AgentMembershipStatus.queue_id == queue_id
    )
    q2 = (
        session.query(QueueMember.userid)
        .filter(QueueFeatures.name == QueueMember.queue_name)
        .filter(QueueFeatures.id == queue_id)
        .filter(QueueMember.usertype == 'agent')
    )
    agent_ids_to_remove = q1.except_(q2)
    query = session.query(AgentLoginStatus).filter(
        AgentLoginStatus.agent_id.in_(agent_ids_to_remove)
    )

    return [_to_agent_status(q, None) for q in query]


@daosession
def get_logged_agent_ids(session, tenant_uuids=None):
    query = session.query(
        AgentLoginStatus.agent_id, AgentFeatures.tenant_uuid
    ).outerjoin(AgentFeatures, AgentFeatures.id == AgentLoginStatus.agent_id)

    if tenant_uuids is not None:
        query = query.filter(AgentFeatures.tenant_uuid.in_(tenant_uuids))

    return [q.agent_id for q in query]


def _to_agent_status(agent_login_status, queues):
    agent = agent_login_status.agent
    user_ids = [user.id for user in agent.users] if agent else []
    return _AgentStatus(
        agent_id=agent_login_status.agent_id,
        tenant_uuid=agent_login_status.agent.tenant_uuid,
        agent_number=agent_login_status.agent_number,
        extension=agent_login_status.extension,
        context=agent_login_status.context,
        interface=agent_login_status.interface,
        state_interface=agent_login_status.state_interface,
        login_at=agent_login_status.login_at,
        paused=agent_login_status.paused,
        paused_reason=agent_login_status.paused_reason,
        queues=queues,
        user_ids=user_ids,
        logged=True,
    )


@daosession
def is_extension_in_use(session, extension, context):
    count = (
        session.query(AgentLoginStatus)
        .filter(AgentLoginStatus.extension == extension)
        .filter(AgentLoginStatus.context == context)
        .count()
    )
    return count > 0


@daosession
def log_in_agent(
    session, agent_id, agent_number, extension, context, interface, state_interface
):
    agent = AgentLoginStatus()
    agent.agent_id = agent_id
    agent.agent_number = agent_number
    agent.extension = extension
    agent.context = context
    agent.interface = interface
    agent.state_interface = state_interface
    agent.paused = False

    _add_agent(session, agent)


def _add_agent(session, agent):
    with flush_session(session):
        session.add(agent)


@daosession
def log_off_agent(session, agent_id):
    (
        session.query(AgentLoginStatus)
        .filter(AgentLoginStatus.agent_id == agent_id)
        .delete(synchronize_session='fetch')
    )


@daosession
def add_agent_to_queues(session, agent_id, queues):
    for queue in queues:
        agent_membership_status = AgentMembershipStatus(
            agent_id=agent_id,
            queue_id=queue.id,
            queue_name=queue.name,
            penalty=queue.penalty,
        )
        session.add(agent_membership_status)


@daosession
def remove_agent_from_queues(session, agent_id, queue_ids):
    (
        session.query(AgentMembershipStatus)
        .filter(AgentMembershipStatus.agent_id == agent_id)
        .filter(AgentMembershipStatus.queue_id.in_(queue_ids))
        .delete(synchronize_session='fetch')
    )


@daosession
def remove_agent_from_all_queues(session, agent_id):
    (
        session.query(AgentMembershipStatus)
        .filter(AgentMembershipStatus.agent_id == agent_id)
        .delete(synchronize_session='fetch')
    )


@daosession
def remove_all_agents_from_queue(session, queue_id):
    (
        session.query(AgentMembershipStatus)
        .filter(AgentMembershipStatus.queue_id == queue_id)
        .delete(synchronize_session='fetch')
    )


@daosession
def update_penalty(session, agent_id, queue_id, penalty):
    (
        session.query(AgentMembershipStatus)
        .filter(AgentMembershipStatus.queue_id == queue_id)
        .filter(AgentMembershipStatus.agent_id == agent_id)
        .update({'penalty': penalty})
    )


@daosession
def update_pause_status(session, agent_id, is_paused, reason=None):
    (
        session.query(AgentLoginStatus)
        .filter(AgentLoginStatus.agent_id == agent_id)
        .update({'paused': is_paused, 'paused_reason': reason})
    )
