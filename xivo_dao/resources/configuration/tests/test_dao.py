# -*- coding: utf-8 -*-
# Copyright (C) 2013-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

from hamcrest.core import assert_that
from hamcrest.core.core.isequal import equal_to
from xivo_dao.alchemy.ctimain import CtiMain

from xivo_dao.resources.configuration import dao
from xivo_dao.tests.test_dao import DAOTestCase


class TestConfigurationDao(DAOTestCase):

    def test_is_live_reload_enabled(self):
        ctimain = CtiMain(live_reload_conf=0)
        self.add_me(ctimain)

        result = dao.is_live_reload_enabled()

        self.assertFalse(result)

        ctimain.live_reload_conf = 1
        self.add_me(ctimain)

        result = dao.is_live_reload_enabled()

        self.assertTrue(result)

    def test_set_live_reload_status(self):
        ctimain = CtiMain(live_reload_conf=0)
        self.add_me(ctimain)

        dao.set_live_reload_status({'enabled': True})

        assert_that(ctimain.live_reload_conf, equal_to(1))
