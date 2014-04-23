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

from hamcrest import assert_that, contains, has_items

from xivo_dao.alchemy.incall import Incall
from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.extension import Extension
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.data_handler.incall import dao
from xivo_dao.data_handler.line_extension.model import LineExtension


class TestIncallDAO(DAOTestCase):

    def create_incall_for_user(self, user_id, extension_id):
        extension_row = self.session.query(Extension).get(extension_id)

        incall_row = Incall(exten=extension_row.exten,
                            context=extension_row.context,
                            description='')
        self.add_me(incall_row)

        dialaction_row = Dialaction(event='answer',
                                    category='incall',
                                    categoryval=str(incall_row.id),
                                    action='user',
                                    actionarg1=str(user_id),
                                    linked=1)
        self.add_me(dialaction_row)

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
        user_line_row = self.add_user_line_with_exten(exten='1000', context='from-extern')
        self.create_incall_for_user(user_line_row.user_id, user_line_row.extension_id)

        line_extension = LineExtension(line_id=user_line_row.line_id,
                                       extension_id=user_line_row.extension_id)

        result = dao.find_all_line_extensions_by_line_id(line_extension.line_id)

        assert_that(result, contains(line_extension))

    def test_given_line_with_multiple_users_then_returns_one_item(self):
        user_line_row = self.add_user_line_with_exten(exten='1000', context='from-extern')
        self.create_incall_for_user(user_line_row.user_id, user_line_row.extension_id)

        line_extension = LineExtension(line_id=user_line_row.line_id,
                                       extension_id=user_line_row.extension_id)
        self.add_secondary_user(line_extension)

        result = dao.find_all_line_extensions_by_line_id(line_extension.line_id)

        assert_that(result, contains(line_extension))

    def test_given_2_incalls_on_same_user_then_returns_two_items(self):
        user_line_row = self.add_user_line_with_exten(exten='1000', context='from-extern')
        second_extension_row = self.add_extension(exten='1001', context='from-extern')

        self.create_incall_for_user(user_line_row.user_id, user_line_row.extension_id)
        self.create_incall_for_user(user_line_row.user_id, second_extension_row.id)

        first_line_extension = LineExtension(line_id=user_line_row.line_id,
                                             extension_id=user_line_row.extension_id)
        second_line_extension = LineExtension(line_id=user_line_row.line_id,
                                              extension_id=second_extension_row.id)

        result = dao.find_all_line_extensions_by_line_id(user_line_row.line_id)

        assert_that(result, has_items(first_line_extension, second_line_extension))

    def test_given_2_lines_then_returns_one_item_with_right_line_id(self):
        first_user_line_row = self.add_user_line_with_exten(exten='1000', context='from-extern')
        second_user_line_row = self.add_user_line_with_exten(exten='1001', context='from-extern')
        self.create_incall_for_user(first_user_line_row.user_id, first_user_line_row.extension_id)
        self.create_incall_for_user(second_user_line_row.user_id, second_user_line_row.extension_id)

        line_extension = LineExtension(line_id=first_user_line_row.line_id,
                                       extension_id=first_user_line_row.extension_id)

        result = dao.find_all_line_extensions_by_line_id(first_user_line_row.line_id)

        assert_that(result, contains(line_extension))
