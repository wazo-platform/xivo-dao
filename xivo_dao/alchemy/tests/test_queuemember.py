# -*- coding: utf-8 -*-

# Copyright (C) 2016 Proformatique Inc.
#
# SPDX-License-Identifier: GPL-3.0+

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
