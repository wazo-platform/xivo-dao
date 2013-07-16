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


class TestExtensionDao(DAOTestCase):

    tables = [
        ExtensionSchema
    ]

    def setUp(self):
        self.empty_tables()

    def test_get_no_exist(self):
        self.assertRaises(LookupError, extension_dao.get, 666)

    def test_get(self):
        exten = 'sdklfj'

        extension_id = self.add_extension(exten=exten)

        extension = extension_dao.get(extension_id)

        assert_that(extension.exten, equal_to(exten))

    def test_get_by_exten_context_no_exist(self):
        self.assertRaises(LookupError, extension_dao.get_by_exten_context, '1234', 'default')

    def test_get_by_exten_context(self):
        exten = 'sdklfj'
        context = 'toto'

        extension_id = self.add_extension(exten=exten,
                                          context=context)

        extension = extension_dao.get_by_exten_context(exten, context)

        assert_that(extension.id, equal_to(extension_id))
        assert_that(extension.exten, equal_to(exten))
        assert_that(extension.context, equal_to(context))

    def test_test_get_by_type_typeval_no_exist(self):
        self.assertRaises(LookupError, extension_dao.get_by_type_typeval, 'user', '1')

    def test_get_by_type_typeval(self):
        exten = 'sdklfj'
        context = 'toto'
        type = 'user'
        typeval = '2'

        extension_id = self.add_extension(exten=exten,
                                          context=context,
                                          type=type,
                                          typeval=typeval)

        extension = extension_dao.get_by_type_typeval(type, typeval)

        assert_that(extension.id, equal_to(extension_id))
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

        extension_id = self.add_extension(exten=exten,
                                          context=context,
                                          type=type,
                                          typeval=typeval)

        extension = extension_dao.get(extension_id)

        extension_dao.delete(extension)

        row = self.session.query(ExtensionSchema).filter(ExtensionSchema.id == extension_id).first()

        self.assertEquals(row, None)

    def test_delete_not_exist(self):
        extension = Extension(id=1)

        self.assertRaises(ElementDeletionError, extension_dao.delete, extension)
