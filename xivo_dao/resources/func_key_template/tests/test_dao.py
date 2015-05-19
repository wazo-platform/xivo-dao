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

from hamcrest import assert_that, is_not, none, has_property, equal_to
from mock import patch, ANY, Mock

from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.alchemy.func_key_template import FuncKeyTemplate as FuncKeyTemplateSchema
from xivo_dao.alchemy.func_key_mapping import FuncKeyMapping as FuncKeyMappingSchema

from xivo_dao.helpers.exception import DataError
from xivo_dao.resources.func_key_template import dao
from xivo_dao.resources.func_key.model import UserFuncKey


class TestFuncKeyTemplateDao(DAOTestCase):

    def setUp(self):
        DAOTestCase.setUp(self)
        func_key_type_row = self.add_func_key_type(name='speeddial')
        destination_type_row = self.add_func_key_destination_type(id=1, name='user')

        self.type_id = func_key_type_row.id
        self.destination_type_id = destination_type_row.id

    def assert_template_empty(self, template_row):
        count = (self.session.query(FuncKeyMappingSchema)
                 .filter(FuncKeyMappingSchema.template_id == template_row.id)
                 .count())

        assert_that(count, equal_to(0))

    def create_func_key_for_template(self, template_row, position):
        func_key_row = self.add_func_key(type_id=self.type_id,
                                         destination_type_id=self.destination_type_id)

        mapping_row = FuncKeyMappingSchema(template_id=template_row.id,
                                           func_key_id=func_key_row.id,
                                           destination_type_id=func_key_row.destination_type_id,
                                           position=position)
        self.add_me(mapping_row)

        return UserFuncKey(id=func_key_row.id)


class TestCreatePrivateTemplate(TestFuncKeyTemplateDao):

    def test_create_private_template(self):
        template_id = dao.create_private_template()

        self.assert_private_template_created(template_id)

    def assert_private_template_created(self, template_id):
        template_row = self.session.query(FuncKeyTemplateSchema).get(template_id)
        assert_that(template_row, is_not(none()))

        assert_that(template_row, has_property('private', True))
        assert_that(template_row, has_property('name', none()))

    @patch('xivo_dao.resources.func_key_template.dao.commit_or_abort')
    def test_given_database_error_then_transaction_aborted(self, commit_or_abort):
        dao.create_private_template()

        commit_or_abort.assert_called_with(ANY, DataError.on_create, 'FuncKeyTemplate')


class TestRemoveFuncKeyFromTemplate(TestFuncKeyTemplateDao):

    def test_given_one_func_key_mapped_when_removed_then_template_empty(self):
        template_row = self.add_func_key_template()
        func_key = self.create_func_key_for_template(template_row, 1)

        dao.remove_func_key_from_templates(func_key)

        self.assert_template_empty(template_row)

    def test_given_two_func_keys_mapped_when_first_removed_then_other_func_key_remains(self):
        template_row = self.add_func_key_template()
        first_func_key = self.create_func_key_for_template(template_row, 1)
        second_func_key = self.create_func_key_for_template(template_row, 2)

        dao.remove_func_key_from_templates(first_func_key)

        self.assert_template_contains_func_key(template_row, second_func_key)

    @patch('xivo_dao.resources.func_key_template.dao.commit_or_abort')
    def test_given_database_error_then_transaction_aborted(self, commit_or_abort):
        func_key = Mock(id=1)
        dao.remove_func_key_from_templates(func_key)

        commit_or_abort.assert_called_with(ANY, DataError.on_delete, 'FuncKeyTemplate')

    def assert_template_contains_func_key(self, template_row, func_key_row):
        count = (self.session.query(FuncKeyMappingSchema)
                 .filter(FuncKeyMappingSchema.template_id == template_row.id)
                 .filter(FuncKeyMappingSchema.func_key_id == func_key_row.id)
                 .count())

        assert_that(count, equal_to(1))


class TestDeletePrivateTemplate(TestFuncKeyTemplateDao):

    def test_given_empty_template_then_template_deleted(self):
        template_row = self.add_func_key_template(private=True)

        dao.delete_private_template(template_row.id)

        self.assert_template_deleted(template_row)

    def test_given_template_with_one_func_key_then_template_and_mapping_deleted(self):
        template_row = self.add_func_key_template(private=True)
        self.create_func_key_for_template(template_row, 1)

        dao.delete_private_template(template_row.id)

        self.assert_template_deleted(template_row)
        self.assert_template_empty(template_row)

    def assert_template_deleted(self, template_row):
        row = self.session.query(FuncKeyTemplateSchema).get(template_row.id)
        assert_that(row, none())

    @patch('xivo_dao.resources.func_key_template.dao.commit_or_abort')
    def test_given_database_error_then_transaction_aborted(self, commit_or_abort):
        template_id = 1
        dao.delete_private_template(template_id)

        commit_or_abort.assert_called_with(ANY, DataError.on_delete, 'FuncKeyTemplate')
