# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import assert_that, contains_inanyorder
from xivo_dao import cti_context_dao
from xivo_dao.tests.test_dao import DAOTestCase


class TestCTIContextDAO(DAOTestCase):

    def test_get_profile_names(self):
        self.add_cti_context(name='foo')
        self.add_cti_context(name='bar')

        result = cti_context_dao.get_context_names()

        assert_that(result, contains_inanyorder('foo', 'bar'))
