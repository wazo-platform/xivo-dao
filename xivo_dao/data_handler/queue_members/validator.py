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
from xivo_dao import queue_dao, agent_dao
from xivo_dao.data_handler.queue_members import dao as queue_members_dao
from xivo_dao.data_handler.queues.exception import QueueNotExistsError
from xivo_dao.data_handler.agents.exception import AgentNotExistsError


def validate_edit_agent_queue_association(queue_member):
    _validate_queue_exists(queue_member.queue_id)
    _validate_agent_exists(queue_member.agent_id)
    queue_members_dao.get_by_queue_id_and_agent_id(queue_member.queue_id, queue_member.agent_id)


def validate_get_agent_queue_association(queue_id, agent_id):
    _validate_queue_exists(queue_id)
    _validate_agent_exists(agent_id)


def _validate_queue_exists(queue_id):
    try:
        queue_dao.get(queue_id)
    except LookupError:
        raise QueueNotExistsError('Queue', id=queue_id)


def _validate_agent_exists(agent_id):
    if agent_dao.get(agent_id) is None:
        raise AgentNotExistsError('Agent', id=agent_id)
