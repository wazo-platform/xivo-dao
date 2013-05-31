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


class Line(object):

    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.number = kwargs.get('number')
        self.context = kwargs.get('context')
        self.protocol = kwargs.get('protocol')
        self.iduserfeatures = kwargs.get('iduserfeatures')

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError('Must compare a Line with another Line')

        return self.__dict__ == other.__dict__

    @classmethod
    def from_data_source(cls, properties):
        data = {
            'number': properties.number,
            'context': properties.context,
            'protocol': properties.protocol,
            'name': properties.name,
            'iduserfeatures': properties.iduserfeatures,
        }
        return cls(**data)

    @classmethod
    def from_user_data(cls, properties):
        return cls(**properties)
