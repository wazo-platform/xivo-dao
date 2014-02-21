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

from hamcrest import assert_that, is_not, none
from mock import patch, Mock, ANY

from sqlalchemy.exc import SQLAlchemyError

from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.alchemy.userfeatures import test_dependencies as user_test_dependencies
from xivo_dao.alchemy.func_key import test_dependencies as func_key_test_dependencies
from xivo_dao.alchemy.func_key import FuncKey as FuncKeySchema
from xivo_dao.alchemy.func_key_template import FuncKeyTemplate as FuncKeyTemplateSchema
from xivo_dao.alchemy.userfeatures import UserFeatures as UserSchema

from xivo_dao.data_handler.exception import ElementCreationError
from xivo_dao.data_handler.func_key_template import dao
from xivo_dao.data_handler.user.model import User


class TestCreatePrivateTemplateForUser(DAOTestCase):

    tables = [
        FuncKeyTemplateSchema,
        FuncKeySchema,
        UserSchema,
    ]

    tables += user_test_dependencies
    tables += func_key_test_dependencies

    def setUp(self):
        self.empty_tables()

    def test_given_one_user_then_private_template_is_created(self):
        user = self.prepare_user()

        dao.create_private_template_for_user(user)

        self.assert_user_has_private_template(user)

    @patch('xivo_dao.data_handler.func_key_template.dao.commit_or_abort')
    def test_given_database_error_then_transaction_aborted(self, commit_or_abort):
        user = User(firstname='firstname')

        dao.create_private_template_for_user(user)

        commit_or_abort.assert_called_with(ANY, ElementCreationError, 'FuncKeyTemplate')

    def prepare_user(self):
        user_row = self.add_user()
        user = User(id=user_row.id, firstname=user_row.firstname)
        return user

    def assert_user_has_private_template(self, user):
        row = (self.session.query(UserSchema.func_key_private_template_id)
               .filter(UserSchema.id == user.id)
               .first())

        template_id = row.func_key_private_template_id
        assert_that(template_id, is_not(none()), "user has no private template")

        template_row = (self.session.query(FuncKeyTemplateSchema)
                        .get(template_id))

        assert_that(template_row.private, True)
