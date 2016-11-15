# -*- coding: utf-8 -*-

# Copyright (C) 2016 Proformatique Inc.
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

from hamcrest import (assert_that,
                      equal_to)

from xivo_dao.alchemy.groupfeatures import GroupFeatures
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.tests.test_dao import DAOTestCase


class TestDelete(DAOTestCase):

    def test_group_is_not_deleted(self):
        group = self.add_group()
        queue_member = self.add_queue_member(queue_name=group.name, category='group')

        self.session.delete(queue_member)
        self.session.flush()

        row = self.session.query(GroupFeatures).first()
        assert_that(row, equal_to(group))

    def test_user_is_not_deleted(self):
        user = self.add_user()
        queue_member = self.add_queue_member(usertype='user', userid=user.id)

        self.session.delete(queue_member)
        self.session.flush()

        row = self.session.query(UserFeatures).first()
        assert_that(row, equal_to(user))
