# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.alchemy import QueueMember as QueueMemberSchema
from xivo_dao.alchemy import QueueFeatures as QueueFeaturesSchema
from xivo_dao.data_handler.queue_members.exception import QueueMemberNotExistsError
from xivo_dao.data_handler.queue_members.model import db_converter


@daosession
def get_by_queue_id_and_agent_id(session, queue_id, agent_id):
    row = (session.query(QueueMemberSchema)
                  .filter(QueueFeaturesSchema.name == QueueMemberSchema.queue_name)
                  .filter(QueueMemberSchema.usertype == 'agent')
                  .filter(QueueMemberSchema.userid == agent_id)
                  .filter(QueueFeaturesSchema.id == queue_id)).first()
    if not row:
        raise QueueMemberNotExistsError('QueueMember', agent_id=agent_id, queue_id=queue_id)
    result = db_converter.to_model(row)
    result.queue_id = queue_id
    return result


@daosession
def edit_agent_queue_association(session, queue_member):
    session.begin()
    row = (session.query(QueueMemberSchema)
                  .filter(QueueFeaturesSchema.name == QueueMemberSchema.queue_name)
                  .filter(QueueMemberSchema.usertype == 'agent')
                  .filter(QueueMemberSchema.userid == queue_member.agent_id)
                  .filter(QueueFeaturesSchema.id == queue_member.queue_id)).first()
    row.penalty = queue_member.penalty
    session.commit()
