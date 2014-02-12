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

from mock import patch, Mock
from hamcrest import assert_that, equal_to

from xivo_dao.tests.test_case import TestCase
from xivo_dao.data_handler.func_key import services


class TestFuncKeyService(TestCase):

    @patch('xivo_dao.data_handler.func_key.dao.search')
    def test_search(self, dao_search):
        search_result = dao_search.return_value = Mock()
        term = 'term'
        limit = 2
        skip = 1
        order = 'order'
        direction = 'desc'

        result = services.search(term, limit, skip, order, direction)

        dao_search.assert_called_once_with(term, limit, skip, order, direction)
        assert_that(result, equal_to(search_result))
