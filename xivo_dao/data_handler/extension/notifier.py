# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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

from xivo_dao.helpers.bus_manager import send_bus_event
from xivo_bus.resources.extension.event import CreateExtensionEvent, \
    EditExtensionEvent, DeleteExtensionEvent
from xivo_dao.helpers import sysconfd_connector

sysconfd_base_data = {
    'ctibus': [],
    'dird': [],
    'ipbx': ['dialplan reload'],
    'agentbus': []
}

routing_key = 'config.extension.{}'


def created(extension):
    sysconfd_connector.exec_request_handlers(sysconfd_base_data)
    event = CreateExtensionEvent(extension.id,
                                 extension.exten,
                                 extension.context)
    send_bus_event(event, routing_key.format('created'))


def edited(extension):
    sysconfd_connector.exec_request_handlers(sysconfd_base_data)
    event = EditExtensionEvent(extension.id,
                               extension.exten,
                               extension.context)
    send_bus_event(event, routing_key.format('edited'))


def deleted(extension):
    sysconfd_connector.exec_request_handlers(sysconfd_base_data)
    event = DeleteExtensionEvent(extension.id,
                                 extension.exten,
                                 extension.context)
    send_bus_event(event, routing_key.format('deleted'))
