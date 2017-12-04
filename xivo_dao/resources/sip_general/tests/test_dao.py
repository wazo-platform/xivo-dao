# -*- coding: utf-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from hamcrest import (assert_that,
                      empty,
                      equal_to,
                      none)

from xivo_dao.alchemy.staticsip import StaticSIP
from xivo_dao.resources.sip_general import dao as sip_general_dao
from xivo_dao.tests.test_dao import DAOTestCase


class TestFindBy(DAOTestCase):

    def test_find_by_no_sip_general(self):
        result = sip_general_dao.find_by()

        assert_that(result, none())

    def test_find_by(self):
        self.add_sip_general_settings(var_metric=3,
                                      var_name='setting1',
                                      var_val='value1')
        row2 = self.add_sip_general_settings(var_metric=2,
                                             var_name='setting2',
                                             var_val='value1')

        sip_general_option = sip_general_dao.find_by(var_name='setting2')

        assert_that(sip_general_option, equal_to(row2))


class TestFindAll(DAOTestCase):

    def test_find_all_no_sip_general(self):
        result = sip_general_dao.find_all()

        assert_that(result, empty())

    def test_find_all(self):
        row1 = self.add_sip_general_settings(var_metric=3,
                                             var_name='setting1',
                                             var_val='value1')
        row2 = self.add_sip_general_settings(var_metric=2,
                                             var_name='setting2',
                                             var_val='value1')
        row3 = self.add_sip_general_settings(var_metric=1,
                                             var_name='setting3',
                                             var_val='value1')
        row4 = self.add_sip_general_settings(var_metric=4,
                                             var_name='setting2',
                                             var_val='value2')

        sip_general = sip_general_dao.find_all()

        assert_that(sip_general, equal_to([row3, row2, row1, row4]))

    def test_find_all_do_not_find_register(self):
        self.add_sip_general_settings(var_metric=1,
                                      var_name='register',
                                      var_val='value1')
        row2 = self.add_sip_general_settings(var_metric=2,
                                             var_name='setting1',
                                             var_val='value1')

        sip_general = sip_general_dao.find_all()

        assert_that(sip_general, equal_to([row2]))

    def test_find_all_do_not_find_var_val_none(self):
        self.add_sip_general_settings(var_metric=1,
                                      var_name='setting1',
                                      var_val=None)
        row2 = self.add_sip_general_settings(var_metric=2,
                                             var_name='setting1',
                                             var_val='value1')

        sip_general = sip_general_dao.find_all()

        assert_that(sip_general, equal_to([row2]))


class TestEditAll(DAOTestCase):

    def test_edit_all(self):
        row1 = StaticSIP(var_name='setting1', var_val='value1')
        row2 = StaticSIP(var_name='setting2', var_val='value1')
        row3 = StaticSIP(var_name='setting3', var_val='value1')
        row4 = StaticSIP(var_name='setting2', var_val='value2')

        sip_general_dao.edit_all([row3, row4, row2, row1])

        sip_general = sip_general_dao.find_all()
        assert_that(sip_general, equal_to([row3, row4, row2, row1]))

    def test_edit_all_do_not_delete_register(self):
        row1 = self.add_sip_general_settings(var_metric=1,
                                             var_name='register',
                                             var_val='value1')

        row2 = StaticSIP(var_name='nat', var_val='value1')

        sip_general_dao.edit_all([row2])

        assert_that(self.session.query(StaticSIP)
                    .filter(StaticSIP.var_name == 'register')
                    .first(), equal_to(row1))

    def test_delete_old_entries(self):
        self.add_sip_general_settings()
        self.add_sip_general_settings()
        row = StaticSIP(var_name='nat', var_val='value1')

        sip_general_dao.edit_all([row])

        sip_general = sip_general_dao.find_all()
        assert_that(sip_general, equal_to([row]))


class TestTable(DAOTestCase):

    def test_values_from_renamed_column(self):
        row1 = StaticSIP(var_name='setting1', var_val='value1', metric=None)
        row2 = StaticSIP(var_name='setting2', var_val='value1', metric=0)
        row3 = StaticSIP(var_name='setting3', var_val='value1', metric=1)

        assert_that(row1.var_metric, equal_to(0))
        assert_that(row2.var_metric, equal_to(1))
        assert_that(row3.var_metric, equal_to(2))
