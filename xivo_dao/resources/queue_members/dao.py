# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy import func
from xivo_dao.helpers.db_utils import flush_session
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.alchemy.agentfeatures import AgentFeatures as AgentFeaturesSchema
from xivo_dao.alchemy.queuefeatures import QueueFeatures as QueueFeaturesSchema
from xivo_dao.alchemy.queuemember import QueueMember as QueueMemberSchema
from xivo_dao.resources.queue_members.model import db_converter
from xivo_dao.helpers import errors


@daosession
def get_by_queue_id_and_agent_id(session, queue_id, agent_id):
    row = (session.query(QueueMemberSchema)
           .filter(QueueFeaturesSchema.name == QueueMemberSchema.queue_name)
           .filter(QueueMemberSchema.usertype == 'agent')
           .filter(QueueMemberSchema.userid == agent_id)
           .filter(QueueFeaturesSchema.id == queue_id)).first()
    if not row:
        raise errors.not_found('QueueMember', agent_id=agent_id, queue_id=queue_id)
    result = db_converter.to_model(row)
    result.queue_id = queue_id
    return result


@daosession
def edit_agent_queue_association(session, queue_member):
    with flush_session(session):
        row = (session.query(QueueMemberSchema)
                      .filter(QueueFeaturesSchema.name == QueueMemberSchema.queue_name)
                      .filter(QueueMemberSchema.usertype == 'agent')
                      .filter(QueueMemberSchema.userid == queue_member.agent_id)
                      .filter(QueueFeaturesSchema.id == queue_member.queue_id)).first()
        row.penalty = queue_member.penalty


@daosession
def associate(session, queue_member):
    with flush_session(session):
        agent = (session.query(AgentFeaturesSchema.number)
                 .filter(AgentFeaturesSchema.id == queue_member.agent_id).first())
        queue = (session.query(QueueFeaturesSchema.name)
                 .filter(QueueFeaturesSchema.id == queue_member.queue_id).first())
        current_max_pos = (session.query(func.max(QueueMemberSchema.position))
                           .filter(QueueFeaturesSchema.name == QueueMemberSchema.queue_name)
                           .filter(QueueMemberSchema.usertype == 'agent')).scalar()

        if current_max_pos is None:
            max_pos = 0
        else:
            max_pos = current_max_pos + 1
        db_qm = db_converter.to_source(queue_member)
        db_qm.queue_name = queue.name
        db_qm.interface = 'Agent/%s' % agent.number
        db_qm.commented = 0
        db_qm.usertype = 'agent'
        db_qm.channel = 'Agent'
        db_qm.category = 'queue'
        db_qm.position = max_pos

        session.add(db_qm)

    return queue_member


@daosession
def remove_agent_from_queue(session, agent_id, queue_id):
    row = (session.query(QueueMemberSchema)
           .filter(QueueMemberSchema.usertype == 'agent')
           .filter(QueueMemberSchema.userid == agent_id)
           .filter(QueueMemberSchema.queue_name == QueueFeaturesSchema.name)
           .filter(QueueFeaturesSchema.id == queue_id)).first()
    session.delete(row)
