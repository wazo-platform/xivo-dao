# -*- coding: utf-8 -*-
# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import unicode_literals

from hamcrest import (
    assert_that,
    contains,
    equal_to,
    has_items,
    has_properties,
    has_property,
    is_not,
    none
)
from sqlalchemy.inspection import inspect

from xivo_dao.alchemy.schedule import Schedule
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.helpers.exception import NotFoundError, InputError
from xivo_dao.resources.schedule import dao as schedule_dao
from xivo_dao.tests.test_dao import DAOTestCase


class TestFind(DAOTestCase):

    def test_find_no_schedule(self):
        result = schedule_dao.find(42)

        assert_that(result, none())

    def test_find(self):
        schedule_row = self.add_schedule()

        schedule = schedule_dao.find(schedule_row.id)

        assert_that(schedule, equal_to(schedule_row))

    def test_find_multi_tenant(self):
        tenant = self.add_tenant()
        schedule = self.add_schedule(tenant_uuid=tenant.uuid)

        result = schedule_dao.find(schedule.id, tenant_uuids=[tenant.uuid])
        assert_that(result, equal_to(schedule))

        result = schedule_dao.find(schedule.id, tenant_uuids=[self.default_tenant.uuid])
        assert_that(result, none())


class TestGet(DAOTestCase):

    def test_get_no_schedule(self):
        self.assertRaises(NotFoundError, schedule_dao.get, 42)

    def test_get(self):
        schedule_row = self.add_schedule()

        schedule = schedule_dao.get(schedule_row.id)

        assert_that(schedule.id, equal_to(schedule.id))

    def test_get_multi_tenant(self):
        tenant = self.add_tenant()

        schedule_row = self.add_schedule(tenant_uuid=tenant.uuid)
        schedule = schedule_dao.get(schedule_row.id, tenant_uuids=[tenant.uuid])
        assert_that(schedule, equal_to(schedule_row))

        schedule_row = self.add_schedule()
        self.assertRaises(
            NotFoundError,
            schedule_dao.get, schedule_row.id, tenant_uuids=[tenant.uuid],
        )


class TestFindBy(DAOTestCase):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, schedule_dao.find_by, invalid=42)

    def test_find_by_name(self):
        schedule_row = self.add_schedule(name='123')

        schedule = schedule_dao.find_by(name='123')

        assert_that(schedule, equal_to(schedule_row))
        assert_that(schedule.name, equal_to('123'))

    def test_given_schedule_does_not_exist_then_returns_null(self):
        schedule = schedule_dao.find_by(name='42')

        assert_that(schedule, none())

    def test_find_by_multi_tenant(self):
        tenant = self.add_tenant()

        schedule_row = self.add_schedule()
        schedule = schedule_dao.find_by(id=schedule_row.id, tenant_uuids=[tenant.uuid])
        assert_that(schedule, none())

        schedule_row = self.add_schedule(tenant_uuid=tenant.uuid)
        schedule = schedule_dao.find_by(id=schedule_row.id, tenant_uuids=[tenant.uuid])
        assert_that(schedule, equal_to(schedule_row))


class TestGetBy(DAOTestCase):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, schedule_dao.get_by, invalid=42)

    def test_get_by_name(self):
        schedule_row = self.add_schedule(name='123')

        schedule = schedule_dao.get_by(name='123')

        assert_that(schedule, equal_to(schedule_row))
        assert_that(schedule.name, equal_to('123'))

    def test_given_schedule_does_not_exist_then_raises_error(self):
        self.assertRaises(NotFoundError, schedule_dao.get_by, name='42')


class TestFindAllBy(DAOTestCase):

    def test_find_all_by_no_schedules(self):
        result = schedule_dao.find_all_by(name='123')

        assert_that(result, contains())

    def test_find_all_by_renamed_column(self):
        pass

    def test_find_all_by_native_column(self):
        schedule1 = self.add_schedule(name='schedule')
        schedule2 = self.add_schedule(name='schedule')

        schedules = schedule_dao.find_all_by(name='schedule')

        assert_that(schedules, has_items(
            has_property('id', schedule1.id),
            has_property('id', schedule2.id)
        ))


class TestSearch(DAOTestCase):

    def assert_search_returns_result(self, search_result, **parameters):
        result = schedule_dao.search(**parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestSearch):

    def test_given_no_schedules_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_one_schedule_then_returns_one_result(self):
        schedule = self.add_schedule()
        expected = SearchResult(1, [schedule])

        self.assert_search_returns_result(expected)


