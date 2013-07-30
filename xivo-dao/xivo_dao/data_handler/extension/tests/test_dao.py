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

from hamcrest import assert_that
from hamcrest.core import equal_to
from mock import patch, Mock

from xivo_dao.data_handler.extension import dao as extension_dao
from xivo_dao.tests.test_dao import DAOTestCase
from sqlalchemy.exc import SQLAlchemyError
from xivo_dao.data_handler.exception import ElementCreationError, \
    ElementDeletionError
from xivo_dao.data_handler.extension.model import Extension
from xivo_dao.alchemy.extension import Extension as ExtensionSchema
from hamcrest.library.object.haslength import has_length
from hamcrest.library.object.hasproperty import has_property
from hamcrest.library.collection.issequence_containing import has_items
from hamcrest.core.core.allof import all_of


class TestExtensionDao(DAOTestCase):

    tables = [
        ExtensionSchema
    ]

    def setUp(self):
        self.empty_tables()

    def test_find_all_no_extens(self):
        expected = []
        extens = extension_dao.find_all()

        assert_that(extens, equal_to(expected))

    def test_find_all_one_exten(self):
        expected_exten = '12345'
        exten = self.add_extension(exten=expected_exten)

        extens = extension_dao.find_all()

        assert_that(extens, has_length(1))
        exten_found = extens[0]
        assert_that(exten_found, has_property('id', exten.id))
        assert_that(exten_found, has_property('exten', expected_exten))

    def test_find_all_two_extens(self):
        expected_exten1 = '1234'
        expected_exten2 = '5678'

        exten1 = self.add_extension(exten=expected_exten1)
        exten2 = self.add_extension(exten=expected_exten2)

        extens = extension_dao.find_all()

        assert_that(extens, has_length(2))
        assert_that(extens, has_items(
            all_of(
                has_property('id', exten1.id),
                has_property('exten', expected_exten1)),
            all_of(
                has_property('id', exten2.id),
                has_property('exten', expected_exten2))
        ))

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

    def test_get_no_exist(self):
        self.assertRaises(LookupError, extension_dao.get, 666)

    def test_get(self):
        exten = 'sdklfj'

        expected_extension = self.add_extension(exten=exten)

        extension = extension_dao.get(expected_extension.id)

        assert_that(extension.exten, equal_to(exten))

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

    def test_test_get_by_type_typeval_no_exist(self):
        self.assertRaises(LookupError, extension_dao.get_by_type_typeval, 'user', '1')

    def test_get_by_type_typeval(self):
        exten = 'sdklfj'
        context = 'toto'
        type = 'user'
        typeval = '2'

        expected_extension = self.add_extension(exten=exten,
                                                context=context,
                                                type=type,
                                                typeval=typeval)

        extension = extension_dao.get_by_type_typeval(type, typeval)

        assert_that(extension.id, equal_to(expected_extension.id))
        assert_that(extension.exten, equal_to(exten))
        assert_that(extension.context, equal_to(context))
        assert_that(extension.type, equal_to(type))
        assert_that(extension.typeval, equal_to(typeval))

    def test_create(self):
        exten = 'extension'
        context = 'toto'
        type = 'user'
        typeval = '4'

        extension = Extension(exten=exten,
                              context=context,
                              type=type,
                              typeval=typeval)

        created_extension = extension_dao.create(extension)

        row = self.session.query(ExtensionSchema).filter(ExtensionSchema.id == created_extension.id).first()

        assert_that(row.id, equal_to(created_extension.id))
        assert_that(row.exten, equal_to(exten))
        assert_that(row.context, equal_to(context))
        assert_that(row.type, equal_to(type))
        assert_that(row.typeval, equal_to(typeval))

    def test_create_same_exten_and_context(self):
        exten = 'extension'
        context = 'toto'

        extension = Extension(exten=exten,
                              context=context,
                              type='user')

        extension_dao.create(extension)

        extension = Extension(exten=exten,
                              context=context,
                              type='user')

        self.assertRaises(ElementCreationError, extension_dao.create, extension)

    @patch('xivo_dao.helpers.db_manager.AsteriskSession')
    def test_create_extension_with_error_from_dao(self, Session):
        session = Mock()
        session.commit.side_effect = SQLAlchemyError()
        Session.return_value = session

        exten = 'extension'
        context = 'toto'

        extension = Extension(exten=exten,
                              context=context,
                              type='user')

        self.assertRaises(ElementCreationError, extension_dao.create, extension)
        session.begin.assert_called_once_with()
        session.rollback.assert_called_once_with()

    def test_delete(self):
        exten = 'sdklfj'
        context = 'toto'
        type = 'user'
        typeval = '2'

        expected_extension = self.add_extension(exten=exten,
                                                context=context,
                                                type=type,
                                                typeval=typeval)

        extension = extension_dao.get(expected_extension.id)

        extension_dao.delete(extension)

        row = self.session.query(ExtensionSchema).filter(ExtensionSchema.id == expected_extension.id).first()

        self.assertEquals(row, None)

    def test_delete_not_exist(self):
        extension = Extension(id=1)

        self.assertRaises(ElementDeletionError, extension_dao.delete, extension)
