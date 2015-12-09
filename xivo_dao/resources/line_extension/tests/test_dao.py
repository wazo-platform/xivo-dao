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

from hamcrest import assert_that, all_of, has_property, none, is_not, contains, equal_to, has_properties, has_items

from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.resources.line_extension import dao

from xivo_dao.helpers.exception import NotFoundError

from xivo_dao.alchemy.user_line import UserLine


class TestLineExtensionDAO(DAOTestCase):

    def prepare_secondary_user_associated(self, user_line_row):
        user_row = self.add_user()
        return self.associate_secondary_user(user_line_row, user_row)

    def associate_secondary_user(self, user_line_row, user_row):
        user_line_row = self.add_user_line(user_id=user_row.id,
                                           line_id=user_line_row.line_id,
                                           extension_id=user_line_row.extension_id,
                                           main_user=False,
                                           main_line=True)
        return user_line_row


class TestAssociateLineExtension(TestLineExtensionDAO):

    def test_associate_no_user(self):
        line_row = self.add_line()
        extension_row = self.add_extension()

        result = dao.associate(line_row, extension_row)

        self.assert_line_extension_has_ids(result, line_row.id, extension_row.id)
        self.assert_extension_is_associated(line_row.id, extension_row.id)

    def test_associate_main_user(self):
        ule_row = self.add_user_line_without_exten()
        extension_row = self.add_extension()

        result = dao.associate(ule_row.linefeatures, extension_row)

        self.assert_line_extension_has_ids(result, ule_row.line_id, ule_row.extension_id)
        self.assert_extension_is_associated(ule_row.line_id, extension_row.id)

    def test_associate_main_and_secondary_user(self):
        main_ule = self.add_user_line_without_exten()
        secondary_user = self.add_user()
        secondary_ule = self.associate_secondary_user(main_ule, secondary_user)
        extension_row = self.add_extension()

        result = dao.associate(main_ule.linefeatures, extension_row)

        self.assert_line_extension_has_ids(result, main_ule.line_id, extension_row.id)
        self.assert_extension_is_associated(main_ule.line_id, extension_row.id)
        self.assert_extension_is_associated(secondary_ule.line_id, extension_row.id)

    def assert_line_extension_has_ids(self, line_extensions, line_id, extension_id):
        assert_that(line_extensions, has_items(has_properties(line_id=line_id,
                                                              extension_id=extension_id)))

    def assert_extension_is_associated(self, line_id, extension_id):
        updated_ule = (self.session.query(UserLine)
                       .filter(UserLine.line_id == line_id)
                       .filter(UserLine.extension_id == extension_id)
                       .first())
        assert_that(updated_ule, is_not(none()))


class TestFindByLineId(TestLineExtensionDAO):

    def test_find_by_line_id_no_line(self):
        result = dao.find_by_line_id(1)

        assert_that(result, none())

    def test_find_by_line_id_no_extension(self):
        user_line_row = self.add_user_line_without_exten()

        result = dao.find_by_line_id(user_line_row.line_id)

        assert_that(result, none())

    def test_find_by_line_id_with_extension(self):
        expected = self.add_user_line_with_exten()

        line_extension = dao.find_by_line_id(expected.line_id)

        assert_that(line_extension, equal_to(expected))

    def test_find_by_line_id_with_extension_without_user(self):
        expected = self.add_user_line_without_user()

        line_extension = dao.find_by_line_id(expected.line_id)

        assert_that(line_extension, equal_to(expected))

    def test_find_by_line_id_with_multiple_users(self):
        main_ule = self.add_user_line_with_exten()
        secondary_ule = self.prepare_secondary_user_associated(main_ule)

        line_extension = dao.find_by_line_id(secondary_ule.line_id)

        assert_that(line_extension.line_id, equal_to(main_ule.line_id))
        assert_that(line_extension.extension_id, equal_to(main_ule.extension_id))


class TestFindAllByLineId(TestLineExtensionDAO):

    def test_given_no_line_extensions_then_returns_empty_list(self):
        result = dao.find_all_by_line_id(1)

        assert_that(result, contains())

    def test_given_one_line_extension_then_returns_one_item(self):
        user_line_row = self.add_user_line_with_exten()

        result = dao.find_all_by_line_id(user_line_row.line_id)

        assert_that(result, contains(has_properties(line_id=user_line_row.line_id,
                                                    extension_id=user_line_row.extension_id)))

    def test_given_user_line_without_extension_then_returns_empty_list(self):
        user_line_row = self.add_user_line_without_exten()

        result = dao.find_all_by_line_id(user_line_row.line_id)

        assert_that(result, contains())

    def test_given_multiple_users_associated_to_same_line_then_returns_one_item(self):
        main_ule = self.add_user_line_with_exten()
        self.prepare_secondary_user_associated(main_ule)

        result = dao.find_all_by_line_id(main_ule.line_id)

        assert_that(result, contains(has_properties(line_id=main_ule.line_id,
                                                    extension_id=main_ule.extension_id)))


