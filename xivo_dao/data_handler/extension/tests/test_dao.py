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

from hamcrest import assert_that, all_of, equal_to, has_items, has_length, has_property, none
from mock import patch, Mock
from sqlalchemy.exc import SQLAlchemyError

from xivo_dao.alchemy.extension import Extension as ExtensionSchema
from xivo_dao.data_handler.utils.search import SearchResult
from xivo_dao.data_handler.exception import ElementCreationError
from xivo_dao.data_handler.exception import ElementEditionError
from xivo_dao.data_handler.extension import dao as extension_dao
from xivo_dao.data_handler.extension.model import Extension, ExtensionDestination
from xivo_dao.tests.test_dao import DAOTestCase


class TestExtension(DAOTestCase):

    def prepare_extension(self, **kwargs):
        extension_row = self.add_extension(**kwargs)
        return Extension(id=extension_row.id,
                         exten=extension_row.exten,
                         context=extension_row.context,
                         commented=bool(extension_row.commented))

    def assert_search_returns_result(self, search_result, **parameters):
        result = extension_dao.search(**parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestExtension):

    def setUp(self):
        TestExtension.setUp(self)

    def test_given_no_extensions_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_one_commented_extension_then_returns_one_result(self):
        extension = self.prepare_extension(exten='1000', commented=1)
        expected = SearchResult(1, [extension])

        self.assert_search_returns_result(expected)


class TestSearchGivenMultipleExtensions(TestExtension):

    def setUp(self):
        TestExtension.setUp(self)
        self.extension1 = self.prepare_extension(exten='1000')
        self.extension2 = self.prepare_extension(exten='1001')
        self.extension3 = self.prepare_extension(exten='1002')
        self.extension4 = self.prepare_extension(exten='1103')

    def test_when_searching_then_returns_one_result(self):
        expected = SearchResult(1, [self.extension2])

        self.assert_search_returns_result(expected, search='1001')

    def test_when_sorting_then_returns_result_in_ascending_order(self):
        expected = SearchResult(4, [self.extension1, self.extension2, self.extension3, self.extension4])

        self.assert_search_returns_result(expected, order='exten')

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(self):
        expected = SearchResult(4, [self.extension4, self.extension3, self.extension2, self.extension1])

        self.assert_search_returns_result(expected, order='exten', direction='desc')

    def test_when_limiting_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.extension1])

        self.assert_search_returns_result(expected, limit=1)

    def test_when_skipping_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.extension2, self.extension3, self.extension4])

        self.assert_search_returns_result(expected, skip=1)

    def test_when_doing_a_paginated_search_then_returns_a_paginated_result(self):
        expected = SearchResult(3, [self.extension2])

        self.assert_search_returns_result(expected,
                                          search='100',
                                          order='exten',
                                          direction='desc',
                                          skip=1,
                                          limit=1)


class TestSearchGivenInternalExtensionType(TestExtension):

    def setUp(self):
        TestExtension.setUp(self)

        self.add_context(name='internal_context', contexttype='internal')
        self.extension1 = self.prepare_extension(exten='1000', context='internal_context')
        self.extension2 = self.prepare_extension(exten='1001', context='internal_context')

    def test_when_searching_type_internal_extensions_then_returns_internal_extensions(self):
        expected = SearchResult(2, [self.extension1, self.extension2])

        self.assert_search_returns_result(expected, type='internal')

    def test_when_searching_type_internal_and_limit_then_returns_internal_extensions(self):
        expected = SearchResult(2, [self.extension1])

        self.assert_search_returns_result(expected, type='internal', limit=1)

    def test_when_searching_type_incall_then_returns_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected, type='incall')


class TestSearchGivenIncallExtensionType(TestExtension):

    def setUp(self):
        TestExtension.setUp(self)

        self.add_context(name='incall_context', contexttype='incall')
        self.extension1 = self.prepare_extension(exten='1000', context='incall_context')
        self.extension2 = self.prepare_extension(exten='1001', context='incall_context')

    def test_when_searching_type_internal_then_returns_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected, type='internal')

    def test_when_searching_type_incall_then_returns_incall_extensions(self):
        expected = SearchResult(2, [self.extension1, self.extension2])

        self.assert_search_returns_result(expected, type='incall')

    def test_when_searching_type_incall_and_limit_then_returns_interal_extensions(self):
        expected = SearchResult(2, [self.extension1])

        self.assert_search_returns_result(expected, type='incall', limit=1)


