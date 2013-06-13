# -*- coding: utf-8 -*-

# Copyright (C) 2012-2013 Avencall
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


class AbstractNoDataParams(object):

    def __init__(self):
        pass

    def marshal(self):
        return None

    @classmethod
    def unmarshal(cls, msg):
        return cls()


class AbstractUserIDParams(object):

    def __init__(self, user_id):
        self.user_id = int(user_id)

    def marshal(self):
        return {'user_id': self.user_id}

    @classmethod
    def unmarshal(cls, msg):
        return cls(msg['user_id'])
