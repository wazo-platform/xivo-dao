# -*- coding: utf-8 -*-
#
# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
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
from hamcrest import none

from xivo_dao.alchemy.cti_profile import CtiProfile
from xivo_dao.helpers.exception import NotFoundError
from xivo_dao.resources.user_cti_profile import dao as user_cti_profile_dao
from xivo_dao.resources.user_cti_profile.model import UserCtiProfile
from xivo_dao.tests.test_dao import DAOTestCase


class TestUserCtiProfile(DAOTestCase):

    def test_find_by_userid(self):
        cti_profile = CtiProfile(id=2, name='Test')
        self.add_me(cti_profile)
        user = self.add_user(cti_profile_id=2)

        result = user_cti_profile_dao.find_profile_by_userid(user.id)

        assert_that(result.name, equal_to('Test'))
        assert_that(result.id, equal_to(2))

    def test_find_by_user_id_not_found(self):
        user = self.add_user()

        result = user_cti_profile_dao.find_profile_by_userid(user.id)

        assert_that(result, none())

    def test_find_by_user_id_no_user(self):
        self.assertRaises(NotFoundError, user_cti_profile_dao.find_profile_by_userid, 123)

    def test_edit(self):
        cti_profile = CtiProfile(id=2, name='Test')
        self.add_me(cti_profile)
        user = self.add_user(cti_profile_id=None, enableclient=0)
        user_cti_profile = UserCtiProfile(user_id=user.id, cti_profile_id=cti_profile.id, enabled=True)

        user_cti_profile_dao.edit(user_cti_profile)

        assert_that(user.cti_profile_id, equal_to(cti_profile.id))
        assert_that(user.enableclient, 1)

    def test_edit_enabled_not_set(self):
        cti_profile = CtiProfile(id=2, name='Test')
        self.add_me(cti_profile)
        user = self.add_user(cti_profile_id=None, enableclient=1)
        user_cti_profile = UserCtiProfile(user_id=user.id, cti_profile_id=cti_profile.id)

        user_cti_profile_dao.edit(user_cti_profile)

        assert_that(user.cti_profile_id, equal_to(cti_profile.id))
        assert_that(user.enableclient, 0)
