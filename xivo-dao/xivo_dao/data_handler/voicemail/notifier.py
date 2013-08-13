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

from xivo_dao.helpers.bus_manager import send_bus_command
from xivo_dao.data_handler.voicemail.command import CreateVoicemailCommand, \
    EditVoicemailCommand, DeleteVoicemailCommand
from xivo_dao.helpers import sysconfd_connector


def _new_sysconfd_data(ctibus_command):
    return {
        'ctibus': [ctibus_command],
        'dird': [],
        'ipbx': ['voicemail reload'],
        'agentbus': []
    }


def created(voicemail):
    data = _new_sysconfd_data('xivo[voicemail,add,%s]' % voicemail.id)
    sysconfd_connector.exec_request_handlers(data)
    send_bus_command(CreateVoicemailCommand(voicemail.id))


def edited(voicemail):
    data = _new_sysconfd_data('xivo[voicemail,edit,%s]' % voicemail.id)
    sysconfd_connector.exec_request_handlers(data)
    send_bus_command(EditVoicemailCommand(voicemail.id))


def deleted(voicemail):
    data = _new_sysconfd_data('xivo[voicemail,delete,%s]' % voicemail.id)
    sysconfd_connector.exec_request_handlers(data)
    send_bus_command(DeleteVoicemailCommand(voicemail.id))
