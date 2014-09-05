# -*- coding: utf-8 -*-

# Copyright (C) 2012-2014 Avencall
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

from xivo_dao import group_dao
from xivo_dao.alchemy.groupfeatures import GroupFeatures
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.helpers.db_utils import commit_or_abort
from xivo_dao.tests.test_dao import DAOTestCase


class TestGroupDAO(DAOTestCase):

    def test_get_name(self):
        group = self._insert_group('test_name', '1234', 'my_ctx')

        result = group_dao.get_name(group.id)

        self.assertEqual(result, group.name)

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

        with commit_or_abort(self.session):
            self.session.add(group)

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

        with commit_or_abort(self.session):
            self.session.add(queue_member)
