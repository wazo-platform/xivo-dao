# -*- coding: utf-8 -*-

# Copyright (C) 2016 Proformatique Inc.
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

from hamcrest import (assert_that,
                      contains,
                      contains_inanyorder,
                      empty,
                      equal_to,
                      has_items,
                      has_properties,
                      has_property,
                      is_not,
                      none)

from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.ivr import IVR
from xivo_dao.alchemy.ivr_choice import IVRChoice
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.resources.ivr import dao as ivr_dao
from xivo_dao.helpers.exception import NotFoundError, InputError
from xivo_dao.resources.utils.search import SearchResult


class TestFind(DAOTestCase):

    def test_find_no_ivr(self):
        result = ivr_dao.find(42)

        assert_that(result, none())

    def test_find(self):
        ivr_row = self.add_ivr()

        ivr = ivr_dao.find(ivr_row.id)

        assert_that(ivr, equal_to(ivr_row))


class TestGet(DAOTestCase):

    def test_get_no_ivr(self):
        self.assertRaises(NotFoundError, ivr_dao.get, 42)

    def test_get(self):
        ivr_row = self.add_ivr()

        ivr = ivr_dao.get(ivr_row.id)

        assert_that(ivr, equal_to(ivr_row))
        assert_that(ivr.choices, contains())


class TestFindBy(DAOTestCase):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, ivr_dao.find_by, invalid=42)

    def test_find_by_name(self):
        ivr_row = self.add_ivr(name='myname')

        ivr = ivr_dao.find_by(name='myname')

        assert_that(ivr, equal_to(ivr_row))
        assert_that(ivr.name, equal_to('myname'))

    def test_find_by_description(self):
        ivr_row = self.add_ivr(description='mydescription')

        ivr = ivr_dao.find_by(description='mydescription')

        assert_that(ivr, equal_to(ivr_row))
        assert_that(ivr.description, equal_to('mydescription'))

    def test_given_ivr_does_not_exist_then_returns_null(self):
        ivr = ivr_dao.find_by(id=42)

        assert_that(ivr, none())


class TestGetBy(DAOTestCase):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, ivr_dao.get_by, invalid=42)

    def test_get_by_name(self):
        ivr_row = self.add_ivr(name='myname')

        ivr = ivr_dao.get_by(name='myname')

        assert_that(ivr, equal_to(ivr_row))
        assert_that(ivr.name, equal_to('myname'))

    def test_get_by_description(self):
        ivr_row = self.add_ivr(description='mydescription')

        ivr = ivr_dao.get_by(description='mydescription')

        assert_that(ivr, equal_to(ivr_row))
        assert_that(ivr.description, equal_to('mydescription'))

    def test_given_ivr_does_not_exist_then_raises_error(self):
        self.assertRaises(NotFoundError, ivr_dao.get_by, id='42')


class TestFindAllBy(DAOTestCase):

    def test_find_all_by_no_ivr(self):
        result = ivr_dao.find_all_by(description='toto')

        assert_that(result, contains())

    def test_find_all_by_native_column(self):
        ivr1 = self.add_ivr(description='MyIVR')
        ivr2 = self.add_ivr(description='MyIVR')

        ivrs = ivr_dao.find_all_by(description='MyIVR')

        assert_that(ivrs, has_items(has_property('id', ivr1.id),
                                    has_property('id', ivr2.id)))


class TestSearch(DAOTestCase):

    def assert_search_returns_result(self, search_result, **parameters):
        result = ivr_dao.search(**parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestSearch):

    def test_given_no_ivr_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_one_ivr_then_returns_one_result(self):
        ivr = self.add_ivr()
        expected = SearchResult(1, [ivr])

        self.assert_search_returns_result(expected)


class TestSearchGivenMultipleIncall(TestSearch):

    def setUp(self):
        super(TestSearch, self).setUp()
        self.ivr1 = self.add_ivr(name='Ashton', description='resto')
        self.ivr2 = self.add_ivr(name='Beaugarton', description='bar')
        self.ivr3 = self.add_ivr(name='Casa', description='resto')
        self.ivr4 = self.add_ivr(name='Dunkin', description='resto')

    def test_when_searching_then_returns_one_result(self):
        expected = SearchResult(1, [self.ivr2])

        self.assert_search_returns_result(expected, search='eau')

    def test_when_searching_with_an_extra_argument(self):
        expected_resto = SearchResult(1, [self.ivr1])
        self.assert_search_returns_result(expected_resto, search='ton', description='resto')

        expected_bar = SearchResult(1, [self.ivr2])
        self.assert_search_returns_result(expected_bar, search='ton', description='bar')

        expected_all_resto = SearchResult(3, [self.ivr1, self.ivr3, self.ivr4])
        self.assert_search_returns_result(expected_all_resto, description='resto', order='name')

    def test_when_sorting_then_returns_result_in_ascending_order(self):
        expected = SearchResult(4,
                                [self.ivr1,
                                 self.ivr2,
                                 self.ivr3,
                                 self.ivr4])

        self.assert_search_returns_result(expected, order='name')

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(self):
        expected = SearchResult(4, [self.ivr4,
                                    self.ivr3,
                                    self.ivr2,
                                    self.ivr1])

        self.assert_search_returns_result(expected, order='name', direction='desc')

    def test_when_limiting_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.ivr1])

        self.assert_search_returns_result(expected, limit=1)

    def test_when_skipping_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.ivr2, self.ivr3, self.ivr4])

        self.assert_search_returns_result(expected, skip=1)

    def test_when_doing_a_paginated_search_then_returns_a_paginated_result(self):
        expected = SearchResult(3, [self.ivr3])

        self.assert_search_returns_result(expected,
                                          search='resto',
                                          order='name',
                                          direction='desc',
                                          skip=1,
                                          limit=1)