class TestSearchGivenMultipleSchedules(TestSearch):

    def setUp(self):
        super(TestSearch, self).setUp()
        self.schedule1 = self.add_schedule(name='Ashton', timezone='resto')
        self.schedule2 = self.add_schedule(name='Beaugarton', timezone='bar')
        self.schedule3 = self.add_schedule(name='Casa', timezone='resto')
        self.schedule4 = self.add_schedule(name='Dunkin', timezone='resto')

    def test_when_searching_then_returns_one_result(self):
        expected = SearchResult(1, [self.schedule2])

        self.assert_search_returns_result(expected, search='eau')

    def test_when_searching_with_an_extra_argument(self):
        expected_resto = SearchResult(1, [self.schedule1])
        self.assert_search_returns_result(expected_resto, search='ton', timezone='resto')

        expected_bar = SearchResult(1, [self.schedule2])
        self.assert_search_returns_result(expected_bar, search='ton', timezone='bar')

        expected_all_resto = SearchResult(3, [self.schedule1, self.schedule3, self.schedule4])
        self.assert_search_returns_result(expected_all_resto, timezone='resto', order='timezone')

    def test_when_searching_with_a_custom_extra_argument(self):
        expected_allow = SearchResult(1, [self.schedule2])
        self.assert_search_returns_result(expected_allow, timezone='bar')

        expected_all_deny = SearchResult(3, [self.schedule1, self.schedule3, self.schedule4])
        self.assert_search_returns_result(expected_all_deny, timezone='resto')

    def test_when_sorting_then_returns_result_in_ascending_order(self):
        expected = SearchResult(4, [
            self.schedule1,
            self.schedule2,
            self.schedule3,
            self.schedule4,
        ])

        self.assert_search_returns_result(expected, order='name')

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(self):
        expected = SearchResult(4, [
            self.schedule4,
            self.schedule3,
            self.schedule2,
            self.schedule1,
        ])

        self.assert_search_returns_result(expected, order='name', direction='desc')

    def test_when_limiting_then_returns_right_name_of_items(self):
        expected = SearchResult(4, [self.schedule1])

        self.assert_search_returns_result(expected, limit=1)

    def test_when_skipping_then_returns_right_name_of_items(self):
        expected = SearchResult(4, [self.schedule2, self.schedule3, self.schedule4])

        self.assert_search_returns_result(expected, skip=1)

    def test_when_doing_a_paginated_search_then_returns_a_paginated_result(self):
        expected = SearchResult(3, [self.schedule2])

        self.assert_search_returns_result(
            expected,
            search='a',
            order='name',
            direction='desc',
            skip=1,
            limit=1,
        )


class TestCreate(DAOTestCase):

    def setUp(self):
        super(TestCreate, self).setUp()
        tenant = self.add_tenant()
        self.entity = self.add_entity(tenant_uuid=tenant.uuid)

    def test_create_minimal_fields(self):
        schedule_model = Schedule(tenant_uuid=self.default_tenant.uuid)
        schedule = schedule_dao.create(schedule_model)

        self.session.expire_all()
        assert_that(inspect(schedule).persistent)
        assert_that(schedule, has_properties(
            id=is_not(none()),
            tenant_uuid=self.default_tenant.uuid,
            entity_id=self.entity.id,
            name=None,
            timezone=None,
            fallback_action='none',
            type='none',
            fallback_actionid=None,
            actionarg1=None,
            fallback_actionargs=None,
            actionarg2=None,
            enabled=True
        ))

    def test_create_with_all_fields(self):
        schedule_model = Schedule(
            name='schedule',
            tenant_uuid=self.default_tenant.uuid,
            timezone='time/zone',
            fallback_action='user',
            fallback_actionid='2',
            fallback_actionargs='10',
            enabled=False,
        )
        schedule = schedule_dao.create(schedule_model)

        self.session.expire_all()
        assert_that(inspect(schedule).persistent)
        assert_that(schedule, has_properties(
            name='schedule',
            tenant_uuid=self.default_tenant.uuid,
            entity_id=self.entity.id,
            timezone='time/zone',
            fallback_action='user',
            fallback_actionid='2',
            fallback_actionargs='10',
            enabled=False,
        ))


class TestEdit(DAOTestCase):

    def test_edit_all_fields(self):
        schedule = self.add_schedule(
            name='schedule',
            timezone='time/zone',
            fallback_action='user',
            fallback_actionid='2',
            fallback_actionargs='10',
            enabled=False,
        )

        self.session.expire_all()
        schedule.name = 'other_schedule'
        schedule.timezone = 'other/time'
        schedule.type = 'none'
        schedule.actionarg1 = None
        schedule.actionarg2 = None
        schedule.enabled = True

        schedule_dao.edit(schedule)

        self.session.expire_all()
        assert_that(schedule, has_properties(
            name='other_schedule',
            timezone='other/time',
            type='none',
            actionarg1=None,
            actionarg2=None,
            enabled=True,
        ))

    def test_edit_set_fields_to_null(self):
        schedule = self.add_schedule(
            name='schedule',
            timezone='123',
            actionarg1='2',
            actionarg2='10',
        )

        self.session.expire_all()
        schedule.name = None
        schedule.timezone = None
        schedule.actionarg1 = None
        schedule.actionarg2 = None

        schedule_dao.edit(schedule)

        self.session.expire_all()
        assert_that(schedule, has_properties(
            name=none(),
            timezone=none(),
            actionarg1=none(),
            actionarg2=none(),
        ))


class TestDelete(DAOTestCase):

    def test_delete(self):
        schedule = self.add_schedule()

        schedule_dao.delete(schedule)

        assert_that(inspect(schedule).deleted)
