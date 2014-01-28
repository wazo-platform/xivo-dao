# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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
from xivo_dao.data_handler.configuration import services
from mock import patch


class TestConfiguration(unittest.TestCase):

    @patch('xivo_dao.data_handler.configuration.dao.get_live_reload_status')
    def test_find_by_name_inexistant(self, get_live_reload_status):
        get_live_reload_status.return_value = False

        result = services.get_live_reload_status()

        self.assertFalse(result)
        get_live_reload_status.assert_called_once_with()