class TestFind(DAOTestCase):

    def test_find_no_extension(self):
        result = extension_dao.find(1)

        assert_that(result, none())

    def test_find(self):
        extension_row = self.add_extension(exten='1234', context='default')

        result = extension_dao.find(extension_row.id)

        assert_that(result, all_of(
            has_property('exten', extension_row.exten),
            has_property('context', extension_row.context)))


class TestFindByExten(DAOTestCase):

    def test_find_by_exten_no_extens(self):
        expected = []
        extens = extension_dao.find_by_exten('123')

        assert_that(extens, equal_to(expected))

    def test_find_by_exten(self):
        expected_exten = '1234'

        exten = self.add_extension(exten=expected_exten)
        self.add_extension(exten='1236')
        self.add_extension(exten='8652')

        extens = extension_dao.find_by_exten(expected_exten)

        assert_that(extens, has_length(1))
        assert_that(extens, has_items(
            all_of(
                has_property('id', exten.id),
                has_property('exten', expected_exten))
        ))


class TestFindByContext(DAOTestCase):

    def test_find_by_context_no_extens(self):
        expected = []
        extens = extension_dao.find_by_context('fuh')

        assert_that(extens, equal_to(expected))

    def test_find_by_context(self):
        expected_context = 'hhi'

        exten = self.add_extension(context=expected_context)
        self.add_extension(context='guj')
        self.add_extension(context='asc')

        extens = extension_dao.find_by_context(expected_context)

        assert_that(extens, has_length(1))
        assert_that(extens, has_items(
            all_of(
                has_property('id', exten.id),
                has_property('context', expected_context))
        ))


class TestGet(DAOTestCase):

    def test_get_no_exist(self):
        self.assertRaises(LookupError, extension_dao.get, 666)

    def test_get(self):
        exten = 'sdklfj'

        expected_extension = self.add_extension(exten=exten)

        extension = extension_dao.get(expected_extension.id)

        assert_that(extension.exten, equal_to(exten))


class TestGetByExten(DAOTestCase):

    def test_get_by_exten_context_no_exist(self):
        self.assertRaises(LookupError, extension_dao.get_by_exten_context, '1234', 'default')

    def test_get_by_exten_context(self):
        exten = 'sdklfj'
        context = 'toto'

        expected_extension = self.add_extension(exten=exten,
                                                context=context)

        extension = extension_dao.get_by_exten_context(exten, context)

        assert_that(extension.id, equal_to(expected_extension.id))
        assert_that(extension.exten, equal_to(exten))
        assert_that(extension.context, equal_to(context))


class TestFindByExtenContext(DAOTestCase):

    def test_find_by_exten_context_no_extensions(self):
        expected = None
        result = extension_dao.find_by_exten_context('1000', 'default')

        assert_that(expected, equal_to(result))

    def test_find_by_exten_context_one_extension(self):
        exten = 'sdklfj'
        context = 'toto'
        extension_row = self.add_extension(exten=exten,
                                           context=context)

        result = extension_dao.find_by_exten_context(exten, context)

        assert_that(result, all_of(
            has_property('id', extension_row.id),
            has_property('exten', exten),
            has_property('context', context)
        ))


class TestCreate(DAOTestCase):

    def test_create(self):
        exten = 'extension'
        context = 'toto'
        commented = True

        extension = Extension(exten=exten,
                              context=context,
                              commented=commented)

        created_extension = extension_dao.create(extension)

        row = self.session.query(ExtensionSchema).filter(ExtensionSchema.id == created_extension.id).first()

        assert_that(row.id, equal_to(created_extension.id))
        assert_that(row.exten, equal_to(exten))
        assert_that(row.context, equal_to(context))
        assert_that(row.commented, equal_to(1))
        assert_that(row.type, equal_to('user'))
        assert_that(row.typeval, equal_to('0'))

    def test_create_same_exten_and_context(self):
        exten = 'extension'
        context = 'toto'

        extension = Extension(exten=exten,
                              context=context)

        extension_dao.create(extension)

        extension = Extension(exten=exten,
                              context=context)

        self.assertRaises(ElementCreationError, extension_dao.create, extension)

    @patch('xivo_dao.helpers.db_manager.DaoSession')
    def test_create_extension_with_error_from_dao(self, Session):
        session = Mock()
        session.commit.side_effect = SQLAlchemyError()
        Session.return_value = session

        exten = 'extension'
        context = 'toto'

        extension = Extension(exten=exten,
                              context=context)

        self.assertRaises(ElementCreationError, extension_dao.create, extension)
        session.begin.assert_called_once_with()
        session.rollback.assert_called_once_with()


