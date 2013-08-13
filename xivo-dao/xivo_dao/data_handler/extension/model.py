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

from xivo_dao.helpers.abstract_model import AbstractModels
from xivo_dao.alchemy.extension import Extension as ExtensionSchema


class Extension(AbstractModels):

    MANDATORY = [
        'exten',
        'context',
        'type',
        'typeval'
    ]

    # mapping = {db_field: model_field}
    _MAPPING = {
        'id': 'id',
        'exten': 'exten',
        'context': 'context',
        'type': 'type',
        'typeval': 'typeval',
        'commented': 'commented'
    }

    _RELATION = {}

    def __init__(self, *args, **kwargs):
        AbstractModels.__init__(self, *args, **kwargs)

    @classmethod
    def from_data_source(cls, db_object):
        obj = super(Extension, cls).from_data_source(db_object)
        if hasattr(obj, 'commented') and isinstance(obj.commented, int):
            obj.commented = bool(obj.commented)
        return obj

    def to_data_source(self, class_schema):
        if hasattr(self, 'commented') and isinstance(self.commented, bool):
            self.commented = int(self.commented)
        return AbstractModels.to_data_source(self, class_schema)

    def to_data_dict(self):
        if hasattr(self, 'commented') and isinstance(self.commented, bool):
            self.commented = int(self.commented)
        return AbstractModels.to_data_dict(self)

    def update_from_data(self, data):
        if 'commented' in data:
            data['commented'] = bool(data['commented'])
        AbstractModels.update_from_data(self, data)


class ExtensionOrdering(object):
    exten = ExtensionSchema.exten
    context = ExtensionSchema.context
