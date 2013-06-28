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
from xivo_dao.data_handler.voicemail.command import CreateVoicemailCommand, \
    EditVoicemailCommand, DeleteVoicemailCommand
from xivo_dao.helpers import sysconfd_connector

sysconfd_base_data = {
    'ctibus': ['xivo[voicemail,edit,7]'],
    'dird': [],
    'ipbx': ['voicemail reload'],
    'agentbus': []
}


def created(voicemail_id):
    sysconfd_base_data['ctibus'].extend(['xivo[voicemail,create,%s]' % voicemail_id])
    sysconfd_connector.SYSCONFD_CONN.request('POST', '/exec_request_handlers', sysconfd_base_data)
    BusPublisher.execute_command(CreateVoicemailCommand(voicemail_id))


def edited(voicemail_id):
    sysconfd_base_data['ctibus'].extend(['xivo[voicemail,edit,%s]' % voicemail_id])
    sysconfd_connector.SYSCONFD_CONN.request('POST', '/exec_request_handlers', sysconfd_base_data)
    BusPublisher.execute_command(EditVoicemailCommand(voicemail_id))


def deleted(voicemail_id):
    sysconfd_base_data['ctibus'].extend(['xivo[voicemail,delete,%s]' % voicemail_id])
    sysconfd_connector.SYSCONFD_CONN.request('POST', '/exec_request_handlers', sysconfd_base_data)
    BusPublisher.execute_command(DeleteVoicemailCommand(voicemail_id))
