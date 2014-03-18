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

from xivo_dao.data_handler.func_key import dao as func_key_dao
from xivo_dao.data_handler.func_key_template import dao as template_dao
from xivo_dao.data_handler.func_key.model import FuncKey


def create_user_destination(user):
    func_key = FuncKey(type='speeddial',
                       destination='user',
                       destination_id=user.id)
    func_key_dao.create(func_key)


def delete_user_destination(user):
    func_keys = func_key_dao.find_all_by_destination('user', user.id)
    for func_key in func_keys:
        template_dao.remove_func_key_from_templates(func_key)
        func_key_dao.delete(func_key)
