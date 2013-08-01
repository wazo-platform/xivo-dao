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


class AbstractUserLineExtensionIDParams(object):

    def __init__(self,
                 user_line_extension_id,
                 user_id,
                 line_id,
                 extension_id,
                 main_user,
                 main_line):
        self.id = int(user_line_extension_id)
        self.user_id = int(user_id)
        self.line_id = int(line_id)
        self.extension_id = int(extension_id)
        self.main_user = bool(main_user)
        self.main_line = bool(main_line)

    def marshal(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'line_id': self.line_id,
            'extension_id': self.extension_id,
            'main_user': self.main_user,
            'main_line': self.main_line
        }

    @classmethod
    def unmarshal(cls, msg):
        return cls(msg['id'],
                   msg['user_id'],
                   msg['line_id'],
                   msg['extension_id'],
                   msg['main_user'],
                   msg['main_line'])


class CreateUserLineExtensionCommand(AbstractUserLineExtensionIDParams):
    name = 'user_line_extension_created'


class EditUserLineExtensionCommand(AbstractUserLineExtensionIDParams):
    name = 'user_line_extension_edited'


class DeleteUserLineExtensionCommand(AbstractUserLineExtensionIDParams):
    name = 'user_line_extension_deleted'
