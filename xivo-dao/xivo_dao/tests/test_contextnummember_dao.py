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

from xivo_dao import contextnummember_dao
from xivo_dao.alchemy.contextnummember import ContextNumMember
from xivo_dao.tests.test_dao import DAOTestCase


class TestContextNumMemberDAO(DAOTestCase):

    tables = [ContextNumMember]

    def setUp(self):
        self.empty_tables()

    def test_create(self):
        member = ContextNumMember()
        member.context = 'default'
        member.number = '2000'
        member.type = 'user'
        member.typeval = '1'

        contextnummember_dao.create(member)
        self.assertTrue(member in self._get_all())

    def test_create_type_fix(self):
        member = ContextNumMember()
        member.context = 'default'
        member.number = '2000'
        member.type = 'line'
        member.typeval = '1'

        contextnummember_dao.create(member)
        self.assertEquals('user', member.type)

    def _get_all(self):
        return self.session.query(ContextNumMember).all()

    def _insert(self, typename, typeval, context='default', number=''):
        member = ContextNumMember(type=typename, typeval=typeval, context=context, number=number)
        self.add_me(member)