class TestGetByLineId(TestLineExtensionDAO):

    def test_get_by_line_id_no_line(self):
        self.assertRaises(NotFoundError, dao.get_by_line_id, 1)

    def test_get_by_line_id_no_extension(self):
        user_line_row = self.add_user_line_without_exten()

        self.assertRaises(NotFoundError, dao.get_by_line_id, user_line_row.line_id)

    def test_get_by_line_id_with_extension(self):
        user_line_row = self.add_user_line_with_exten()

        line_extension = dao.get_by_line_id(user_line_row.line_id)

        assert_that(line_extension, equal_to(user_line_row))

    def test_get_by_line_id_with_multiple_users(self):
        main_ule = self.add_user_line_with_exten()
        secondary_ule = self.prepare_secondary_user_associated(main_ule)

        line_extension = dao.get_by_line_id(secondary_ule.line_id)

        assert_that(line_extension.line_id, equal_to(main_ule.line_id))
        assert_that(line_extension.extension_id, equal_to(main_ule.extension_id))


class TestFindAllByExtensionId(TestLineExtensionDAO):

    def test_find_by_extension_id_no_links(self):
        result = dao.find_by_extension_id(1)

        assert_that(result, none())

    def test_find_by_extension_id_not_associated_to_extension(self):
        self.add_user_line_without_exten()

        result = dao.find_by_extension_id(1)

        assert_that(result, none())

    def test_find_by_extension_id_not_associated_to_wrong_extension(self):
        self.add_user_line_with_exten(exten=2)

        result = dao.find_by_extension_id(1)

        assert_that(result, none())

    def test_find_by_extension_id_associated_to_extension(self):
        user_line_row = self.add_user_line_with_exten(exten=2)

        result = dao.find_by_extension_id(user_line_row.extension_id)

        assert_that(result, equal_to(user_line_row))

    def test_find_by_extension_id_associated_to_multiple_users(self):
        main_ule = self.add_user_line_with_exten(exten=2)
        secondary_ule = self.prepare_secondary_user_associated(main_ule)

        result = dao.find_by_extension_id(secondary_ule.extension_id)

        assert_that(result.line_id, equal_to(main_ule.line_id))
        assert_that(result.extension_id, equal_to(main_ule.extension_id))


class TestGetByExtensionId(TestLineExtensionDAO):

    def test_get_by_extension_id_no_line(self):
        extension_row = self.add_extension()

        self.assertRaises(NotFoundError, dao.get_by_extension_id, extension_row.id)

    def test_get_by_extension_id_with_line(self):
        user_line_row = self.add_user_line_with_exten()

        line_extension = dao.get_by_extension_id(user_line_row.extension_id)

        assert_that(line_extension, all_of(
            has_property('line_id', user_line_row.line_id),
            has_property('extension_id', user_line_row.extension_id)))

    def test_get_by_extension_id_with_multiple_users(self):
        main_ule = self.add_user_line_with_exten()
        secondary_ule = self.prepare_secondary_user_associated(main_ule)

        line_extension = dao.get_by_extension_id(secondary_ule.extension_id)

        assert_that(line_extension, all_of(
            has_property('line_id', main_ule.line_id),
            has_property('extension_id', main_ule.extension_id)))


class TestDissociateLineExtension(TestLineExtensionDAO):

    def test_dissociate_one_association_with_user(self):
        user_line_row = self.add_user_line_with_exten()

        dao.dissociate(user_line_row.linefeatures, user_line_row.extensions)

        self.assert_no_extensions_associated(user_line_row)

    def test_dissociate_one_association_without_user(self):
        user_line_row = self.add_user_line_without_user()

        dao.dissociate(user_line_row.linefeatures, user_line_row.extensions)

        self.assert_user_line_deleted(user_line_row)

    def test_dissociate_multiple_users(self):
        main_ule = self.add_user_line_with_exten()
        secondary_ule = self.prepare_secondary_user_associated(main_ule)

        dao.dissociate(secondary_ule.linefeatures, secondary_ule.extensions)

        self.assert_no_extensions_associated(main_ule)
        self.assert_no_extensions_associated(secondary_ule)

    def assert_no_extensions_associated(self, user_line_row):
        updated_row = (self.session.query(UserLine)
                       .filter(UserLine.user_id == user_line_row.user_id)
                       .filter(UserLine.line_id == user_line_row.line_id)
                       .first())

        assert_that(updated_row, has_property('extension_id', none()))

    def assert_user_line_deleted(self, user_line_row):
        updated_row = (self.session.query(UserLine)
                       .filter(UserLine.user_id == user_line_row.user_id)
                       .filter(UserLine.line_id == user_line_row.line_id)
                       .first())

        assert_that(updated_row, none())