class TestCreate(DAOTestCase):

    def test_create_minimal_fields(self):
        ivr = IVR(name='myivr', menu_sound='menu')
        created_ivr = ivr_dao.create(ivr)

        row = self.session.query(IVR).first()

        assert_that(created_ivr, equal_to(row))
        assert_that(created_ivr, has_properties(id=is_not(none()),
                                                name='myivr',
                                                greeting_sound=none(),
                                                menu_sound='menu',
                                                invalid_sound=none(),
                                                abort_sound=none(),
                                                description=none(),
                                                invalid_destination=none(),
                                                timeout_destination=none(),
                                                abort_destination=none()))

    def test_create_with_all_fields(self):
        ivr = IVR(name='myivr',
                  greeting_sound='greeting',
                  menu_sound='menu',
                  invalid_sound='invalid',
                  abort_sound='abort',
                  timeout=10,
                  max_tries=2,
                  description='description',
                  invalid_destination=Dialaction(action='user', actionarg1='1'),
                  timeout_destination=Dialaction(action='user', actionarg1='2'),
                  abort_destination=Dialaction(action='user', actionarg1='3'),
                  choices=[IVRChoice(exten='1', destination=Dialaction(action='user', actionarg1='4'))])

        created_ivr = ivr_dao.create(ivr)

        row = self.session.query(IVR).first()

        assert_that(created_ivr, equal_to(row))
        assert_that(created_ivr, has_properties(id=is_not(none()),
                                                name='myivr',
                                                greeting_sound='greeting',
                                                menu_sound='menu',
                                                invalid_sound='invalid',
                                                abort_sound='abort',
                                                timeout=10,
                                                max_tries=2,
                                                description='description',
                                                invalid_destination=has_properties(action='user', actionarg1='1'),
                                                timeout_destination=has_properties(action='user', actionarg1='2'),
                                                abort_destination=has_properties(action='user', actionarg1='3')))
        assert_that(created_ivr.choices, contains(
            has_properties(exten='1', destination=has_properties(action='user', actionarg1='4')),
        ))


