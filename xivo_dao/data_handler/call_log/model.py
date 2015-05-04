# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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

from xivo_dao.alchemy.call_log import CallLog as CallLogSchema
from xivo_dao.converters.database_converter import DatabaseConverter
from xivo_dao.helpers.new_model import NewModel

sentinel = object()


class CallLog(NewModel):
    MANDATORY = [
        'date',
        'duration',
    ]

    FIELDS = [
        'id',
        'date',
        'source_name',
        'source_exten',
        'destination_name',
        'destination_exten',
        'user_field',
        'answered',
        'duration',
        'source_line_identity',
        'destination_line_identity',
    ]

    _RELATION = {
    }

    def __init__(self, *args, **kwargs):
        NewModel.__init__(self, *args, **kwargs)
        self._related_cels = []

    def get_related_cels(self):
        return self._related_cels

    def add_related_cels(self, cel_ids):
        self._related_cels.extend(cel_ids)

    def matches(self, other, fields):
        for field in fields:
            mine = getattr(self, field, sentinel)
            others = getattr(other, field, sentinel)
            if mine != others:
                print mine, '!=', others
                return False
        else:
            return True



DB_TO_MODEL_MAPPING = {
    'id': 'id',
    'date': 'date',
    'source_name': 'source_name',
    'source_exten': 'source_exten',
    'destination_name': 'destination_name',
    'destination_exten': 'destination_exten',
    'user_field': 'user_field',
    'answered': 'answered',
    'duration': 'duration',
    'source_line_identity': 'source_line_identity',
    'destination_line_identity': 'destination_line_identity',
}


db_converter = DatabaseConverter(DB_TO_MODEL_MAPPING, CallLogSchema, CallLog)
