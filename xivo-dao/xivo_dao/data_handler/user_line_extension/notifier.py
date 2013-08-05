# -*- coding: utf-8 -*-
#
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

from xivo_dao.helpers.bus_manager import send_bus_command
from command import CreateUserLineExtensionCommand, \
    EditUserLineExtensionCommand, DeleteUserLineExtensionCommand
from xivo_dao.helpers import sysconfd_connector


def _new_sysconfd_data(ctibus_command):
    return {
        'ctibus': [ctibus_command],
        'dird': [],
        'ipbx': [],
        'agentbus': []
    }


def created(user_line_extension):
    data = _new_sysconfd_data('xivo[phone,add,%s]' % user_line_extension.line_id)
    sysconfd_connector.exec_request_handlers(data)

    send_bus_command(CreateUserLineExtensionCommand(user_line_extension.id,
                                                    user_line_extension.user_id,
                                                    user_line_extension.line_id,
                                                    user_line_extension.extension_id,
                                                    user_line_extension.main_user,
                                                    user_line_extension.main_line))


def edited(user_line_extension):
    data = _new_sysconfd_data('xivo[phone,edit,%s]' % user_line_extension.line_id)
    sysconfd_connector.exec_request_handlers(data)

    send_bus_command(EditUserLineExtensionCommand(user_line_extension.id,
                                                  user_line_extension.user_id,
                                                  user_line_extension.line_id,
                                                  user_line_extension.extension_id,
                                                  user_line_extension.main_user,
                                                  user_line_extension.main_line))


def deleted(user_line_extension):
    data = _new_sysconfd_data('xivo[phone,delete,%s]' % user_line_extension.line_id)
    sysconfd_connector.exec_request_handlers(data)

    send_bus_command(DeleteUserLineExtensionCommand(user_line_extension.id,
                                                    user_line_extension.user_id,
                                                    user_line_extension.line_id,
                                                    user_line_extension.extension_id,
                                                    user_line_extension.main_user,
                                                    user_line_extension.main_line))
