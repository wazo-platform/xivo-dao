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

from hamcrest import assert_that, equal_to, instance_of, has_property, all_of, none

from xivo_dao.tests.test_dao import DAOTestCase

from xivo_dao.alchemy.context import Context as ContextSchema
from xivo_dao.alchemy.contextnumbers import ContextNumbers as ContextNumberSchema

from xivo_dao.data_handler.context.model import Context, ContextType, ContextRange
from xivo_dao.data_handler.context import dao as context_dao
from xivo_dao.data_handler.exception import NotFoundError
from xivo_dao.helpers.db_utils import commit_or_abort


class TestContextDao(DAOTestCase):

    def _insert_contextnumber(self, **kwargs):
        context_number = ContextNumberSchema(**kwargs)

        with commit_or_abort(self.session):
            self.session.add(context_number)


class TestContextGet(TestContextDao):

    def test_given_no_context_then_raises_error(self):
        self.assertRaises(NotFoundError, context_dao.get, 'mycontext')

    def test_given_context_exists_then_returns_context_model(self):
        context_row = self.add_context()

        expected_context = Context(name=context_row.name,
                                   display_name=context_row.displayname,
                                   type=context_row.contexttype,
                                   description=context_row.description)

        result = context_dao.get(context_row.name)

        assert_that(result, equal_to(expected_context))


class TestContextGetByExtensionId(TestContextDao):

    def test_given_no_extension_then_raises_error(self):
        self.assertRaises(NotFoundError, context_dao.get_by_extension_id, 1)

    def test_given_extension_exists_then_returns_associated_context(self):
        context_row = self.add_context()
        extension_row = self.add_extension(context=context_row.name)

        expected_context = Context(name=context_row.name,
                                   display_name=context_row.displayname,
                                   type=context_row.contexttype,
                                   description=context_row.description)

        result = context_dao.get_by_extension_id(extension_row.id)

        assert_that(result, equal_to(expected_context))


class TestContextFindByExtensionId(TestContextDao):

    def test_given_no_extension_then_returns_nothing(self):
        result = context_dao.find_by_extension_id(1)

        assert_that(result, none())

    def test_given_extension_exists_then_returns_associated_context(self):
        context_row = self.add_context()
        extension_row = self.add_extension(context=context_row.name)

        expected_context = Context(name=context_row.name,
                                   display_name=context_row.displayname,
                                   type=context_row.contexttype,
                                   description=context_row.description)

        result = context_dao.find_by_extension_id(extension_row.id)

        assert_that(result, equal_to(expected_context))


class TestContextCreate(TestContextDao):

    def test_create(self):
        entity_name = 'testentity'
        context_name = 'contextname'
        context_type = ContextType.internal

        context = Context(name=context_name,
                          display_name=context_name,
                          type=context_type)

        self.add_entity(name=entity_name)

        created_context = context_dao.create(context)

        context_row = self.session.query(ContextSchema).filter(ContextSchema.name == context_name).first()

        assert_that(created_context, instance_of(Context))

        assert_that(context_row, all_of(
            has_property('name', context_name),
            has_property('displayname', context_name),
            has_property('entity', entity_name),
            has_property('contexttype', context_type),
            has_property('commented', 0),
            has_property('description', '')
        ))


