# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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

from xivo_dao import usersip_dao
from xivo_dao.alchemy.usersip import UserSIP
from xivo_dao.tests.test_dao import DAOTestCase


class TestUserSIPDAO(DAOTestCase):

    tables = [UserSIP]

    def setUp(self):
        self.empty_tables()

    def test_create(self):
        usersip = UserSIP(name='abcd', type='friend')

        usersip_dao.create(usersip)
        self.assertTrue(usersip.id > 0)
        self.assertEquals(1, len(self._get_all()))
        self.assertEquals(usersip, self._get_all()[0])

    def _get_all(self):
        return self.session.query(UserSIP).all()

    def _insert(self, name, typename='friend'):
        usersip = UserSIP(name=name, type=typename)
        self.add_me(usersip)
        return usersip.id

    def test_get(self):
        gen_id = self._insert("abcd")
        result = usersip_dao.get(gen_id)
        self.assertEquals(result.id, gen_id)

    def test_delete(self):
        gen_id = self._insert("abcd")
        usersip_dao.delete(gen_id)
        self.assertFalse(gen_id in [item.id for item in self._get_all()])
