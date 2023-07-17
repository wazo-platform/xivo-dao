# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from hamcrest import (
    assert_that,
    equal_to,
    has_properties,
)
from xivo_dao.alchemy.extension import Extension
from xivo_dao.tests.test_dao import DAOTestCase


class TestIsPattern(unittest.TestCase):

    def test_is_not_pattern(self):
        extension = Extension(exten='1000')
        assert_that(extension.is_pattern(), equal_to(False))

    def test_is_pattern(self):
        extension = Extension(exten='_XXXX')
        assert_that(extension.is_pattern(), equal_to(True))


class TestIsFeature(unittest.TestCase):

    def test_is_not_feature(self):
        extension = Extension(context='not-features')
        assert_that(extension.is_feature, equal_to(False))

    def test_is_feature(self):
        extension = Extension(context='xivo-features')
        assert_that(extension.is_feature, equal_to(True))


class TestTenantUUID(DAOTestCase):

    def test_that_the_tenant_uuid_matches_the_context(self):
        context = self.add_context()
        extension = self.add_extension(context=context.name)

        assert_that(extension, has_properties(
            tenant_uuid=context.tenant_uuid,
        ))


class TestGetOldContext(DAOTestCase):

    def test_get_old_context(self):
        extension = self.add_extension(context='context')
        extension.context = 'other-context'

        assert_that(extension.context, equal_to('other-context'))
        assert_that(extension.get_old_context(), equal_to('context'))

    def test_get_old_context_without_change(self):
        extension = self.add_extension(context='context')

        assert_that(extension.context, equal_to('context'))
        assert_that(extension.get_old_context(), equal_to('context'))
