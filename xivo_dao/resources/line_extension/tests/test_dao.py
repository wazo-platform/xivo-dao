# Copyright 2013-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    any_of,
    assert_that,
    contains_exactly,
    equal_to,
    has_properties,
    is_not,
    none,
)

from xivo_dao.alchemy.line_extension import LineExtension
from xivo_dao.helpers.exception import InputError
from xivo_dao.resources.line_extension import dao
from xivo_dao.tests.test_dao import DAOTestCase


class TestLineExtensionDAO(DAOTestCase):
    def prepare_secondary_user_associated(self, line_extension):
        user = self.add_user()
        return self.associate_secondary_user(line_extension, user)

    def associate_secondary_user(self, line_extension, user_row):
        line_extension = self.add_line_extension(
            line_id=line_extension.line_id, extension_id=line_extension.extension_id
        )
        return line_extension


class TestAssociateLineExtension(TestLineExtensionDAO):
    def test_associate(self):
        line = self.add_line()
        extension = self.add_extension()

        result = dao.associate(line, extension)

        assert_that(result, has_properties(line_id=line.id, extension_id=extension.id))
        self.assert_extension_is_associated(line.id, extension.id)

    def test_associate_already_associated(self):
        line = self.add_line()
        extension = self.add_extension()
        line_extension_associated = dao.associate(line, extension)

        result = dao.associate(line, extension)

        assert_that(result, equal_to(line_extension_associated))

    def test_associate_line_multiple_extensions(self):
        line = self.add_line()
        extension1 = self.add_extension()
        extension2 = self.add_extension()

        dao.associate(line, extension1)
        dao.associate(line, extension2)

        self.assert_extension_is_associated(line.id, extension1.id, main_extension=True)
        self.assert_extension_is_associated(
            line.id, extension2.id, main_extension=False
        )

    def test_associate_multiple_lines_extension(self):
        line1 = self.add_line()
        line2 = self.add_line()
        extension = self.add_extension()

        dao.associate(line1, extension)
        dao.associate(line2, extension)

        self.assert_extension_is_associated(line1.id, extension.id)
        self.assert_extension_is_associated(line1.id, extension.id)

    def assert_extension_is_associated(
        self, line_id, extension_id, main_extension=True
    ):
        line_extension = (
            self.session.query(LineExtension)
            .filter(LineExtension.line_id == line_id)
            .filter(LineExtension.extension_id == extension_id)
            .filter(LineExtension.main_extension == main_extension)
            .first()
        )
        assert_that(line_extension, is_not(none()))


class TestFindBy(TestLineExtensionDAO):
    def test_given_column_does_not_exist_then_raises_error(self):
        self.assertRaises(InputError, dao.find_by, column=1)

    def test_find_by(self):
        line = self.add_line()
        extension = self.add_extension()
        expected = self.add_line_extension(line_id=line.id, extension_id=extension.id)

        line_extension = dao.find_by(line_id=expected.line_id)

        assert_that(line_extension, equal_to(expected))


class TestFindByLineId(TestLineExtensionDAO):
    def test_find_by_line_id_no_line(self):
        result = dao.find_by_line_id(1)

        assert_that(result, none())

    def test_find_by_line_id(self):
        line = self.add_line()
        extension = self.add_extension()
        expected = self.add_line_extension(line_id=line.id, extension_id=extension.id)

        line_extension = dao.find_by_line_id(expected.line_id)

        assert_that(line_extension, equal_to(expected))


