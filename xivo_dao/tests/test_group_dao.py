# -*- coding: utf-8 -*-
# Copyright (C) 2012-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao import group_dao
from xivo_dao.alchemy.groupfeatures import GroupFeatures
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.tests.test_dao import DAOTestCase


class TestGroupDAO(DAOTestCase):

    def test_get_name_number(self):
        group = self._insert_group('test_name', '1234', 'my_ctx')

        name, number = group_dao.get_name_number(group.id)

        self.assertEqual(name, 'test_name')
        self.assertEqual(number, '1234')

    def test_is_user_member_of_group_when_present(self):
        user_id = 1
        group = self._insert_group('foobar', '1234', 'default')
        self._insert_group_member(group.name, 'user', user_id)

        result = group_dao.is_user_member_of_group(user_id, group.id)

        self.assertTrue(result)

    def test_is_user_member_of_group_when_not_present(self):
        user_id = 1
        group = self._insert_group('foobar', '1234', 'default')

        result = group_dao.is_user_member_of_group(user_id, group.id)

        self.assertFalse(result)

    def _insert_group(self, name, number, context):
        group = GroupFeatures()
        group.name = name
        group.number = number
        group.context = context

        self.add_me(group)

        return group

    def _insert_group_member(self, group_name, user_type, user_id):
        queue_member = QueueMember()
        queue_member.queue_name = group_name
        queue_member.interface = 'SIP/abcdef'
        queue_member.penalty = 0
        queue_member.usertype = user_type
        queue_member.userid = user_id
        queue_member.channel = 'foobar'
        queue_member.category = 'group'

        self.add_me(queue_member)
