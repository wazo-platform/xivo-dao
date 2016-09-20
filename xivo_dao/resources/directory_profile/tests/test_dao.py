# -*- coding: utf-8 -*-

# Copyright (C) 2015-2016 Avencall
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
from hamcrest import equal_to
from hamcrest import is_
from hamcrest import none

from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.resources.directory_profile import dao as profile_dao

from xivo_dao.tests.test_dao import DAOTestCase


class TestDirectoryProfileDao(DAOTestCase):

    def test_find_by_incall_id(self):
        user_line = self.add_user_line_with_exten(context='default')
        incall = self.add_incall(destination=Dialaction(action='user', actionarg1=user_line.user_id))
        result = profile_dao.find_by_incall_id(incall_id=incall.id)

        assert_that(result.profile, equal_to(user_line.line.context))
        assert_that(result.xivo_user_uuid, equal_to(user_line.user.uuid))

    def test_find_by_incall_id_return_none_when_not_found(self):

        result = profile_dao.find_by_incall_id(incall_id=99999999)

        assert_that(result, is_(none()))
