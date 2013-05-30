# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

from mock import Mock
from hamcrest import assert_that
from hamcrest.core import equal_to
from xivo_dao.models.line import Line


class TestLine(unittest.TestCase):

    def test_equal_type_mismatch(self):
        line_1 = Line(
            name='test',
        )

        self.assertRaises(TypeError, lambda: line_1 == 'Not a line')

    def test_equal_same(self):
        name = 'samename'
        line_1 = Line(name=name)
        line_2 = Line(name=name)

        assert_that(line_1, equal_to(line_2))

    def test_from_data_source(self):
        properties = Mock()
        properties.number = number = '42'
        properties.context = context = 'default'
        properties.protocol = protocol = 'sip'
        properties.name = name = 'abswef'
        properties.iduserfeatures = iduserfeatures = 103

        line = Line.from_data_source(properties)

        assert_that(line.name, equal_to(name), 'Name')
        assert_that(line.number, equal_to(number), 'Number')
        assert_that(line.context, equal_to(context), 'Context')
        assert_that(line.protocol, equal_to(protocol), 'Protocol')
        assert_that(line.iduserfeatures, equal_to(iduserfeatures), 'ID User Features')

    def test_from_user_data(self):
        data = {
            'name': 'aname',
            'number': '1234',
            'context': 'notdefault',
            'protocol': 'sip',
        }

        line = Line.from_user_data(data)

        assert_that(line.name, equal_to(data['name']), 'Name')
        assert_that(line.number, equal_to(data['number']), 'Number')
        assert_that(line.context, equal_to(data['context']), 'Context')
        assert_that(line.protocol, equal_to(data['protocol']), 'Protocol')
