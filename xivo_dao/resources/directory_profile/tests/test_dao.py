# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

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
