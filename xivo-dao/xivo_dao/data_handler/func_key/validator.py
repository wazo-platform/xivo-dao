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

from xivo_dao.data_handler.exception import InvalidParametersError
from xivo_dao.data_handler.exception import MissingParametersError
from xivo_dao.data_handler.exception import ElementNotExistsError
from xivo_dao.data_handler.exception import NonexistentParametersError
from xivo_dao.data_handler.func_key import type_dao as func_key_type_dao
from xivo_dao.data_handler.user import dao as user_dao


def validate_create(func_key):
    validate_missing_parameters(func_key)
    validate_type(func_key)
    validate_destination(func_key)


def validate_missing_parameters(func_key):
    missing = func_key.missing_parameters()
    if missing:
        raise MissingParametersError(missing)


def validate_type(func_key):
    if not func_key_type_dao.find_type_for_name(func_key.type):
        raise InvalidParametersError(['type %s does not exist' % func_key.type])


def validate_destination(func_key):
    validate_destination_type(func_key)
    validate_destination_exists(func_key)


def validate_destination_type(func_key):
    if not func_key_type_dao.find_destination_type_for_name(func_key.destination):
        raise InvalidParametersError(['destination of type %s does not exist' % func_key.destination])


def validate_destination_exists(func_key):
    try:
        user_dao.get(func_key.destination_id)
    except ElementNotExistsError:
        raise NonexistentParametersError(user=func_key.destination_id)
