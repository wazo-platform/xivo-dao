# -*- coding: utf-8 -*-
# Copyright 2007-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from collections import namedtuple
from sqlalchemy.sql.expression import case
from xivo_dao.alchemy.agent_login_status import AgentLoginStatus
from xivo_dao.alchemy.agent_membership_status import AgentMembershipStatus
from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.helpers.db_utils import flush_session
from xivo_dao.helpers.db_manager import daosession


_AgentStatus = namedtuple('_AgentStatus', ['agent_id', 'agent_number', 'extension',
                                           'context', 'interface', 'state_interface',
                                           'login_at', 'paused', 'paused_reason', 'queues'])
_Queue = namedtuple('_Queue', ['id', 'name', 'penalty'])


@daosession
def get_status(session, agent_id, tenant_uuids=None):
    login_status = _get_login_status_by_id(session, agent_id, tenant_uuids=tenant_uuids)
    if not login_status:
        return None

    return _to_agent_status(login_status, _get_queues_for_agent(session, agent_id))


@daosession
def get_status_by_number(session, agent_number, tenant_uuids=None):
    login_status = _get_login_status_by_number(session, agent_number, tenant_uuids=tenant_uuids)
    if not login_status:
        return None

    return _to_agent_status(login_status, _get_queues_for_agent(session, login_status.agent_id))


@daosession
def get_status_by_user(session, user_uuid, tenant_uuids=None):
    login_status = _get_login_status_by_user(session, user_uuid, tenant_uuids=tenant_uuids)
    if not login_status:
        return None

    return _to_agent_status(login_status, _get_queues_for_agent(session, login_status.agent_id))


def _get_login_status_by_id(session, agent_id, tenant_uuids=None):
    login_status = (session
                    .query(AgentLoginStatus)
                    .outerjoin((AgentFeatures, AgentFeatures.id == AgentLoginStatus.agent_id))
                    .filter(AgentLoginStatus.agent_id == agent_id))
    if tenant_uuids is not None:
        login_status = login_status.filter(AgentFeatures.tenant_uuid.in_(tenant_uuids))
    return login_status.first()


def _get_login_status_by_number(session, agent_number, tenant_uuids=None):
    login_status = (session
                    .query(AgentLoginStatus)
                    .outerjoin((AgentFeatures, AgentFeatures.id == AgentLoginStatus.agent_id))
                    .filter(AgentLoginStatus.agent_number == agent_number))
    if tenant_uuids is not None:
        login_status = login_status.filter(AgentFeatures.tenant_uuid.in_(tenant_uuids))
    return login_status.first()


def _get_login_status_by_user(session, user_uuid, tenant_uuids=None):
    login_status = (session
                    .query(AgentLoginStatus)
                    .outerjoin((AgentFeatures, AgentFeatures.id == AgentLoginStatus.agent_id))
                    .join((UserFeatures, AgentFeatures.id == UserFeatures.agentid))
                    .filter(UserFeatures.uuid == user_uuid))
    if tenant_uuids is not None:
        login_status = login_status.filter(AgentFeatures.tenant_uuid.in_(tenant_uuids))
    return login_status.first()


def _get_queues_for_agent(session, agent_id):
    query = (session
             .query(AgentMembershipStatus.queue_id.label('queue_id'),
                    AgentMembershipStatus.queue_name.label('queue_name'),
                    AgentMembershipStatus.penalty.label('penalty'))
             .filter(AgentMembershipStatus.agent_id == agent_id))

    return [_Queue(q.queue_id, q.queue_name, q.penalty) for q in query]


@daosession
def get_extension_from_agent_id(session, agent_id):
    login_status_row = (session
                        .query(AgentLoginStatus.extension, AgentLoginStatus.context)
                        .filter(AgentLoginStatus.agent_id == agent_id)
                        .first())

    if not login_status_row:
        raise LookupError('agent with id %s is not logged' % agent_id)

    return login_status_row.extension, login_status_row.context


@daosession
def get_agent_id_from_extension(session, extension, context):
    login_status = (session
                    .query(AgentLoginStatus)
                    .filter(AgentLoginStatus.extension == extension)
                    .filter(AgentLoginStatus.context == context)
                    .first())
    if not login_status:
        raise LookupError('No agent logged onto extension %s@%s' % (extension, context))
    return login_status.agent_id


@daosession
def get_statuses(session, tenant_uuids=None):
    query = (
        session.query(
            AgentFeatures.id.label('agent_id'),
            AgentFeatures.tenant_uuid.label('tenant_uuid'),
            AgentFeatures.number.label('agent_number'),
            AgentLoginStatus.extension.label('extension'),
            AgentLoginStatus.context.label('context'),
            AgentLoginStatus.state_interface.label('state_interface'),
            AgentLoginStatus.paused.label('paused'),
            AgentLoginStatus.paused_reason.label('paused_reason'),
            case([(AgentLoginStatus.agent_id == None, False)], else_=True).label('logged')  # noqa
        ).outerjoin((AgentLoginStatus, AgentFeatures.id == AgentLoginStatus.agent_id))
    )

    if tenant_uuids is not None:
        query = query.filter(AgentFeatures.tenant_uuid.in_(tenant_uuids))

    return query.all()