class TestFindAllByLineId(TestLineExtensionDAO):
    def test_given_no_line_extensions_then_returns_empty_list(self):
        result = dao.find_all_by_line_id(1)

        assert_that(result, contains_exactly())

    def test_given_one_line_extension_then_returns_one_item(self):
        line = self.add_line()
        extension = self.add_extension()
        line_extension = self.add_line_extension(
            line_id=line.id, extension_id=extension.id
        )

        result = dao.find_all_by_line_id(line_extension.line_id)

        assert_that(
            result,
            contains_exactly(
                has_properties(
                    line_id=line_extension.line_id,
                    extension_id=line_extension.extension_id,
                )
            ),
        )

    def test_line_multiple_extensions(self):
        line = self.add_line()
        extension1 = self.add_extension()
        extension2 = self.add_extension()
        self.add_line_extension(line_id=line.id, extension_id=extension1.id)
        self.add_line_extension(line_id=line.id, extension_id=extension2.id)

        result = dao.find_all_by_line_id(line.id)

        assert_that(
            result,
            contains_exactly(
                has_properties(line_id=line.id, extension_id=extension1.id),
                has_properties(line_id=line.id, extension_id=extension2.id),
            ),
        )


class TestFindByExtensionId(TestLineExtensionDAO):
    def test_find_by_extension_id_no_links(self):
        result = dao.find_by_extension_id(1)

        assert_that(result, none())

    def test_find_by_extension_id_not_associated_to_wrong_extension(self):
        line = self.add_line()
        extension = self.add_extension(exten=2)
        self.add_line_extension(line_id=line.id, extension_id=extension.id)

        result = dao.find_by_extension_id(1)

        assert_that(result, none())

    def test_find_by_extension_id_associated_to_extension(self):
        line = self.add_line()
        extension = self.add_extension()
        expected = self.add_line_extension(line_id=line.id, extension_id=extension.id)

        result = dao.find_by_extension_id(extension.id)

        assert_that(result, equal_to(expected))

    def test_line_multiple_extensions(self):
        line1 = self.add_line()
        line2 = self.add_line()
        extension = self.add_extension()
        self.add_line_extension(line_id=line1.id, extension_id=extension.id)
        self.add_line_extension(line_id=line2.id, extension_id=extension.id)

        result = dao.find_by_extension_id(extension.id)

        assert_that(
            result,
            any_of(
                has_properties(line_id=line1.id, extension_id=extension.id),
                has_properties(line_id=line2.id, extension_id=extension.id),
            ),
        )


class TestDissociateLineExtension(TestLineExtensionDAO):
    def test_dissociate_one_association_with_user(self):
        line = self.add_line()
        extension = self.add_extension()
        self.add_line_extension(line_id=line.id, extension_id=extension.id)

        dao.dissociate(line, extension)

        self.assert_line_extension_deleted(line.id, extension.id)

    def test_dissociate_not_associated(self):
        line = self.add_line()
        extension = self.add_extension()

        dao.dissociate(line, extension)

        self.assert_line_extension_deleted(line.id, extension.id)

    def test_dissociate_line_multiple_extensions_then_main_extension_fallback(self):
        line = self.add_line()
        extension1 = self.add_extension()
        extension2 = self.add_extension()
        self.add_line_extension(
            line_id=line.id, extension_id=extension1.id, main_extension=True
        )
        self.add_line_extension(
            line_id=line.id, extension_id=extension2.id, main_extension=False
        )

        dao.dissociate(line, extension1)

        self.assert_line_extension_deleted(line.id, extension1.id)
        self.assert_extension_is_associated(line.id, extension2.id, main_extension=True)

    def assert_line_extension_deleted(self, line_id, extension_id):
        updated_row = (
            self.session.query(LineExtension)
            .filter(LineExtension.line_id == line_id)
            .filter(LineExtension.extension_id == extension_id)
            .first()
        )

        assert_that(updated_row, none())

    def assert_extension_is_associated(
        self, line_id, extension_id, main_extension=True
    ):
        line_extension = (
            self.session.query(LineExtension)
            .filter(LineExtension.line_id == line_id)
            .filter(LineExtension.extension_id == extension_id)
            .filter(LineExtension.main_extension == main_extension)
            .first()
        )
        assert_that(line_extension, is_not(none()))
