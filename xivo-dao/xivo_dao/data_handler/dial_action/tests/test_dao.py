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

from hamcrest import assert_that, equal_to

from mock import patch, ANY

from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.alchemy.dialaction import Dialaction as DialactionSchema
from xivo_dao.data_handler.user.model import User
from xivo_dao.data_handler.dial_action import dao as dial_action_dao
from xivo_dao.data_handler.exception import ElementCreationError


class TestDialActionDAO(DAOTestCase):

    tables = [DialactionSchema]

    def setUp(self):
        self.empty_tables()

    def test_create_default_dial_actions_for_user(self):
        user = User(id=1)

        dial_action_dao.create_default_dial_actions_for_user(user)

        self.assert_user_has_dialaction(user, 'noanswer')
        self.assert_user_has_dialaction(user, 'busy')
        self.assert_user_has_dialaction(user, 'congestion')
        self.assert_user_has_dialaction(user, 'chanunavail')

    @patch('xivo_dao.data_handler.dial_action.dao.commit_or_abort')
    def test_create_default_dial_actions_catches_database_error(self, commit_or_abort):
        user = User(id=1)

        dial_action_dao.create_default_dial_actions_for_user(user)

        commit_or_abort.assert_called_once_with(ANY, ElementCreationError, 'Dialaction')

    def assert_user_has_dialaction(self, user, event):
        count = (self.session.query(DialactionSchema)
                 .filter(DialactionSchema.event == event)
                 .filter(DialactionSchema.category == 'user')
                 .filter(DialactionSchema.categoryval == str(user.id))
                 .filter(DialactionSchema.action == 'none')
                 .filter(DialactionSchema.actionarg1 == None)
                 .filter(DialactionSchema.actionarg2 == None)
                 .filter(DialactionSchema.linked == 1)
                 .count())

        assert_that(count, equal_to(1), "dial action '%s' for user id %d was not created" % (event, user.id))
