# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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

from xivo_dao.helpers.new_model import NewModel


class ContextType(object):
    incall = 'incall'
    internal = 'internal'
    other = 'others'
    outcall = 'outcall'
    service = 'services'

    @classmethod
    def all(cls):
        return [cls.incall, cls.internal, cls.other, cls.outcall, cls.service]


class ContextRangeType(object):
    users = 'user'
    queues = 'queue'
    groups = 'group'
    conference_rooms = 'meetme'
    incalls = 'incall'


class Context(NewModel):

    MANDATORY = [
        'name',
        'display_name',
        'type'
    ]

    FIELDS = [
        'name',
        'display_name',
        'description',
        'type',
    ]

    _RELATION = {
    }


class ContextRange(NewModel):

    MANDATORY = [
        'start'
    ]

    FIELDS = [
        'start',
        'end',
        'did_length'
    ]

    _RELATION = {
    }

    def in_range(self, exten):
        if not self.end and exten == self.start:
            return True
        elif self.start <= exten <= self.end:
            return True
        return False
