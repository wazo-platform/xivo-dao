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

from xivo_dao.data_handler.queue_members import dao as queue_members_dao
from xivo_dao.data_handler.queue_members import validator
from xivo_dao.data_handler.queue_members import notifier


def get_by_queue_id_and_agent_id(queue_id, agent_id):
    validator.validate_get_agent_queue_association(queue_id, agent_id)
    return queue_members_dao.get_by_queue_id_and_agent_id(queue_id, agent_id)


def edit_agent_queue_association(queue_member):
    validator.validate_edit_agent_queue_association(queue_member)
    queue_members_dao.edit_agent_queue_association(queue_member)
    notifier.agent_queue_association_updated(queue_member)


def associate_agent_to_queue(queue_member):
    validator.validate_associate_agent_queue(queue_member.queue_id, queue_member.agent_id)
    qm = queue_members_dao.associate(queue_member)
    notifier.agent_queue_associated(queue_member)
    return qm


def remove_agent_from_queue(agent_id, queue_id):
    validator.validate_remove_agent_from_queue(agent_id, queue_id)
    queue_members_dao.remove_agent_from_queue(agent_id, queue_id)
    notifier.agent_removed_from_queue(agent_id)
