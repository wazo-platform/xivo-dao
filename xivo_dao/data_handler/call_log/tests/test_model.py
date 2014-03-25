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

from hamcrest import assert_that, contains
from mock import Mock
from unittest import TestCase

from xivo_dao.data_handler.call_log.model import CallLog


class TestCallLogModel(TestCase):

    def setUp(self):
        self.call_log = CallLog()

    def tearDown(self):
        pass

    def test_get_related_cels_empty(self):
        result = self.call_log.get_related_cels()

        assert_that(result, contains())

    def test_add_then_get_related_cel(self):
        cel_id_1, cel_id_2, cel_id_3 = Mock(), Mock(), Mock()

        self.call_log.add_related_cels([cel_id_1, cel_id_2])
        result = self.call_log.get_related_cels()
        assert_that(result, contains(cel_id_1, cel_id_2))

        self.call_log.add_related_cels([cel_id_3])
        result = self.call_log.get_related_cels()
        assert_that(result, contains(cel_id_1, cel_id_2, cel_id_3))
