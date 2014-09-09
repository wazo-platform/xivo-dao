# -*- coding: utf-8 -*-

# Copyright (C) 2007-2014 Avencall
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

from xivo_dao import context_dao
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.alchemy.context import Context
from xivo_dao.alchemy.contexttype import ContextType
from xivo_dao.alchemy.contextnumbers import ContextNumbers


class TestContextDAO(DAOTestCase):

    def _insert_context(self, name, displayname=None, contexttype_name='internal'):
        contexttype = ContextType()
        contexttype.name = contexttype_name
        self.session.add(contexttype)

        context = Context()
        context.name = name
        context.displayname = displayname if displayname else name
        context.entity = 'entity'
        context.contexttype = contexttype_name
        context.description = ''

        self.add_me(context)

    def _insert_contextnumbers(self, context_name):
        contextnumbers = ContextNumbers()
        contextnumbers.context = context_name
        contextnumbers.type = 'user'
        contextnumbers.numberbeg = '1000'
        contextnumbers.numberend = '1999'
        contextnumbers.didlength = 0

        self.add_me(contextnumbers)

    def test_get(self):
        context_name = 'test_context'
        self._insert_context(context_name)

        context = context_dao.get(context_name)

        self.assertEqual(context.name, context_name)

    def test_get_join_elements(self):
        context_name = 'test_context'
        self._insert_context(context_name)
        self._insert_contextnumbers(context_name)

        context, contextnumbers, contexttype, contextinclude = context_dao.get_join_elements(context_name)

        self.assertEqual(context.name, context_name)
        self.assertEqual(contextnumbers.context, context_name)
        self.assertEqual(contextinclude, None)
        self.assertEqual(contexttype.name, context.contexttype)

    def test_all(self):
        context_name1 = 'test_context1'
        self._insert_context(context_name1, contexttype_name='internal1')
        self._insert_contextnumbers(context_name1)

        context_name2 = 'test_context2'
        self._insert_context(context_name2, contexttype_name='internal2')
        self._insert_contextnumbers(context_name2)

        context_full_infos = context_dao.all()

        for row in context_full_infos:
            context, contextnumbers, contexttype, contextinclude = row

            assert(context.name in [context_name1, context_name2])
            assert(contextnumbers.context in [context_name1, context_name2])
            self.assertEqual(contextinclude, None)
            self.assertEqual(contexttype.name, context.contexttype)

    def test_all_empty(self):
        result = context_dao.all()
        self.assertEqual([], result)
