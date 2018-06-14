# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import (
    assert_that,
    contains,
    contains_inanyorder,
    empty,
    has_properties,
    none,
    not_,
)

from xivo_dao.tests.test_dao import DAOTestCase

from ..context import Context
from ..contextinclude import ContextInclude


class TestContexts(DAOTestCase):

    def test_create(self):
        tenant = self.add_tenant()
        context = self.add_context()
        included_context = Context(tenant_uuid=tenant.uuid, name='included_context')

        context.contexts = [included_context]
        self.session.flush()

        self.session.expire_all()
        assert_that(context.contexts, contains(has_properties(name='included_context')))

    def test_associate_order_by(self):
        context = self.add_context()
        included_context1 = self.add_context()
        included_context2 = self.add_context()
        included_context3 = self.add_context()

        context.contexts = [included_context2, included_context3, included_context1]
        self.session.flush()

        self.session.expire_all()
        assert_that(context.contexts, contains(
            included_context2,
            included_context3,
            included_context1,
        ))
        context_includes = self.session.query(ContextInclude).filter_by(context=context.name).all()
        assert_that(context_includes, contains_inanyorder(
            has_properties(include=included_context2.name, priority=0),
            has_properties(include=included_context3.name, priority=1),
            has_properties(include=included_context1.name, priority=2),
        ))

    def test_dissociate(self):
        context = self.add_context()
        context.contexts = [self.add_context(), self.add_context(), self.add_context()]
        self.session.flush()

        context.contexts = []
        self.session.flush()

        self.session.expire_all()
        assert_that(context.contexts, empty())

        row = self.session.query(Context).first()
        assert_that(row, not_(none()))

        row = self.session.query(ContextInclude).first()
        assert_that(row, none())


class TestDelete(DAOTestCase):

    def test_context_include_parents(self):
        context = self.add_context()
        included_context = self.add_context()
        self.add_context_include(context=context.name, include=included_context.name)

        self.session.delete(context)
        self.session.flush()

        row = self.session.query(ContextInclude).first()
        assert_that(row, none())

    def test_context_include_children(self):
        context = self.add_context()
        included_context = self.add_context()
        self.add_context_include(context=context.name, include=included_context.name)

        self.session.delete(included_context)
        self.session.flush()

        row = self.session.query(ContextInclude).first()
        assert_that(row, none())
