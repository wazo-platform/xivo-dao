# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Avencall
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

from xivo_dao import rightcall_member_dao
from xivo_dao.alchemy.rightcall import RightCall
from xivo_dao.alchemy.rightcallmember import RightCallMember
from xivo_dao.tests.test_dao import DAOTestCase


class TestRightCallMemberDAO(DAOTestCase):

    tables = [RightCall, RightCallMember]

    def setUp(self):
        self.cleanTables()

    def test_add_user_to_rightcall(self):
        userid = 1
        rightid = 2
        rightcall_member_dao.add_user_to_rightcall(userid, rightid)

        result = self.session.query(RightCallMember).first()
        self.assertEquals('1', result.typeval)
        self.assertEquals(2, result.rightcallid)
        self.assertEquals('user', result.type)

    def test_get_by_userid(self):
        self._insert_rightcallmember(1, 2)
        self._insert_rightcallmember(3, 4)
        result = rightcall_member_dao.get_by_userid(1)
        self.assertEquals(len(result), 1)
        self.assertEquals(result[0].typeval, '1')
        self.assertEquals(result[0].rightcallid, 2)

    def test_delete_by_userid(self):
        self._insert_rightcallmember(1, 2)
        self._insert_rightcallmember(3, 4)
        rightcall_member_dao.delete_by_userid(1)

        result = rightcall_member_dao.get_by_userid(1)
        self.assertEquals(result, [])
        result = rightcall_member_dao.get_by_userid(3)
        self.assertEquals(len(result), 1)

    def _insert_rightcallmember(self, userid, rightcallid):
        self.add_me(RightCallMember(type='user', typeval=str(userid), rightcallid=rightcallid))
