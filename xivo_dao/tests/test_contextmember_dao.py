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

from xivo_dao import contextmember_dao
from xivo_dao.alchemy.contextmember import ContextMember
from xivo_dao.tests.test_dao import DAOTestCase


class TestContextMemberDAO(DAOTestCase):

    tables = [ContextMember]

    def setUp(self):
        self.empty_tables()

    def test_add(self):
        contextmember = ContextMember()
        contextmember.varname = "context"
        contextmember.type = "voicemail"
        contextmember.typeval = "1"
        contextmember.context = "default"

        contextmember_dao.add(contextmember)
        result = self.session.query(ContextMember).first()
        self.assertEquals(contextmember, result)

    def test_delete_by_type_typeval(self):
        self._insert_contextmember('voicemail', '1')
        self._insert_contextmember('voicemail', '2')
        contextmember_dao.delete_by_type_typeval('voicemail', '1')

        result = self.session.query(ContextMember).all()
        self.assertEquals(1, len(result))
        self.assertEquals('2', result[0].typeval)

    def _insert_contextmember(self, typename, typeval, context="default", varname="context"):
        contextmember = ContextMember(type=typename, typeval=typeval, context=context, varname=varname)
        self.add_me(contextmember)

    def test_get_by_type_typeval(self):
        self._insert_contextmember('voicemail', '1')
        self._insert_contextmember('voicemail', '2')
        result = contextmember_dao.get_by_type_typeval('voicemail', '1')
        self.assertEquals('1', result.typeval)
