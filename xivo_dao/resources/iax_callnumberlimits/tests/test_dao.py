# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from hamcrest import (
    assert_that,
    contains,
    contains_inanyorder,
    empty,
)
from xivo_dao.alchemy.iaxcallnumberlimits import IAXCallNumberLimits
from xivo_dao.tests.test_dao import DAOTestCase

from .. import dao as iax_callnumberlimits_dao


class TestFindAll(DAOTestCase):

    def test_find_all_no_iax_callnumberlimits(self):
        result = iax_callnumberlimits_dao.find_all()

        assert_that(result, empty())

    def test_find_all(self):
        row1 = self.add_iax_callnumberlimits()
        row2 = self.add_iax_callnumberlimits()
        row3 = self.add_iax_callnumberlimits()
        row4 = self.add_iax_callnumberlimits()

        iax_callnumberlimits = iax_callnumberlimits_dao.find_all()

        assert_that(iax_callnumberlimits, contains_inanyorder(row1, row2, row3, row4))


class TestEditAll(DAOTestCase):

    def test_edit_all(self):
        row1 = IAXCallNumberLimits(destination='127.0.0.1', netmask='255.255.255.0')
        row2 = IAXCallNumberLimits(destination='127.0.1.1', netmask='255.255.255.0')
        row3 = IAXCallNumberLimits(destination='127.0.2.1', netmask='255.255.255.0')
        row4 = IAXCallNumberLimits(destination='127.0.3.1', netmask='255.255.255.0')

        iax_callnumberlimits_dao.edit_all([row1, row2, row3, row4])

        iax_callnumberlimits = iax_callnumberlimits_dao.find_all()
        assert_that(iax_callnumberlimits, contains_inanyorder(row1, row2, row3, row4))

    def test_delete_old_entries(self):
        self.add_iax_callnumberlimits()
        self.add_iax_callnumberlimits()
        row = IAXCallNumberLimits(destination='0.0.0.0', netmask='0.0.0.0')

        iax_callnumberlimits_dao.edit_all([row])

        iax_callnumberlimits = iax_callnumberlimits_dao.find_all()
        assert_that(iax_callnumberlimits, contains(row))
