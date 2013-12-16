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

from xivo_dao.helpers.new_model import NewModel
from xivo_dao.alchemy.user_line import UserLine as UserLineSchema
from xivo_dao.converters.database_converter import DatabaseConverter

DB_TO_MODEL_MAPPING = {
    'line_id': 'line_id',
    'extension_id': 'extension_id',
}


class LineExtension(NewModel):

    FIELDS = [
        'line_id',
        'extension_id'
    ]

    _RELATION = {}

    MANDATORY = [
        'line_id',
        'extension_id',
    ]


class LineExtensionDbConverter(DatabaseConverter):

    def __init__(self):
        DatabaseConverter.__init__(self, DB_TO_MODEL_MAPPING, UserLineSchema, LineExtension)

    def to_source(self, model):
        source = DatabaseConverter.to_source(self, model)
        if not source.main_line:
            source.main_line = True
        if not source.main_user:
            source.main_user = True
        return source

db_converter = LineExtensionDbConverter()