@daosession
def get_statuses_for_queue(session, queue_id):
    session = session

    subquery = (session
                .query(QueueMember.userid)
                .filter(QueueFeatures.name == QueueMember.queue_name)
                .filter(QueueFeatures.id == queue_id)
                .filter(QueueMember.usertype == 'agent'))
    query = (session
             .query(AgentLoginStatus)
             .filter(AgentLoginStatus.agent_id.in_(subquery)))

    return [_to_agent_status(q, None) for q in query]


@daosession
def get_statuses_to_add_to_queue(session, queue_id):
    q1 = (session
          .query(QueueMember.userid)
          .filter(QueueFeatures.name == QueueMember.queue_name)
          .filter(QueueFeatures.id == queue_id)
          .filter(QueueMember.usertype == 'agent'))
    q2 = (session
          .query(AgentMembershipStatus.agent_id)
          .filter(AgentMembershipStatus.queue_id == queue_id))
    agent_ids_to_add = q1.except_(q2)
    query = (session
             .query(AgentLoginStatus)
             .filter(AgentLoginStatus.agent_id.in_(agent_ids_to_add)))

    return [_to_agent_status(q, None) for q in query]


@daosession
def get_statuses_to_remove_from_queue(session, queue_id):
    q1 = (session
          .query(AgentMembershipStatus.agent_id)
          .filter(AgentMembershipStatus.queue_id == queue_id))
    q2 = (session
          .query(QueueMember.userid)
          .filter(QueueFeatures.name == QueueMember.queue_name)
          .filter(QueueFeatures.id == queue_id)
          .filter(QueueMember.usertype == 'agent'))
    agent_ids_to_remove = q1.except_(q2)
    query = (session
             .query(AgentLoginStatus)
             .filter(AgentLoginStatus.agent_id.in_(agent_ids_to_remove)))

    return [_to_agent_status(q, None) for q in query]


@daosession
def get_logged_agent_ids(session, tenant_uuids=None):
    query = (session
             .query(AgentLoginStatus.agent_id, AgentFeatures.tenant_uuid)
             .outerjoin(AgentFeatures, AgentFeatures.id == AgentLoginStatus.agent_id))

    if tenant_uuids is not None:
        query = query.filter(AgentFeatures.tenant_uuid.in_(tenant_uuids))

    return [q.agent_id for q in query]


def _to_agent_status(agent_login_status, queues):
    return _AgentStatus(agent_login_status.agent_id,
                        agent_login_status.agent_number,
                        agent_login_status.extension,
                        agent_login_status.context,
                        agent_login_status.interface,
                        agent_login_status.state_interface,
                        agent_login_status.login_at,
                        agent_login_status.paused,
                        agent_login_status.paused_reason,
                        queues)


@daosession
def is_extension_in_use(session, extension, context):
    count = (session
             .query(AgentLoginStatus)
             .filter(AgentLoginStatus.extension == extension)
             .filter(AgentLoginStatus.context == context)
             .count())
    return count > 0


@daosession
def log_in_agent(session, agent_id, agent_number, extension, context, interface, state_interface):
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
    (session
     .query(AgentLoginStatus)
     .filter(AgentLoginStatus.agent_id == agent_id)
     .delete(synchronize_session='fetch'))


@daosession
def add_agent_to_queues(session, agent_id, queues):
    for queue in queues:
        agent_membership_status = AgentMembershipStatus(agent_id=agent_id,
                                                        queue_id=queue.id,
                                                        queue_name=queue.name,
                                                        penalty=queue.penalty)
        session.add(agent_membership_status)


@daosession
def remove_agent_from_queues(session, agent_id, queue_ids):
    (session
     .query(AgentMembershipStatus)
     .filter(AgentMembershipStatus.agent_id == agent_id)
     .filter(AgentMembershipStatus.queue_id.in_(queue_ids))
     .delete(synchronize_session='fetch'))


@daosession
def remove_agent_from_all_queues(session, agent_id):
    (session
     .query(AgentMembershipStatus)
     .filter(AgentMembershipStatus.agent_id == agent_id)
     .delete(synchronize_session='fetch'))


@daosession
def remove_all_agents_from_queue(session, queue_id):
    (session
     .query(AgentMembershipStatus)
     .filter(AgentMembershipStatus.queue_id == queue_id)
     .delete(synchronize_session='fetch'))


@daosession
def update_penalty(session, agent_id, queue_id, penalty):
    (session
     .query(AgentMembershipStatus)
     .filter(AgentMembershipStatus.queue_id == queue_id)
     .filter(AgentMembershipStatus.agent_id == agent_id)
     .update({'penalty': penalty}))


@daosession
def update_pause_status(session, agent_id, is_paused, reason=None):
    (session
     .query(AgentLoginStatus)
     .filter(AgentLoginStatus.agent_id == agent_id)
     .update({'paused': is_paused, 'paused_reason': reason}))
