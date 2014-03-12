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

from sqlalchemy import func

from xivo_dao.helpers.new_model import NewModel
from xivo_dao.converters.database_converter import DatabaseConverter
from xivo_dao.data_handler.func_key import type_dao as func_key_type_dao
from xivo_dao.alchemy.func_key import FuncKey as FuncKeySchema
from xivo_dao.alchemy.func_key_type import FuncKeyType as FuncKeyTypeSchema
from xivo_dao.alchemy.func_key_dest_user import FuncKeyDestUser as FuncKeyDestUserSchema
from xivo_dao.alchemy.func_key_dest_group import FuncKeyDestGroup as FuncKeyDestGroupSchema
from xivo_dao.alchemy.func_key_destination_type import FuncKeyDestinationType as FuncKeyDestinationTypeSchema


class FuncKey(NewModel):

    MANDATORY = [
        'type',
        'destination',
        'destination_id',
    ]

    FIELDS = [
        'id',
        'type',
        'destination',
        'destination_id',
    ]

    _RELATION = {}


class DestinationType(object):
    user = 'user'
    group = 'group'

    all_types = [user, group]

    @classmethod
    def exists(cls, name):
        return name in cls.all_types


class DbHelper(object):
    id = FuncKeySchema.id.label('id')
    type = FuncKeyTypeSchema.name.label('type')
    destination = FuncKeyDestinationTypeSchema.name.label('destination')
    destination_id = func.coalesce(FuncKeyDestUserSchema.user_id,
                                   FuncKeyDestGroupSchema.group_id
                                   ).label('destination_id')

    search_columns = [type, destination, destination_id]

    destination_schemas = {
        'user': (FuncKeyDestUserSchema, FuncKeyDestUserSchema.user_id),
        'group': (FuncKeyDestGroupSchema, FuncKeyDestGroupSchema.group_id)
    }

    @classmethod
    def schema_and_column(cls, dest_type):
        return cls.destination_schemas.get(dest_type, (None, None))

    @classmethod
    def view_query(cls, session):
        query = (session
                 .query(cls.id, cls.type, cls.destination, cls.destination_id)
                 .join(FuncKeyTypeSchema)
                 .join(FuncKeyDestinationTypeSchema)
                 .outerjoin(FuncKeyDestUserSchema, FuncKeyDestUserSchema.func_key_id == FuncKeySchema.id)
                 .outerjoin(FuncKeyDestGroupSchema, FuncKeyDestGroupSchema.func_key_id == FuncKeySchema.id)
                 .filter(cls.destination_id != None))
        return query


class FuncKeyOrder(object):
    id = DbHelper.id
    type = DbHelper.type
    destination = DbHelper.destination
    destination_id = DbHelper.destination_id


class FuncKeyDbConverter(DatabaseConverter):

    DB_TO_MODEL_MAPPING = {
        'id': 'id',
        'type': 'type',
        'destination': 'destination',
        'destination_id': 'destination_id',
    }

    def __init__(self):
        DatabaseConverter.__init__(self,
                                   self.DB_TO_MODEL_MAPPING,
                                   FuncKeySchema,
                                   FuncKey)

    def create_func_key_row(self, model):
        destination_type_row = func_key_type_dao.find_destination_type_for_name(model.destination)
        type_row = func_key_type_dao.find_type_for_name(model.type)

        func_key_row = FuncKeySchema(type_id=type_row.id,
                                     destination_type_id=destination_type_row.id)

        return func_key_row

    def create_destination_row(self, model):
        destination_type_row = func_key_type_dao.find_destination_type_for_name(model.destination)

        if model.destination == DestinationType.user:
            return FuncKeyDestUserSchema(destination_type_id=destination_type_row.id,
                                         user_id=model.destination_id,
                                         func_key_id=model.id)
        elif model.destination == DestinationType.group:
            return FuncKeyDestGroupSchema(destination_type_id=destination_type_row.id,
                                          group_id=model.destination_id,
                                          func_key_id=model.id)


db_converter = FuncKeyDbConverter()
