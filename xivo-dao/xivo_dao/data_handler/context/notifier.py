# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
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

from xivo_bus.resources.context import event
from xivo_dao.helpers import bus_manager
from xivo_dao.helpers import sysconfd_connector


def created(context):
    sysconf_reload_dialplan()
    send_bus_event_created(context)


def sysconf_reload_dialplan():
    sysconf_command = {
        'ctibus': [],
        'dird': [],
        'ipbx': ['dialplan reload'],
        'agentbus': []
    }

    sysconfd_connector.exec_request_handlers(sysconf_command)


def send_bus_event_created(context):
    created_event = event.CreateContextEvent(context.name,
                                             context.display_name,
                                             context.description,
                                             context.type)
    bus_manager.send_bus_command(created_event)
