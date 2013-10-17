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

from xivo_dao.alchemy.context import Context as ContextSchema
from xivo_dao.converters.database_converter import DatabaseConverter
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


DB_TO_MODEL_MAPPING = {
    'name': 'name',
    'displayname': 'display_name',
    'description': 'description',
    'contexttype': 'type'
}


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


class ContextDBConverter(DatabaseConverter):
    def __init__(self):
        DatabaseConverter.__init__(self, DB_TO_MODEL_MAPPING, ContextSchema, Context)

    def to_source(self, model):
        context_row = DatabaseConverter.to_source(self, model)
        if context_row.description is None:
            context_row.description = ''
        if context_row.commented is None:
            context_row.commented = 0
        return context_row

db_converter = ContextDBConverter()
