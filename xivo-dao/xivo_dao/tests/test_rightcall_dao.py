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
from xivo_dao import rightcall_dao
from xivo_dao.alchemy.rightcall import RightCall
from xivo_dao.tests.test_dao import DAOTestCase

class TestRightCallDAO(DAOTestCase):

    tables = [RightCall]

    def test_add(self):
        right = RightCall(name='test')
        rightcall_dao.add(right)

        result = self.session.query(RightCall).first()
        self.assertEquals(result.name, 'test')

    def test_get_by_name(self):
        self._insert_rightcall('test')
        result = rightcall_dao.get_by_name('test')
        self.assertEquals('test', result.name)

    def _insert_rightcall(self, name):
        right = RightCall(name=name)
        self.session.add(right)
        return right.id
