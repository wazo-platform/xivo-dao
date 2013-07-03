# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

from xivo_dao.helpers.db_manager import BusPublisher
from xivo_dao.data_handler.line.command import CreateLineCommand, \
    EditLineCommand, DeleteLineCommand
from xivo_dao.helpers import sysconfd_connector

sysconfd_base_data = {
    'ctibus': [],
    'dird': [],
    'ipbx': ['dialplan reload',
             'sip reload'],
    'agentbus': []
}


def created(line):
    sysconfd_base_data['ctibus'].extend(['xivo[phone,create,%s]' % line.id])
    sysconfd_connector.exec_request_handlers(sysconfd_base_data)
    BusPublisher.execute_command(CreateLineCommand(line))


def edited(line):
    sysconfd_base_data['ctibus'].extend(['xivo[phone,edit,%s]' % line.id])
    sysconfd_connector.exec_request_handlers(sysconfd_base_data)
    BusPublisher.execute_command(EditLineCommand(line))


def deleted(line):
    sysconfd_base_data['ctibus'].extend(['xivo[phone,delete,%s]' % line.id])
    sysconfd_connector.exec_request_handlers(sysconfd_base_data)
    BusPublisher.execute_command(DeleteLineCommand(line))
