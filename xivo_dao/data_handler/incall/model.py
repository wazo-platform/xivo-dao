# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
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

from xivo_dao.alchemy.incall import Incall as IncallSchema
from xivo_dao.alchemy.dialaction import Dialaction as DialactionSchema

from xivo_dao.helpers.new_model import NewModel
from xivo_dao.converters.database_converter import DatabaseConverter


class Incall(NewModel):

    MANDATORY = [
        'destination',
        'destination_id',
        'extension_id',
    ]

    FIELDS = [
        'destination',
        'destination_id',
        'extension_id',
        'description',
    ]

    _RELATION = {}

    @classmethod
    def user_destination(cls, user_id, extension_id):
        return cls(destination='user',
                   destination_id=user_id,
                   extension_id=extension_id)


class IncallDbConverter(DatabaseConverter):

    DB_TO_MODEL_MAPPING = {}

    def __init__(self):
        DatabaseConverter.__init__(self, self.DB_TO_MODEL_MAPPING, IncallSchema, Incall)

    def to_incall(self, incall, extension):
        description = incall.description or ''
        incall_row = IncallSchema(exten=extension.exten,
                                  context=extension.context,
                                  description=description)
        return incall_row

    def to_dialaction(self, incall):
        dialaction_row = DialactionSchema(event='answer',
                                          category='incall',
                                          categoryval=incall.id,
                                          action=incall.destination,
                                          actionarg1=incall.destination_id)
        return dialaction_row


db_converter = IncallDbConverter()
