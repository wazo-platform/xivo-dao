# -*- coding: utf-8 -*-
#
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

from hamcrest import *
from mock import Mock

from xivo_dao.converters.database_converter import DatabaseConverter


class TestDatabaseConverterToModel(unittest.TestCase):

    def setUp(self):
        self.Schema = Mock()
        self.Model = Mock()
        self.model = self.Model.return_value = Mock()

    def test_to_model_empty_mapping(self):
        mapping = {}

        db_row = Mock()

        converter = DatabaseConverter(mapping, self.Schema, self.Model)
        result = converter.to_model(db_row)

        self.Model.assert_called_once_with()
        assert_that(result, same_instance(self.model))

    def test_to_model(self):
        value = 'value'

        mapping = {'db_field': 'model_field'}

        db_row = Mock()
        db_row.db_field = value

        converter = DatabaseConverter(mapping, self.Schema, self.Model)
        result = converter.to_model(db_row)

        self.Model.assert_called_once_with(model_field=value)
        assert_that(result, same_instance(self.model))

    def test_to_model_with_nonexistent_column(self):
        value = 'value'

        mapping = {
            'db_field': 'model_field',
            'does_not_exist': 'does_not_exist',
        }

        db_row = Mock()
        db_row.db_field = value
        del db_row.does_not_exist

        converter = DatabaseConverter(mapping, self.Schema, self.Model)

        self.assertRaises(ValueError, converter.to_model, db_row)


class TestDatabaseConverterToSource(unittest.TestCase):

    def setUp(self):
        self.Schema = Mock()
        self.Model = Mock()
        self.db_row = self.Schema.return_value = Mock()

    def test_to_source_empty_mapping(self):
        mapping = {}

        model = Mock()

        converter = DatabaseConverter(mapping, self.Schema, self.Model)
        result = converter.to_source(model)

        self.Schema.assert_called_once_with()
        assert_that(result, same_instance(self.db_row))

    def test_to_source(self):
        value = 'value'
        mapping = {'db_field': 'model_field'}

        model = Mock()
        model.model_field = value

        converter = DatabaseConverter(mapping, self.Schema, self.Model)
        result = converter.to_source(model)

        self.Schema.assert_called_once_with(db_field=value)
        assert_that(result, same_instance(self.db_row))

    def test_to_source_with_nonexistent_column(self):
        value = 'value'
        mapping = {
            'db_field': 'model_field',
            'does_not_exist': 'does_not_exist'
        }

        model = Mock()
        model.model_field = value
        del model.does_not_exist

        converter = DatabaseConverter(mapping, self.Schema, self.Model)

        self.assertRaises(ValueError, converter.to_source, model)


class TestDatabaseConverterUpdateModel(unittest.TestCase):

    def setUp(self):
        self.Schema = Mock()
        self.Model = Mock()

    def test_update_model(self):
        value = 'value'

        mapping = {
            'db_field': 'model_field'
        }

        db_row = Mock()
        db_row.db_field = value

        model = Mock()

        converter = DatabaseConverter(mapping, self.Schema, self.Model)
        converter.update_model(model, db_row)

        assert_that(model.model_field, equal_to(value))


class TestDatabaseConverterUpdateSource(unittest.TestCase):

    def setUp(self):
        self.Schema = Mock()
        self.Model = Mock()

    def test_update_source(self):
        value = 'value'

        mapping = {
            'db_field': 'model_field'
        }

        db_row = Mock()

        model = Mock()
        model.model_field = value

        converter = DatabaseConverter(mapping, self.Schema, self.Model)
        converter.update_source(db_row, model)

        assert_that(db_row.db_field, equal_to(value))

    def test_update_source_nothing_to_update(self):
        value = 'value'

        mapping = {
            'db_field': 'model_field'
        }

        db_row = Mock()
        db_row.db_field = value

        model = Mock()
        del model.model_field

        converter = DatabaseConverter(mapping, self.Schema, self.Model)
        converter.update_model(db_row, model)

        assert_that(db_row.db_field, equal_to(value))
