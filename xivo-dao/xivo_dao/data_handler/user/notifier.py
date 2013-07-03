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
from xivo_dao.data_handler.user.command import CreateUserCommand, \
    EditUserCommand, DeleteUserCommand
from xivo_dao.helpers import sysconfd_connector

sysconfd_base_data = {
    'ctibus': [],
    'dird': [],
    'ipbx': ['dialplan reload',
             'module reload app_queue.so',
             'sip reload'],
    'agentbus': []
}


def created(user):
    sysconfd_base_data['ctibus'].extend(['xivo[user,create,%s]' % user.id])
    sysconfd_connector.exec_request_handlers(sysconfd_base_data)
    BusPublisher.execute_command(CreateUserCommand(user))


def edited(user):
    sysconfd_base_data['ctibus'].extend(['xivo[user,edit,%s]' % user.id])
    sysconfd_connector.exec_request_handlers(sysconfd_base_data)
    BusPublisher.execute_command(EditUserCommand(user))


def deleted(user):
    sysconfd_base_data['ctibus'].extend(['xivo[user,delete,%s]' % user.id])
    sysconfd_connector.exec_request_handlers(sysconfd_base_data)
    BusPublisher.execute_command(DeleteUserCommand(user))
