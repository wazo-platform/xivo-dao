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

from hamcrest import assert_that, contains, has_items, equal_to, none

from xivo_dao.alchemy.incall import Incall as IncallSchema
from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.extension import Extension
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.data_handler.incall import dao
from xivo_dao.data_handler.incall.model import Incall
from xivo_dao.data_handler.line_extension.model import LineExtension


class TestIncallDAO(DAOTestCase):

    def create_user_incall(self):
        user_row = self.add_user()
        extension_row = self.add_extension(exten='1000', context='from-extern')
        incall_row = self.create_incall_row_for_user(user_row.id, extension_row.id)
        return Incall(id=incall_row.id,
                      destination='user',
                      destination_id=user_row.id,
                      extension_id=extension_row.id)

    def create_incall_row_for_user(self, user_id, extension_id):
        extension_row = self.session.query(Extension).get(extension_id)

        incall_row = self.add_incall(exten=extension_row.exten,
                                     context=extension_row.context)

        dialaction_row = Dialaction(event='answer',
                                    category='incall',
                                    categoryval=str(incall_row.id),
                                    action='user',
                                    actionarg1=str(user_id),
                                    linked=1)
        self.add_me(dialaction_row)

        extension_row.type = 'incall'
        extension_row.typeval = str(incall_row.id)
        self.add_me(extension_row)

        return incall_row

    def add_secondary_user(self, line_extension):
        user_row = self.add_user()
        return self.add_user_line(user_id=user_row.id,
                                  line_id=line_extension.line_id,
                                  extension_id=line_extension.extension_id,
                                  main_user=False,
                                  main_line=True)


class TestFindAllLineExtensionsByLineId(TestIncallDAO):

    def test_given_no_incalls_then_returns_empty_list(self):
        result = dao.find_all_line_extensions_by_line_id(1)

        assert_that(result, contains())

    def test_given_user_with_no_incall_then_returns_empty_list(self):
        user_line_row = self.add_user_line_with_exten()

        result = dao.find_all_line_extensions_by_line_id(user_line_row.line_id)

        assert_that(result, contains())

    def test_given_incall_associated_to_user_with_line_then_returns_one_item(self):
        user_line_row = self.add_user_line_with_exten(exten='1000', context='default')
        extension_row = self.add_extension(exten='1000', context='from-extern')

        self.create_incall_row_for_user(user_line_row.user_id, extension_row.id)

        line_extension = LineExtension(line_id=user_line_row.line_id,
                                       extension_id=extension_row.id)

        result = dao.find_all_line_extensions_by_line_id(line_extension.line_id)

        assert_that(result, contains(line_extension))

    def test_given_line_with_multiple_users_then_returns_one_item(self):
        user_line_row = self.add_user_line_with_exten(exten='1000', context='default')
        extension_row = self.add_extension(exten='1000', context='from-extern')

        self.create_incall_row_for_user(user_line_row.user_id, extension_row.id)

        line_extension = LineExtension(line_id=user_line_row.line_id,
                                       extension_id=extension_row.id)
        self.add_secondary_user(line_extension)

        result = dao.find_all_line_extensions_by_line_id(line_extension.line_id)

        assert_that(result, contains(line_extension))

    def test_given_2_incalls_on_same_user_then_returns_two_items(self):
        user_line_row = self.add_user_line_with_exten(exten='1000', context='default')
        extension_row = self.add_extension(exten='1000', context='from-extern')
        second_extension_row = self.add_extension(exten='1001', context='from-extern')

        self.create_incall_row_for_user(user_line_row.user_id, extension_row.id)
        self.create_incall_row_for_user(user_line_row.user_id, second_extension_row.id)

        first_line_extension = LineExtension(line_id=user_line_row.line_id,
                                             extension_id=extension_row.id)
        second_line_extension = LineExtension(line_id=user_line_row.line_id,
                                              extension_id=second_extension_row.id)

        result = dao.find_all_line_extensions_by_line_id(user_line_row.line_id)

        assert_that(result, has_items(first_line_extension, second_line_extension))

    def test_given_2_lines_then_returns_one_item_with_right_line_id(self):
        first_user_line_row = self.add_user_line_with_exten(exten='1000', context='default')
        second_user_line_row = self.add_user_line_with_exten(exten='1001', context='default')
        first_extension_row = self.add_extension(exten='1000', context='from-extern')
        second_extension_row = self.add_extension(exten='1001', context='from-extern')

        self.create_incall_row_for_user(first_user_line_row.user_id, first_extension_row.id)
        self.create_incall_row_for_user(second_user_line_row.user_id, second_extension_row.id)

        line_extension = LineExtension(line_id=first_user_line_row.line_id,
                                       extension_id=first_extension_row.id)

        result = dao.find_all_line_extensions_by_line_id(first_user_line_row.line_id)

        assert_that(result, contains(line_extension))


