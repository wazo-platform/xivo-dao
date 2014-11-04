# -*- coding: utf-8 -*-
#
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

import unittest

from mock import patch, Mock

from xivo_dao.data_handler.infos import services as infos_services
from xivo_dao.data_handler.infos.model import Infos


class TestInfos(unittest.TestCase):

    @patch('xivo_dao.data_handler.infos.dao.get')
    def test_search_with_parameters(self, mock_get):
        expected_result = Mock(Infos)
        mock_get.return_value = expected_result

        result = infos_services.get()

        mock_get.assert_called_once_with()

        self.assertEquals(result, expected_result)
