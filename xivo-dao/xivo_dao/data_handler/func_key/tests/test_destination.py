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

from mock import patch, Mock


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
