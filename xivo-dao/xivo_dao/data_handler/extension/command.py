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

from __future__ import unicode_literals


class AbstractExtensionIDParams(object):

    def __init__(self, extension_id, exten, context):
        self.id = int(extension_id)
        self.exten = exten
        self.context = context

    def marshal(self):
        return {
            'id': self.id,
            'exten': self.exten,
            'context': self.context
        }

    @classmethod
    def unmarshal(cls, msg):
        return cls(msg['id'], msg['exten'], msg['context'])


class EditExtensionCommand(AbstractExtensionIDParams):
    name = 'extension_edited'


class CreateExtensionCommand(AbstractExtensionIDParams):
    name = 'extension_created'


class DeleteExtensionCommand(AbstractExtensionIDParams):
    name = 'extension_deleted'
