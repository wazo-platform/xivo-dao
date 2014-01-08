# -*- coding: utf-8 -*-

# Copyright (C) 2007-2014 Avencall
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

from hamcrest import all_of, assert_that, has_entries, has_key, is_not, same_instance
from hamcrest.core import equal_to
from mock import Mock
from xivo_dao.helpers.abstract_model import AbstractModels
from xivo_dao.data_handler.exception import InvalidParametersError
from xivo_dao.data_handler.line.model import Line, LineSIP


class TestModel(AbstractModels):

    MANDATORY = [
        'field1'
    ]

    _MAPPING = {
        'db_field1': 'field1',
        'db_field2': 'field2',
    }

    _RELATION = {
        'db_relation1': 'relation1'
    }


class TestModelsAbstract(unittest.TestCase):

    def test_instance_of_new_class(self):
        value1 = 'value1'
        value2 = 'value2'

        model = TestModel(field1=value1, field2=value2)

        assert_that(model.field1, equal_to(value1))
        assert_that(model.field2, equal_to(value2))

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

    def test_equal(self):
        model1 = TestModel(field1='value1')

        model2 = TestModel(field1='value1')

        model3 = TestModel(field1='value3',
                           field2='value4')

        self.assertRaises(TypeError, lambda: model1 == 12)
        self.assertNotEquals(model1, TestModel())
        self.assertEquals(model1, model1)
        self.assertNotEquals(model1, model3)
        self.assertEquals(model1, model2)

    def test_from_data_source(self):
        properties = Mock()
        properties.db_field1 = 'value1'
        properties.db_field2 = 'value2'
        properties.db_relation1 = 'relation1'

        model = TestModel.from_data_source(properties)

        assert_that(model.field1, equal_to('value1'))
        assert_that(model.field2, equal_to('value2'))
        assert_that(model.relation1, equal_to('relation1'))

    def test_to_data_source(self):
        Source = Mock()
        source_obj = Source.return_value = Mock()

        model = TestModel(field1='value1', field2='value2')

        data_source = model.to_data_source(Source)

        assert_that(source_obj, same_instance(data_source))
        assert_that(data_source.db_field1, equal_to('value1'))
        assert_that(data_source.db_field2, equal_to('value2'))

    def test_from_user_data(self):
        properties = {
            'field1': 'value1',
            'field2': 'value2',
            'relation1': 'relation1',
        }

        model = TestModel.from_user_data(properties)

        assert_that(model.field1, equal_to('value1'))
        assert_that(model.field2, equal_to('value2'))
        assert_that(model.relation1, equal_to('relation1'))

    def test_to_user_data(self):
        line_sip = LineSIP()
        line_sip.private_value = 'private_value'
        provisioning_extension = line_sip.provisioning_extension = '192837'
        username = line_sip.username = 'username'

        line_sip_dict = line_sip.to_user_data()

        assert_that(line_sip_dict, has_entries({
            'provisioning_extension': provisioning_extension,
            'username': username,
        }))
        assert_that(line_sip_dict, all_of(is_not(has_key('private_value')),  # not mapped
                                          is_not(has_key('secret'))))  # not set

    def test_update_from_data(self):
        model = TestModel(field1='value1')

        data_update = {
            'field1': 'updated_value'
        }

        model.update_from_data(data_update)

        assert_that(model.field1, equal_to('updated_value'))

    def test_update_from_data_invalid_properties(self):
        model = TestModel()

        data_update = {
            'toto': 'tata'
        }

        self.assertRaises(InvalidParametersError, model.update_from_data, data_update)
