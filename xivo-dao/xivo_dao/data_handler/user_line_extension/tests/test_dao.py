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

from hamcrest import assert_that, contains, equal_to
from mock import patch, Mock

from .. import dao as ule_dao
from ..model import UserLineExtension
from xivo_dao.tests.test_dao import DAOTestCase
from sqlalchemy.exc import SQLAlchemyError
from xivo_dao.data_handler.exception import ElementCreationError, \
    ElementDeletionError, ElementEditionError
from xivo_dao.alchemy.userfeatures import UserFeatures as UserSchema
from xivo_dao.alchemy.extension import Extension as ExtensionSchema
from xivo_dao.alchemy.linefeatures import LineFeatures as LineSchema
from xivo_dao.alchemy.user_line import UserLine as ULESchema
from xivo_dao.alchemy.ctiphonehintsgroup import CtiPhoneHintsGroup
from xivo_dao.alchemy.ctipresences import CtiPresences
from xivo_dao.alchemy.cti_profile import CtiProfile


class TestUserLineExtensionDao(DAOTestCase):

    tables = [
        UserSchema,
        ExtensionSchema,
        LineSchema,
        ULESchema,
        CtiPhoneHintsGroup,
        CtiPresences,
        CtiProfile,
    ]

    def setUp(self):
        self.empty_tables()

    def test_get_no_exist(self):
        self.assertRaises(LookupError, ule_dao.get, 666)

    def test_get(self):
        expected_ule = self.add_user_line_with_exten()

        ule = ule_dao.get(expected_ule.id)

        assert_that(ule.id, equal_to(expected_ule.id))
        assert_that(ule.user_id, equal_to(expected_ule.user_id))
        assert_that(ule.line_id, equal_to(expected_ule.line_id))
        assert_that(ule.extension_id, equal_to(expected_ule.extension_id))
        assert_that(ule.main_user, equal_to(expected_ule.main_user))
        assert_that(ule.main_line, equal_to(expected_ule.main_line))

    def test_find_all_by_user_id_not_found(self):
        expected_result = []
        user_id = 5676

        result = ule_dao.find_all_by_user_id(user_id)

        assert_that(result, equal_to(expected_result))

    def test_find_all_by_user_id_found(self):
        ule_row = self.add_user_line_with_exten()
        user_id = ule_row.user_id
        expected_ule = UserLineExtension.from_data_source(ule_row)

        result = ule_dao.find_all_by_user_id(user_id)

        assert_that(result, contains(expected_ule))

    def test_find_all_by_extension_id_not_found(self):
        expected_result = []
        extension_id = 5676

        result = ule_dao.find_all_by_extension_id(extension_id)

        assert_that(result, equal_to(expected_result))

    def test_find_all_by_extension_id_found(self):
        ule_row = self.add_user_line_with_exten()
        extension_id = ule_row.extension_id
        expected_ule = UserLineExtension.from_data_source(ule_row)

        result = ule_dao.find_all_by_extension_id(extension_id)

        assert_that(result, contains(expected_ule))

    def test_create(self):
        expected_user = self.add_user()
        expected_line = self.add_line()
        expected_extension = self.add_extension()

        ule = UserLineExtension(user_id=expected_user.id,
                                line_id=expected_line.id,
                                extension_id=expected_extension.id,
                                main_user=True,
                                main_line=False)

        created_extension = ule_dao.create(ule)

        row = self.session.query(ULESchema).filter(ULESchema.id == created_extension.id).first()

        assert_that(row.id, equal_to(created_extension.id))
        assert_that(row.user_id, equal_to(expected_user.id))
        assert_that(row.line_id, equal_to(expected_line.id))
        assert_that(row.extension_id, equal_to(expected_extension.id))

    def test_create_same_user_id__line_id(self):
        expected_user = self.add_user()
        expected_line = self.add_line()
        expected_extension_1 = self.add_extension()
        expected_extension_2 = self.add_extension(exten='1254')

        ule = UserLineExtension(user_id=expected_user.id,
                                line_id=expected_line.id,
                                extension_id=expected_extension_1.id,
                                main_user=True,
                                main_line=False)

        ule_dao.create(ule)

        ule = UserLineExtension(user_id=expected_user.id,
                                line_id=expected_line.id,
                                extension_id=expected_extension_2.id,
                                main_user=True,
                                main_line=False)

        self.assertRaises(ElementCreationError, ule_dao.create, ule)

    @patch('xivo_dao.helpers.db_manager.AsteriskSession')
    def test_create_extension_with_error_from_dao(self, Session):
        session = Mock()
        session.commit.side_effect = SQLAlchemyError()
        Session.return_value = session

        expected_user = self.add_user()
        expected_line = self.add_line()
        expected_extension = self.add_extension()

        ule = UserLineExtension(user_id=expected_user.id,
                                line_id=expected_line.id,
                                extension_id=expected_extension.id,
                                main_user=True,
                                main_line=False)

        self.assertRaises(ElementCreationError, ule_dao.create, ule)
        session.begin.assert_called_once_with()
        session.rollback.assert_called_once_with()

    def test_edit(self):
        expected_ule = self.add_user_line_with_exten()
        expected_user = self.add_user()

        ule = UserLineExtension(id=expected_ule.id, user_id=expected_user.id)

        ule_dao.edit(ule)

        row = (self.session.query(ULESchema)
               .filter(ULESchema.user_id == expected_user.id)
               .first())

        self.assertEquals(row.user_id, expected_user.id)

    def test_edit_with_unknown_id(self):
        ule = UserLineExtension(id=123, user_id=55)

        self.assertRaises(ElementEditionError, ule_dao.edit, ule)

    @patch('xivo_dao.helpers.db_manager.AsteriskSession')
    def test_edit_with_database_error(self, Session):
        session = Mock()
        session.commit.side_effect = SQLAlchemyError()
        Session.return_value = session

        expected_ule = self.add_user_line_with_exten()

        ule = UserLineExtension(id=expected_ule.id, user_id=55)

        self.assertRaises(ElementEditionError, ule_dao.edit, ule)
        session.begin.assert_called_once_with()
        session.rollback.assert_called_once_with()

    def test_delete(self):
        expected_ule = self.add_user_line_with_exten()

        extension = ule_dao.get(expected_ule.id)

        ule_dao.delete(extension)

        row = self.session.query(ULESchema).filter(ULESchema.id == expected_ule.id).first()

        self.assertEquals(row, None)

    def test_delete_not_exist(self):
        extension = UserLineExtension(id=1)

        self.assertRaises(ElementDeletionError, ule_dao.delete, extension)
