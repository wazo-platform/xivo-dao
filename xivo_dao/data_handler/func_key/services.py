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

from xivo_dao.data_handler.func_key import dao
from xivo_dao.data_handler.func_key import validator
from xivo_dao.data_handler.func_key import notifier


def search(**parameters):
    return dao.search(**parameters)


def get(func_key_id):
    return dao.get(func_key_id)


def create(func_key):
    validator.validate_create(func_key)
    created_func_key = dao.create(func_key)
    notifier.created(created_func_key)
    return created_func_key


def find_all_hints(context):
    return dao.find_all_hints(context)
