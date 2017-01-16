# -*- coding: utf-8 -*-

# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from __future__ import unicode_literals

from hamcrest import (assert_that,
                      contains,
                      equal_to,
                      has_items,
                      has_properties,
                      has_property,
                      is_not,
                      none)


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


class TestGet(DAOTestCase):

    def test_get_no_schedule(self):
        self.assertRaises(NotFoundError, schedule_dao.get, 42)

    def test_get(self):
        schedule_row = self.add_schedule()

        schedule = schedule_dao.get(schedule_row.id)

        assert_that(schedule.id, equal_to(schedule.id))


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

        assert_that(schedules, has_items(has_property('id', schedule1.id),
                                         has_property('id', schedule2.id)))


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
        expected = SearchResult(4,
                                [self.schedule1,
                                 self.schedule2,
                                 self.schedule3,
                                 self.schedule4])

        self.assert_search_returns_result(expected, order='name')

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(self):
        expected = SearchResult(4, [self.schedule4,
                                    self.schedule3,
                                    self.schedule2,
                                    self.schedule1])

        self.assert_search_returns_result(expected, order='name', direction='desc')

    def test_when_limiting_then_returns_right_name_of_items(self):
        expected = SearchResult(4, [self.schedule1])

        self.assert_search_returns_result(expected, limit=1)

    def test_when_skipping_then_returns_right_name_of_items(self):
        expected = SearchResult(4, [self.schedule2, self.schedule3, self.schedule4])

        self.assert_search_returns_result(expected, skip=1)

    def test_when_doing_a_paginated_search_then_returns_a_paginated_result(self):
        expected = SearchResult(3, [self.schedule2])

        self.assert_search_returns_result(expected,
                                          search='a',
                                          order='name',
                                          direction='desc',
                                          skip=1,
                                          limit=1)


class TestCreate(DAOTestCase):

    def setUp(self):
        super(TestCreate, self).setUp()
        self.entity = self.add_entity()

    def test_create_minimal_fields(self):
        schedule = Schedule()
        created_schedule = schedule_dao.create(schedule)

        row = self.session.query(Schedule).first()

        assert_that(created_schedule, equal_to(row))
        assert_that(row, has_properties(id=is_not(none()),
                                        entity_id=self.entity.id,
                                        name=None,
                                        timezone=None,
                                        fallback_action='none',
                                        type='none',
                                        fallback_actionid=None,
                                        actionarg1=None,
                                        fallback_actionargs=None,
                                        actionarg2=None,
                                        enabled=True))

    def test_create_with_all_fields(self):
        schedule = Schedule(name='schedule',
                            timezone='time/zone',
                            fallback_action='user',
                            fallback_actionid='2',
                            fallback_actionargs='10',
                            enabled=False)
        created_schedule = schedule_dao.create(schedule)

        row = self.session.query(Schedule).first()

        assert_that(created_schedule, equal_to(row))
        assert_that(row, has_properties(name='schedule',
                                        entity_id=self.entity.id,
                                        timezone='time/zone',
                                        fallback_action='user',
                                        fallback_actionid='2',
                                        fallback_actionargs='10',
                                        enabled=False))


class TestEdit(DAOTestCase):

    def test_edit_all_fields(self):
        schedule = schedule_dao.create(
            Schedule(name='schedule',
                     timezone='time/zone',
                     fallback_action='user',
                     fallback_actionid='2',
                     fallback_actionargs='10',
                     enabled=False)
        )

        schedule = schedule_dao.get(schedule.id)
        schedule.name = 'other_schedule'
        schedule.timezone = 'other/time'
        schedule.type = 'none'
        schedule.actionarg1 = None
        schedule.actionarg2 = None
        schedule.enabled = True

        schedule_dao.edit(schedule)

        row = self.session.query(Schedule).first()

        assert_that(row, has_properties(name='other_schedule',
                                        timezone='other/time',
                                        type='none',
                                        actionarg1=None,
                                        actionarg2=None,
                                        enabled=True))

    def test_edit_set_fields_to_null(self):
        schedule = schedule_dao.create(Schedule(name='schedule',
                                                timezone='123',
                                                actionarg1='2',
                                                actionarg2='10'))

        schedule = schedule_dao.get(schedule.id)
        schedule.name = None
        schedule.timezone = None
        schedule.actionarg1 = None
        schedule.actionarg2 = None

        schedule_dao.edit(schedule)

        row = self.session.query(Schedule).first()
        assert_that(row, has_properties(name=none(),
                                        timezone=none(),
                                        actionarg1=none(),
                                        actionarg2=none()))


class TestDelete(DAOTestCase):

    def test_delete(self):
        schedule = self.add_schedule()

        schedule_dao.delete(schedule)

        row = self.session.query(Schedule).first()
        assert_that(row, none())
