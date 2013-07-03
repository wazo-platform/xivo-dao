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

from __future__ import unicode_literals


class AbstractVoicemailIDParams(object):

    def __init__(self, voicemail_id):
        self.id = int(voicemail_id)

    def marshal(self):
        return {'id': self.id}

    @classmethod
    def unmarshal(cls, msg):
        return cls(msg['id'])


class EditVoicemailCommand(AbstractVoicemailIDParams):
    name = 'voicemail_edited'


class CreateVoicemailCommand(AbstractVoicemailIDParams):
    name = 'voicemail_created'


class DeleteVoicemailCommand(AbstractVoicemailIDParams):
    name = 'voicemail_deleted'
