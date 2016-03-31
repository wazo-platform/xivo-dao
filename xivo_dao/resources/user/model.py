# -*- coding: utf-8 -*-

# Copyright (C) 2013-2016 Avencall
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


class UserDirectory(object):

    def __init__(self, id, uuid, line_id, agent_id, firstname, lastname, exten, email,
                 mobile_phone_number, voicemail_number, userfield, description, context):
        self.id = id
        self.uuid = uuid
        self.line_id = line_id
        self.agent_id = agent_id
        self.firstname = firstname
        self.lastname = lastname
        self.exten = exten
        self.email = email
        self.mobile_phone_number = mobile_phone_number
        self.voicemail_number = voicemail_number
        self.userfield = userfield
        self.description = description
        self.context = context

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class UserSummary(object):

    def __init__(self, id, uuid, firstname, lastname, provisioning_code, protocol,
                 extension, context, entity):
        self.id = id
        self.uuid = uuid
        self.firstname = firstname
        self.lastname = lastname
        self.provisioning_code = provisioning_code
        self.protocol = protocol
        self.extension = extension
        self.context = context
        self.entity = entity

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
