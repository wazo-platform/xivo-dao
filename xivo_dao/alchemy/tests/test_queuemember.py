# -*- coding: utf-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import (assert_that,
                      equal_to,
                      is_,
                      none)

from xivo_dao.alchemy.groupfeatures import GroupFeatures
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.alchemy.queuemember import QueueMember
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


class TestPropriety(DAOTestCase):

    def test_exten_with_local(self):
        member = QueueMember(interface='Local/123@default')
        assert_that(member.exten, equal_to('123'))

    def test_exten_with_no_local(self):
        member = QueueMember(interface='SIP/123')
        assert_that(member.exten, is_(none()))

    def test_context_with_local(self):
        member = QueueMember(interface='Local/123@default')
        assert_that(member.context, equal_to('default'))

    def test_context_with_no_local(self):
        member = QueueMember(interface='SIP/123')
        assert_that(member.context, is_(none()))
