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

from xivo_dao.tests.test_case import TestCase
from xivo_dao.data_handler.user.model import User
from xivo_dao.data_handler.func_key.model import FuncKey
from xivo_dao.data_handler.func_key import destination

from mock import patch, Mock, sentinel


class TestCreateUserDestination(TestCase):

    @patch('xivo_dao.data_handler.func_key.dao.create')
    def test_create_user_destination(self,
                                     dao_create):
        user = Mock(User, id=1)

        expected_func_key = FuncKey(type='speeddial',
                                    destination='user',
                                    destination_id=user.id)

        destination.create_user_destination(user)

        dao_create.assert_called_once_with(expected_func_key)


class TestDeleteUserDestination(TestCase):

    @patch('xivo_dao.data_handler.func_key.dao.delete')
    @patch('xivo_dao.data_handler.func_key_template.dao.remove_func_key_from_templates')
    @patch('xivo_dao.data_handler.func_key.dao.find_all_by_destination')
    def test_delete_user_destination(self,
                                     find_all_by_destination,
                                     remove_func_key_from_templates,
                                     dao_delete):
        user = Mock(User, id=sentinel.user_id)

        first_func_key = Mock(FuncKey)
        second_func_key = Mock(FuncKey)
        find_all_by_destination.return_value = [first_func_key, second_func_key]

        destination.delete_user_destination(user)

        find_all_by_destination.assert_called_once_with('user', sentinel.user_id)
        dao_delete.assert_any_call(first_func_key)
        dao_delete.assert_any_call(second_func_key)
        remove_func_key_from_templates.assert_any_call(first_func_key)
        remove_func_key_from_templates.assert_any_call(second_func_key)
