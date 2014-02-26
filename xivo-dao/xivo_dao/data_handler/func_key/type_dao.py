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

from xivo_dao.alchemy.func_key_type import FuncKeyType as FuncKeyTypeSchema
from xivo_dao.alchemy.func_key_destination_type import FuncKeyDestinationType as FuncKeyDestinationTypeSchema

from xivo_dao.helpers.db_manager import daosession


@daosession
def find_type_for_name(session, name):
    return _find_using_name(session, FuncKeyTypeSchema, name)


@daosession
def find_destination_type_for_name(session, name):
    return _find_using_name(session, FuncKeyDestinationTypeSchema, name)


def _find_using_name(session, schema, name):
    return (session.query(schema)
            .filter(schema.name == name)
            .first())
