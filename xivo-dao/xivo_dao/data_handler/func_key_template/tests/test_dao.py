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

from hamcrest import assert_that, is_not, none, has_property
from mock import patch, ANY

from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.alchemy.func_key_template import FuncKeyTemplate as FuncKeyTemplateSchema

from xivo_dao.data_handler.exception import ElementCreationError
from xivo_dao.data_handler.func_key_template import dao


class TestCreatePrivateTemplate(DAOTestCase):

    tables = [
        FuncKeyTemplateSchema,
    ]

    def setUp(self):
        self.empty_tables()

    def test_create_private_template(self):
        template_id = dao.create_private_template()

        self.assert_private_template_created(template_id)

    def assert_private_template_created(self, template_id):
        template_row = self.session.query(FuncKeyTemplateSchema).get(template_id)
        assert_that(template_row, is_not(none()))

        assert_that(template_row, has_property('private', True))
        assert_that(template_row, has_property('name', none()))

    @patch('xivo_dao.data_handler.func_key_template.dao.commit_or_abort')
    def test_given_database_error_then_transaction_aborted(self, commit_or_abort):
        dao.create_private_template()

        commit_or_abort.assert_called_with(ANY, ElementCreationError, 'FuncKeyTemplate')
