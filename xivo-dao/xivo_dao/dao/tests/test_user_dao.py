# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 Avencall
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

import unittest

from mock import Mock, patch
from xivo_dao.dao import user_dao
from xivo_dao.models.user import User


class TestUserDAO(unittest.TestCase):

    @patch('xivo_dao.user_dao.get')
    def test_get_user_by_id_inexistant(self, mock_get):
        user_id = 42
        mock_get.side_effect = LookupError()

        self.assertRaises(LookupError, user_dao.get_user_by_id, user_id)

    @patch('xivo_dao.user_dao.get')
    def test_get_user_by_id(self, mock_get):
        user_id = 42
        expected_user = User()
        expected_user.id = user_id
        mock_user_row = Mock()
        mock_user_row.id = user_id
        mock_get.return_value = mock_user_row

        user = user_dao.get_user_by_id(user_id)

        self.assertEquals(expected_user.id, user.id)