class TestFindLineExtensionByExtensionId(TestIncallDAO):

    def test_given_no_incalls_then_returns_nothing(self):
        result = dao.find_line_extension_by_extension_id(1)

        assert_that(result, none())

    def test_given_user_with_internal_extension_then_returns_nothing(self):
        user_line_row = self.add_user_line_with_exten(exten='1000', context='default')

        result = dao.find_line_extension_by_extension_id(user_line_row.extension_id)

        assert_that(result, none())

    def test_given_incall_associated_to_user_with_line_then_returns_item(self):
        user_line_row = self.add_user_line_with_exten(exten='1000', context='default')
        extension_row = self.add_extension(exten='1000', context='from-extern')

        self.create_incall_row_for_user(user_line_row.user_id, extension_row.id)

        line_extension = LineExtension(line_id=user_line_row.line_id,
                                       extension_id=extension_row.id)

        result = dao.find_line_extension_by_extension_id(line_extension.extension_id)

        assert_that(result, equal_to(line_extension))

    def test_given_2_incalls_on_same_user_then_returns_correct_item(self):
        user_line_row = self.add_user_line_with_exten(exten='1000', context='default')
        extension_row = self.add_extension(exten='1000', context='from-extern')
        second_extension_row = self.add_extension(exten='1001', context='from-extern')

        self.create_incall_row_for_user(user_line_row.user_id, extension_row.id)
        self.create_incall_row_for_user(user_line_row.user_id, second_extension_row.id)

        line_extension = LineExtension(line_id=user_line_row.line_id,
                                       extension_id=extension_row.id)

        result = dao.find_line_extension_by_extension_id(line_extension.extension_id)

        assert_that(result, equal_to(line_extension))


class TestFindByExtensionId(TestIncallDAO):

    def test_given_no_extension_then_returns_none(self):
        result = dao.find_by_extension_id(1)

        assert_that(result, none())

    def test_given_extension_associated_to_nothing_then_returns_none(self):
        extension_row = self.add_extension(exten='1000', context='default')

        result = dao.find_by_extension_id(extension_row.id)

        assert_that(result, none())

    def test_given_extension_to_line_then_returns_none(self):
        user_line_row = self.add_user_line_with_exten()

        result = dao.find_by_extension_id(user_line_row.extension_id)

        assert_that(result, none())

    def test_given_extension_associated_to_user_incall_then_returns_incall(self):
        expected_incall = self.create_user_incall()

        result = dao.find_by_extension_id(expected_incall.extension_id)

        assert_that(result, equal_to(expected_incall))


class TestCreateUserIncall(TestIncallDAO):

    def setUp(self):
        TestIncallDAO.setUp(self)

        user_row = self.add_user()
        extension_row = self.add_extension(exten='1000', context='from-extern')

        self.user_id = user_row.id
        self.exten = extension_row.exten
        self.context = extension_row.context

        self.incall = Incall(destination='user',
                             destination_id=user_row.id,
                             extension_id=extension_row.id)

    def test_given_user_incall_then_creates_incall_row(self):
        created_incall = dao.create(self.incall)

        self.assert_incall_row_created(created_incall.id)

    def test_given_user_incall_then_creates_dialaction_row(self):
        created_incall = dao.create(self.incall)

        self.assert_dialaction_row_created(created_incall.id)

    def assert_incall_row_created(self, incall_id):
        count = (self.session.query(IncallSchema)
                 .filter(IncallSchema.id == incall_id)
                 .filter(IncallSchema.exten == self.exten)
                 .filter(IncallSchema.context == self.context)
                 .count())

        assert_that(count, equal_to(1), "incall %s@%s was not created" % (self.exten,
                                                                          self.context))

    def assert_dialaction_row_created(self, incall_id):
        count = (self.session.query(Dialaction)
                 .filter(Dialaction.event == 'answer')
                 .filter(Dialaction.category == 'incall')
                 .filter(Dialaction.categoryval == str(incall_id))
                 .filter(Dialaction.action == 'user')
                 .filter(Dialaction.actionarg1 == str(self.user_id))
                 .filter(Dialaction.linked == 1)
                 .count())

        assert_that(count, equal_to(1), "dialaction was not created")


class TestDeleteUserIncall(TestIncallDAO):

    def test_given_user_incall_model_then_deletes_incall_row(self):
        incall = self.create_user_incall()

        dao.delete(incall)

        self.assert_incall_row_deleted(incall.id)

    def test_given_user_incall_model_then_deletes_dialaction_row(self):
        incall = self.create_user_incall()

        dao.delete(incall)

        self.assert_dialaction_row_deleted(incall.id)

    def assert_incall_row_deleted(self, incall_id):
        count = (self.session.query(IncallSchema)
                 .filter(IncallSchema.id == incall_id)
                 .count())

        assert_that(count, equal_to(0), "incall row was not deleted")

    def assert_dialaction_row_deleted(self, incall_id):
        count = (self.session.query(Dialaction)
                 .filter(Dialaction.category == 'incall')
                 .filter(Dialaction.categoryval == str(incall_id))
                 .count())

        assert_that(count, equal_to(0), "dialaction row was not deleted")
