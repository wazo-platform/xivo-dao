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

from xivo_dao.alchemy.user_line import UserLine as UserLineSchema
from xivo_dao.converters.database_converter import DatabaseConverter
from xivo_dao.helpers.new_model import NewModel

DB_TO_MODEL_MAPPING = {
    'user_id': 'user_id',
    'line_id': 'line_id',
    'main_user': 'main_user',
    'main_line': 'main_line'
}


class UserLine(NewModel):

    def __init__(self, *args, **kwargs):
        NewModel.__init__(self, *args, **kwargs)
        if self.main_user is None:
            self.main_user = True
        if self.main_line is None:
            self.main_line = True

    FIELDS = [
        'user_id',
        'line_id',
        'main_user',
        'main_line'
    ]

    MANDATORY = [
        'user_id',
        'line_id'
    ]

    _RELATION = {}


class UserLineDbConverter(DatabaseConverter):

    def __init__(self):
        DatabaseConverter.__init__(self, DB_TO_MODEL_MAPPING, UserLineSchema, UserLine)


db_converter = UserLineDbConverter()