class TestEdit(DAOTestCase):

    def setUp(self):
        DAOTestCase.setUp(self)
        self.existing_extension = self.add_extension(exten='1635', context='my_context', type='user', typeval='0')

    def test_edit(self):
        exten = 'extension'
        context = 'toto'
        commented = True

        extension = Extension(id=self.existing_extension.id,
                              exten=exten,
                              context=context,
                              commented=commented)

        extension_dao.edit(extension)

        row = self.session.query(ExtensionSchema).get(extension.id)

        assert_that(row.id, equal_to(extension.id))
        assert_that(row.exten, equal_to(exten))
        assert_that(row.context, equal_to(context))
        assert_that(row.commented, equal_to(1))
        assert_that(row.type, equal_to('user'))
        assert_that(row.typeval, equal_to('0'))

    @patch('xivo_dao.helpers.db_manager.DaoSession')
    def test_edit_extension_with_error_from_dao(self, Session):
        session = Mock()
        session.commit.side_effect = SQLAlchemyError()
        Session.return_value = session

        extension = Extension(exten='extension',
                              context='context')

        self.assertRaises(ElementEditionError, extension_dao.edit, extension)
        session.begin.assert_called_once_with()
        session.rollback.assert_called_once_with()


class TestDelete(DAOTestCase):

    def test_delete(self):
        exten = 'sdklfj'
        context = 'toto'

        expected_extension = self.add_extension(exten=exten,
                                                context=context)

        extension = extension_dao.get(expected_extension.id)

        extension_dao.delete(extension)

        row = self.session.query(ExtensionSchema).filter(ExtensionSchema.id == expected_extension.id).first()

        self.assertEquals(row, None)


class TestAssociateDestination(DAOTestCase):

    def test_associate_to_user(self):
        extension_row = self.add_extension()
        user_row = self.add_user()

        extension_dao.associate_destination(extension_row.id, ExtensionDestination.user, user_row.id)

        self.assert_extension_is_associated_to_user(user_row, extension_row)

    def test_associate_to_incall(self):
        extension_row = self.add_extension()
        incall_row = self.add_incall()

        extension_dao.associate_destination(extension_row.id, ExtensionDestination.incall, incall_row.id)

        self.assert_extension_is_associated_to_incall(incall_row, extension_row)

    @patch('xivo_dao.helpers.db_manager.DaoSession')
    def test_associate_to_user_with_database_error(self, Session):
        session = Session.return_value = Mock()
        session.commit.side_effect = SQLAlchemyError()

        extension_row = Mock()
        user_row = Mock()

        self.assertRaises(ElementEditionError,
                          extension_dao.associate_destination,
                          extension_row.id,
                          'user',
                          user_row.id)

        session.commit.assert_called_once_with()
        session.rollback.assert_called_once_with()

    def assert_extension_is_associated_to_user(self, user_row, extension_row):
        updated_extension = self.session.query(ExtensionSchema).get(extension_row.id)
        assert_that(updated_extension.type, equal_to('user'))
        assert_that(updated_extension.typeval, equal_to(str(user_row.id)))

    def assert_extension_is_associated_to_incall(self, incall_row, extension_row):
        updated_extension = self.session.query(ExtensionSchema).get(extension_row.id)
        assert_that(updated_extension.type, equal_to('incall'))
        assert_that(updated_extension.typeval, equal_to(str(incall_row.id)))


class TestDissociateExtension(DAOTestCase):

    def test_dissociate_extension(self):
        extension_row = self.add_extension(type='user', typeval='1234')

        extension_dao.dissociate_extension(extension_row.id)

        self.assert_extension_not_associated(extension_row.id)

    @patch('xivo_dao.helpers.db_manager.DaoSession')
    def test_dissociate_extension_with_database_error(self, Session):
        session = Mock()
        session.commit.side_effect = SQLAlchemyError()
        Session.return_value = session

        extension_id = 1

        self.assertRaises(ElementEditionError, extension_dao.dissociate_extension, extension_id)

    def assert_extension_not_associated(self, extension_id):
        updated_extension = self.session.query(ExtensionSchema).get(extension_id)
        assert_that(updated_extension.type, equal_to('user'))
        assert_that(updated_extension.typeval, equal_to('0'))
