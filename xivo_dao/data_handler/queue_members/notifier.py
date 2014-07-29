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

from xivo_bus.resources.queue_members import event
from xivo_dao.helpers import sysconfd_connector
from xivo_dao.helpers import bus_manager


def agent_queue_association_updated(queue_member):
    sysconf_command_agent_association_updated(queue_member)
    bus_event_agent_association_updated(queue_member)


def sysconf_command_agent_association_updated(queue_member):
    command = {
        'dird': [],
        'ipbx': [],
        'agentbus': ['agent.edit.%s' % queue_member.agent_id],
        'ctibus': []
    }
    sysconfd_connector.exec_request_handlers(command)


def bus_event_agent_association_updated(queue_member):
    bus_event = event.AgentQueueAssociationEditedEvent(queue_member.queue_id,
                                                       queue_member.agent_id,
                                                       queue_member.penalty)
    bus_manager.send_bus_command(bus_event)
