# Copyright 2018-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


from hamcrest import (
    assert_that,
    equal_to,
    has_properties,
)

from xivo_dao.tests.test_dao import DAOTestCase

from ..contextinclude import ContextInclude


class TestIncludedContext(DAOTestCase):

    def test_getter(self):
        context = self.add_context()
        context_include = self.add_context_include(include=context.name)
        assert_that(context_include.included_context, equal_to(context))

    def test_setter(self):
        context = self.add_context()
        context_include = self.add_context_include()
        context_include.included_context = context
        self.session.flush()

        self.session.expire_all()
        assert_that(context_include.included_context, has_properties(
            name=context.name
        ))


class TestCreator(DAOTestCase):

    def test_included_context_set_include(self):
        context = self.add_context()
        context_include = ContextInclude(included_context=context, context='random')
        self.session.add(context_include)
        self.session.flush()

        assert_that(context_include, has_properties(include=context.name))