class TestFindAllContextRanges(TestContextDao):

    def test_find_all_context_ranges_no_range(self):
        expected = []

        result = context_dao.find_all_context_ranges('default')

        assert_that(result, equal_to(expected))

    def test_find_all_context_ranges_inexisting_context(self):
        self._insert_contextnumber(context='default',
                                   type='queue',
                                   numberbeg='1000',
                                   numberend='2000',
                                   didlength=0)

        expected = []

        result = context_dao.find_all_context_ranges('othercontext')

        assert_that(result, equal_to(expected))

    def test_find_all_context_ranges_with_one_range(self):
        self._insert_contextnumber(context='default',
                                   type='user',
                                   numberbeg='1000',
                                   numberend='2000',
                                   didlength=0)

        expected = [ContextRange(start='1000', end='2000')]

        result = context_dao.find_all_context_ranges('default')

        assert_that(result, equal_to(expected))

    def test_find_all_context_ranges_with_only_minimum(self):
        self._insert_contextnumber(context='default',
                                   type='user',
                                   numberbeg='1000',
                                   numberend='',
                                   didlength=0)

        expected = [ContextRange(start='1000', end=None)]

        result = context_dao.find_all_context_ranges('default')

        assert_that(result, equal_to(expected))

    def test_find_all_context_ranges_with_two_ranges(self):
        self._insert_contextnumber(context='default',
                                   type='user',
                                   numberbeg='1000',
                                   numberend='1999',
                                   didlength=0)

        self._insert_contextnumber(context='default',
                                   type='user',
                                   numberbeg='2000',
                                   numberend='2999',
                                   didlength=0)

        expected = [ContextRange(start='1000', end='1999'),
                    ContextRange(start='2000', end='2999')]

        result = context_dao.find_all_context_ranges('default')

        assert_that(result, equal_to(expected))

    def test_find_all_context_ranges_with_two_ranges_for_different_types(self):
        self._insert_contextnumber(context='default',
                                   type='user',
                                   numberbeg='1000',
                                   numberend='1999',
                                   didlength=0)

        self._insert_contextnumber(context='default',
                                   type='group',
                                   numberbeg='2000',
                                   numberend='2999',
                                   didlength=0)

        expected = [ContextRange(start='1000', end='1999'),
                    ContextRange(start='2000', end='2999')]

        result = context_dao.find_all_context_ranges('default')

        assert_that(result, equal_to(expected))


class TestFindAllSpecificContextRanges(TestContextDao):

    def test_find_all_specific_context_ranges_no_range(self):
        expected = []

        result = context_dao.find_all_specific_context_ranges('default', 'user')

        assert_that(result, equal_to(expected))

    def test_find_all_specific_context_ranges_inexisting_context(self):
        self._insert_contextnumber(context='default',
                                   type='queue',
                                   numberbeg='1000',
                                   numberend='2000',
                                   didlength=0)

        expected = []

        result = context_dao.find_all_specific_context_ranges('othercontext', 'user')

        assert_that(result, equal_to(expected))

    def test_find_all_specific_context_ranges_wrong_type(self):
        self._insert_contextnumber(context='default',
                                   type='queue',
                                   numberbeg='1000',
                                   numberend='2000',
                                   didlength=0)

        expected = []

        result = context_dao.find_all_specific_context_ranges('default', 'user')

        assert_that(result, equal_to(expected))

    def test_find_all_specific_context_ranges_wrong_context(self):
        self._insert_contextnumber(context='default',
                                   type='queue',
                                   numberbeg='1000',
                                   numberend='2000',
                                   didlength=0)

        expected = []

        result = context_dao.find_all_specific_context_ranges('othercontext', 'user')

        assert_that(result, equal_to(expected))

    def test_find_all_specific_context_ranges_with_one_range(self):
        self._insert_contextnumber(context='default',
                                   type='user',
                                   numberbeg='1000',
                                   numberend='2000',
                                   didlength=0)

        expected = [ContextRange(start='1000', end='2000')]

        result = context_dao.find_all_specific_context_ranges('default', 'user')

        assert_that(result, equal_to(expected))

    def test_find_all_specific_context_ranges_with_only_minimum(self):
        self._insert_contextnumber(context='default',
                                   type='user',
                                   numberbeg='1000',
                                   numberend='',
                                   didlength=0)

        expected = [ContextRange(start='1000')]

        result = context_dao.find_all_specific_context_ranges('default', 'user')

        assert_that(result, equal_to(expected))

    def test_find_all_specific_context_ranges_with_two_ranges(self):
        self._insert_contextnumber(context='default',
                                   type='user',
                                   numberbeg='1000',
                                   numberend='1999',
                                   didlength=0)

        self._insert_contextnumber(context='default',
                                   type='user',
                                   numberbeg='2000',
                                   numberend='2999',
                                   didlength=0)

        expected = [ContextRange(start='1000', end='1999'),
                    ContextRange(start='2000', end='2999')]

        result = context_dao.find_all_specific_context_ranges('default', 'user')

        assert_that(result, equal_to(expected))
