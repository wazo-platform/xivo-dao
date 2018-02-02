# -*- coding: UTF-8 -*-
# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import assert_that, has_items, contains

from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.resources.bsfilter import dao as bsfilter_dao

from xivo_dao.resources.bsfilter.model import FilterMember


class TestFindByMemberId(DAOTestCase):

    def test_given_no_callfilter_or_members_then_returns_empty_list(self):
        result = bsfilter_dao.find_all_by_member_id(1)

        assert_that(result, contains())

    def test_when_filter_has_boss_and_secretary_then_returns_memberships(self):
        boss_id = 10
        secretary_id = 20

        callfilter_row = self.add_bsfilter()
        boss_member_row = self.add_filter_member(callfilter_row.id, boss_id, 'boss')
        secretary_member_row = self.add_filter_member(callfilter_row.id, secretary_id, 'secretary')

        boss_member = FilterMember(id=boss_member_row.id, member_id=boss_id, role='boss')
        secretary_member = FilterMember(id=secretary_member_row.id, member_id=secretary_id, role='secretary')

        result = bsfilter_dao.find_all_by_member_id(boss_id)
        assert_that(result, contains(boss_member))

        result = bsfilter_dao.find_all_by_member_id(secretary_id)
        assert_that(result, contains(secretary_member))

    def test_when_member_is_in_two_filters_then_returns_both_memberships(self):
        boss_id = 10

        first_callfilter = self.add_bsfilter(name='first')
        first_membership_row = self.add_filter_member(first_callfilter.id, boss_id, 'boss')

        second_callfilter = self.add_bsfilter(name='second')
        second_membership_row = self.add_filter_member(second_callfilter.id, boss_id, 'boss')

        first_member = FilterMember(id=first_membership_row.id, member_id=boss_id, role='boss')
        second_member = FilterMember(id=second_membership_row.id, member_id=boss_id, role='boss')

        result = bsfilter_dao.find_all_by_member_id(boss_id)
        assert_that(result, has_items(first_member, second_member))
