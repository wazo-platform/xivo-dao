# -*- coding: utf-8 -*-

# Copyright (C) 2007-2015 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao import context_dao
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.alchemy.context import Context
from xivo_dao.alchemy.contexttype import ContextType


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

    def test_get(self):
        context_name = 'test_context'
        self._insert_context(context_name)

        context = context_dao.get(context_name)

        self.assertEqual(context.name, context_name)
