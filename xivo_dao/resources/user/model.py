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


class UserDirectory(object):

    def __init__(self, id, line_id, agent_id, firstname, lastname, exten,
                 mobile_phone_number, voicemail_number, userfield, description):
        self.id = id
        self.line_id = line_id
        self.agent_id = agent_id
        self.firstname = firstname
        self.lastname = lastname
        self.exten = exten
        self.mobile_phone_number = mobile_phone_number
        self.voicemail_number = voicemail_number
        self.userfield = userfield
        self.description = description

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