class TestEdit(DAOTestCase):

    def test_edit_all_fields(self):
        ivr = ivr_dao.create(IVR(name='myivr',
                                 greeting_sound='greeting',
                                 menu_sound='menu',
                                 invalid_sound='invalid',
                                 abort_sound='abort',
                                 timeout=10,
                                 max_tries=2,
                                 description='description',
                                 invalid_destination=Dialaction(action='user', actionarg1='1'),
                                 timeout_destination=Dialaction(action='user', actionarg1='2'),
                                 choices=[IVRChoice(exten='1', destination=Dialaction(action='user', actionarg1='4'))]))

        ivr = ivr_dao.get(ivr.id)
        ivr.name = 'zmyivr'
        ivr.greeting_sound = 'zgreeting'
        ivr.menu_sound = 'zmenu'
        ivr.invalid_sound = 'zinvalid'
        ivr.abort_sound = 'zabort'
        ivr.timeout = 42
        ivr.max_tries = 1337
        ivr.description = 'lol'
        ivr.invalid_destination = Dialaction(action='user', actionarg1='3')
        ivr.timeout_destination = Dialaction(action='user', actionarg1='4')
        ivr.choices = [IVRChoice(exten='2', destination=Dialaction(action='none'))]

        ivr_dao.edit(ivr)

        row = self.session.query(IVR).first()

        assert_that(ivr, equal_to(row))
        assert_that(ivr, has_properties(name='zmyivr',
                                        greeting_sound='zgreeting',
                                        menu_sound='zmenu',
                                        invalid_sound='zinvalid',
                                        abort_sound='zabort',
                                        timeout=42,
                                        max_tries=1337,
                                        description='lol',
                                        invalid_destination=has_properties(action='user', actionarg1='3'),
                                        timeout_destination=has_properties(action='user', actionarg1='4')))
        assert_that(ivr.choices, contains(
            has_properties(exten='2', destination=has_properties(action='none')),
        ))

    def test_edit_set_fields_to_null(self):
        ivr = ivr_dao.create(IVR(name='myivr',
                                 greeting_sound='greeting',
                                 menu_sound='menu',
                                 invalid_sound='invalid',
                                 abort_sound='abort',
                                 timeout=10,
                                 max_tries=2,
                                 description='description',
                                 invalid_destination=Dialaction(action='user', actionarg1='1'),
                                 timeout_destination=Dialaction(action='user', actionarg1='2'),
                                 choices=[IVRChoice(exten='1', destination=Dialaction(action='user', actionarg1='3'))]))

        ivr = ivr_dao.get(ivr.id)
        ivr.greeting_sound = None
        ivr.invalid_sound = None
        ivr.abort_sound = None
        ivr.description = None
        ivr.invalid_destination = None
        ivr.timeout_destination = None
        ivr.choices = []

        ivr_dao.edit(ivr)

        row = self.session.query(IVR).first()
        assert_that(ivr, equal_to(row))
        assert_that(ivr, has_properties(id=is_not(none()),
                                        name='myivr',
                                        greeting_sound=none(),
                                        menu_sound='menu',
                                        invalid_sound=none(),
                                        abort_sound=none(),
                                        description=none(),
                                        invalid_destination=none(),
                                        timeout_destination=none()))
        assert_that(ivr.choices, empty())

    def test_when_removing_choices_then_choices_are_deleted(self):
        ivr = ivr_dao.create(IVR(name='myivr',
                                 menu_sound='menu',
                                 choices=[IVRChoice(exten='1', destination=Dialaction(action='none'))]))

        ivr = ivr_dao.get(ivr.id)
        ivr.choices = []

        ivr_dao.edit(ivr)

        assert_that(self.session.query(IVRChoice).all(), empty())
        assert_that(self.session.query(Dialaction).all(), empty())


class TestDelete(DAOTestCase):

    def test_delete(self):
        ivr = self.add_ivr()

        ivr_dao.delete(ivr)

        row = self.session.query(IVR).first()
        assert_that(row, none())

    def test_when_deleting_then_dialactions_are_deleted(self):
        ivr = self.add_ivr()
        self.add_dialaction(event='timeout', category='ivr', categoryval=str(ivr.id))

        ivr_dao.delete(ivr)

        dialaction = self.session.query(Dialaction).first()
        assert_that(dialaction, none())

    def test_when_deleting_then_choices_are_deleted(self):
        ivr = self.add_ivr()
        ivr_choice = self.add_ivr_choice(ivr_id=ivr.id)
        self.add_dialaction(category='ivr_choice', categoryval=str(ivr_choice.id))

        ivr_dao.delete(ivr)

        assert_that(self.session.query(IVRChoice).first(), none())
        assert_that(self.session.query(Dialaction).first(), none())

    def test_when_deleting_then_dialactions_are_unlinked(self):
        ivr = self.add_ivr()
        self.add_dialaction(action='ivr', actionarg1=str(ivr.id), linked=1)

        ivr_dao.delete(ivr)

        dialaction = self.session.query(Dialaction).filter(Dialaction.actionarg1 == str(ivr.id)).first()
        assert_that(dialaction, has_properties(linked=0))


class TestRelationship(DAOTestCase):

    def test_dialactions_relationship(self):
        ivr_row = self.add_ivr()
        dialaction_row = self.add_dialaction(event='timeout', category='ivr',
                                             categoryval=str(ivr_row.id))

        ivr = ivr_dao.get(ivr_row.id)

        assert_that(ivr, equal_to(ivr_row))
        assert_that(ivr.dialactions['timeout'], equal_to(dialaction_row))

    def test_choices_relationship(self):
        ivr_row = self.add_ivr()
        ivr_choice_row = self.add_ivr_choice(ivr_id=ivr_row.id)
        dialaction_row = self.add_dialaction(category='ivr_choice',
                                             categoryval=str(ivr_choice_row.id))

        ivr = ivr_dao.get(ivr_row.id)

        assert_that(ivr, equal_to(ivr_row))
        assert_that(ivr.choices, contains(ivr_choice_row))
        assert_that(ivr.choices[0].destination, equal_to(dialaction_row))

    def test_incalls_relationship(self):
        ivr_row = self.add_ivr()
        incall1_row = self.add_incall(destination=Dialaction(action='ivr',
                                                             actionarg1=str(ivr_row.id)))
        incall2_row = self.add_incall(destination=Dialaction(action='ivr',
                                                             actionarg1=str(ivr_row.id)))
        ivr = ivr_dao.get(ivr_row.id)
        assert_that(ivr, equal_to(ivr_row))
        assert_that(ivr.incalls, contains_inanyorder(incall1_row, incall2_row))
