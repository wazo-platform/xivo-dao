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

from hamcrest import assert_that, all_of, equal_to, has_items, has_length, has_property, none, contains
from mock import patch, Mock
from sqlalchemy.exc import SQLAlchemyError

from xivo_dao.alchemy.extension import Extension as ExtensionSchema
from xivo_dao.data_handler.exception import ElementCreationError
from xivo_dao.data_handler.exception import ElementEditionError
from xivo_dao.data_handler.extension import dao as extension_dao
from xivo_dao.data_handler.extension.model import Extension
from xivo_dao.data_handler.user.model import User
from xivo_dao.tests.test_dao import DAOTestCase


class TestFindAll(DAOTestCase):

    def prepare_extension(self, **kwargs):
        extension_row = self.add_extension(**kwargs)
        return Extension(id=extension_row.id,
                         exten=extension_row.exten,
                         context=extension_row.context,
                         commented=bool(extension_row.commented))

    def test_find_all_no_extens(self):
        expected = []
        extens = extension_dao.find_all()

        assert_that(extens, equal_to(expected))

    def test_find_all_one_exten(self):
        expected_exten = '12345'
        extension = self.prepare_extension(exten=expected_exten)

        extens = extension_dao.find_all()

        assert_that(extens, has_length(1))
        assert_that(extens, contains(extension))

    def test_find_all_two_extens(self):
        expected_exten1 = '1234'
        expected_exten2 = '5678'

        exten1 = self.prepare_extension(exten=expected_exten1)
        exten2 = self.prepare_extension(exten=expected_exten2)

        extens = extension_dao.find_all()

        assert_that(extens, has_length(2))
        assert_that(extens, has_items(exten1, exten2))

    def test_find_all_with_commented(self):
        extension = self.prepare_extension(exten='1234', commented=1)

        extens = extension_dao.find_all()

        assert_that(extens, has_length(1))
        assert_that(extens, contains(extension))


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


class TestAssociateToUser(DAOTestCase):

    def test_associate_to_user(self):
        extension = self.prepare_extension()
        user = self.prepare_user()

        extension_dao.associate_to_user(user, extension)

        self.assert_extension_is_associated_to_user(user, extension)

    @patch('xivo_dao.helpers.db_manager.DaoSession')
    def test_associate_to_user_with_database_error(self, Session):
        session = Mock()
        session.commit.side_effect = SQLAlchemyError()
        Session.return_value = session

        extension = Mock(Extension, id=1)
        user = Mock(User, id=2)

        self.assertRaises(ElementEditionError, extension_dao.associate_to_user, user, extension)
        session.commit.assert_called_once_with()
        session.rollback.assert_called_once_with()

    def prepare_extension(self):
        extension_row = self.add_extension()
        extension = Mock(Extension, id=extension_row.id)
        return extension

    def prepare_user(self):
        user_row = self.add_user()
        user = Mock(User, id=user_row.id)
        return user

    def assert_extension_is_associated_to_user(self, user, extension):
        updated_extension = self.session.query(ExtensionSchema).get(extension.id)
        assert_that(updated_extension.type, equal_to('user'))
        assert_that(updated_extension.typeval, equal_to(str(user.id)))


class TestDissociateExtension(DAOTestCase):

    def test_dissociate_extension(self):
        extension = self.prepare_extension()

        extension_dao.dissociate_extension(extension)

        self.assert_extension_not_associated(extension)

    @patch('xivo_dao.helpers.db_manager.DaoSession')
    def test_dissociate_extension_with_database_error(self, Session):
        session = Mock()
        session.commit.side_effect = SQLAlchemyError()
        Session.return_value = session

        extension = Mock(Extension, id=1)

        self.assertRaises(ElementEditionError, extension_dao.dissociate_extension, extension)

    def prepare_extension(self):
        extension_row = self.add_extension(type='user', typeval='1234')
        return Mock(Extension, id=extension_row.id)

    def assert_extension_not_associated(self, extension):
        updated_extension = self.session.query(ExtensionSchema).get(extension.id)
        assert_that(updated_extension.type, equal_to('user'))
        assert_that(updated_extension.typeval, equal_to('0'))
