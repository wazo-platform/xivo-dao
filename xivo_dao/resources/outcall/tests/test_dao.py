# -*- coding: utf-8 -*-

# Copyright (C) 2014-2016 Avencall
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
                      equal_to,
                      has_items,
                      has_properties,
                      has_property,
                      is_not,
                      none)

from xivo_dao.alchemy.dialpattern import DialPattern
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.outcall import Outcall
from xivo_dao.alchemy.rightcallmember import RightCallMember
from xivo_dao.alchemy.schedulepath import SchedulePath
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.resources.outcall import dao as outcall_dao
from xivo_dao.helpers.exception import NotFoundError, InputError
from xivo_dao.resources.utils.search import SearchResult


class TestFind(DAOTestCase):

    def test_find_no_outcall(self):
        result = outcall_dao.find(42)

        assert_that(result, none())

    def test_find(self):
        outcall_row = self.add_outcall()

        outcall = outcall_dao.find(outcall_row.id)

        assert_that(outcall, equal_to(outcall_row))


class TestGet(DAOTestCase):

    def test_get_no_outcall(self):
        self.assertRaises(NotFoundError, outcall_dao.get, 42)

    def test_get(self):
        outcall_row = self.add_outcall()

        outcall = outcall_dao.get(outcall_row.id)

        assert_that(outcall, equal_to(outcall_row))


class TestFindBy(DAOTestCase):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, outcall_dao.find_by, invalid=42)

    def test_find_by_context(self):
        outcall_row = self.add_outcall(context='mycontext')

        outcall = outcall_dao.find_by(context='mycontext')

        assert_that(outcall, equal_to(outcall_row))
        assert_that(outcall.context, equal_to('mycontext'))

    def test_find_by_description(self):
        outcall_row = self.add_outcall(description='mydescription')

        outcall = outcall_dao.find_by(description='mydescription')

        assert_that(outcall, equal_to(outcall_row))
        assert_that(outcall.description, equal_to('mydescription'))

    def test_find_by_name(self):
        outcall_row = self.add_outcall(name='myname')

        outcall = outcall_dao.find_by(name='myname')

        assert_that(outcall, equal_to(outcall_row))
        assert_that(outcall.name, equal_to('myname'))

    def test_find_by_preprocess_subroutine(self):
        outcall_row = self.add_outcall(preprocess_subroutine='mysubroutine')

        outcall = outcall_dao.find_by(preprocess_subroutine='mysubroutine')

        assert_that(outcall, equal_to(outcall_row))
        assert_that(outcall.preprocess_subroutine, equal_to('mysubroutine'))

    def test_given_outcall_does_not_exist_then_returns_null(self):
        outcall = outcall_dao.find_by(id=42)

        assert_that(outcall, none())


class TestGetBy(DAOTestCase):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, outcall_dao.get_by, invalid=42)

    def test_get_by_context(self):
        outcall_row = self.add_outcall(context='mycontext')

        outcall = outcall_dao.get_by(context='mycontext')

        assert_that(outcall, equal_to(outcall_row))
        assert_that(outcall.context, equal_to('mycontext'))

    def test_get_by_description(self):
        outcall_row = self.add_outcall(description='mydescription')

        outcall = outcall_dao.get_by(description='mydescription')

        assert_that(outcall, equal_to(outcall_row))
        assert_that(outcall.description, equal_to('mydescription'))

    def test_get_by_name(self):
        outcall_row = self.add_outcall(name='myname')

        outcall = outcall_dao.get_by(name='myname')

        assert_that(outcall, equal_to(outcall_row))
        assert_that(outcall.name, equal_to('myname'))

    def test_get_by_preprocess_subroutine(self):
        outcall_row = self.add_outcall(preprocess_subroutine='MySubroutine')

        outcall = outcall_dao.get_by(preprocess_subroutine='MySubroutine')

        assert_that(outcall, equal_to(outcall_row))
        assert_that(outcall.preprocess_subroutine, equal_to('MySubroutine'))

    def test_given_outcall_does_not_exist_then_raises_error(self):
        self.assertRaises(NotFoundError, outcall_dao.get_by, id='42')


class TestFindAllBy(DAOTestCase):

    def test_find_all_by_no_outcall(self):
        result = outcall_dao.find_all_by(description='toto')

        assert_that(result, contains())

    def test_find_all_by_custom_column(self):
        pass

    def test_find_all_by_native_column(self):
        outcall1 = self.add_outcall(description='MyOutcall')
        outcall2 = self.add_outcall(description='MyOutcall')

        outcalls = outcall_dao.find_all_by(description='MyOutcall')

        assert_that(outcalls, has_items(has_property('id', outcall1.id),
                                        has_property('id', outcall2.id)))


class TestSearch(DAOTestCase):

    def assert_search_returns_result(self, search_result, **parameters):
        result = outcall_dao.search(**parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestSearch):

    def test_given_no_outcall_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_one_outcall_then_returns_one_result(self):
        outcall = self.add_outcall()
        expected = SearchResult(1, [outcall])

        self.assert_search_returns_result(expected)


class TestSearchGivenMultipleOutcall(TestSearch):

    def setUp(self):
        super(TestSearch, self).setUp()
        self.outcall1 = self.add_outcall(preprocess_subroutine='Ashton', description='resto')
        self.outcall2 = self.add_outcall(preprocess_subroutine='Beaugarton', description='bar')
        self.outcall3 = self.add_outcall(preprocess_subroutine='Casa', description='resto')
        self.outcall4 = self.add_outcall(preprocess_subroutine='Dunkin', description='resto')

    def test_when_searching_then_returns_one_result(self):
        expected = SearchResult(1, [self.outcall2])

        self.assert_search_returns_result(expected, search='eau')

    def test_when_searching_with_an_extra_argument(self):
        expected_resto = SearchResult(1, [self.outcall1])
        self.assert_search_returns_result(expected_resto, search='ton', description='resto')

        expected_bar = SearchResult(1, [self.outcall2])
        self.assert_search_returns_result(expected_bar, search='ton', description='bar')

        expected_all_resto = SearchResult(3, [self.outcall1, self.outcall3, self.outcall4])
        self.assert_search_returns_result(expected_all_resto, description='resto', order='preprocess_subroutine')

    def test_when_sorting_then_returns_result_in_ascending_order(self):
        expected = SearchResult(4,
                                [self.outcall1,
                                 self.outcall2,
                                 self.outcall3,
                                 self.outcall4])

        self.assert_search_returns_result(expected, order='preprocess_subroutine')

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(self):
        expected = SearchResult(4, [self.outcall4,
                                    self.outcall3,
                                    self.outcall2,
                                    self.outcall1])

        self.assert_search_returns_result(expected, order='preprocess_subroutine', direction='desc')

    def test_when_limiting_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.outcall1])

        self.assert_search_returns_result(expected, limit=1)

    def test_when_skipping_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.outcall2, self.outcall3, self.outcall4])

        self.assert_search_returns_result(expected, skip=1)

    def test_when_doing_a_paginated_search_then_returns_a_paginated_result(self):
        expected = SearchResult(3, [self.outcall2])

        self.assert_search_returns_result(expected,
                                          search='a',
                                          order='preprocess_subroutine',
                                          direction='desc',
                                          skip=1,
                                          limit=1)


class TestCreate(DAOTestCase):

    def test_create_minimal_fields(self):
        outcall = Outcall(name='myoutcall', context='to-extern')
        created_outcall = outcall_dao.create(outcall)

        row = self.session.query(Outcall).first()

        assert_that(created_outcall, equal_to(row))
        assert_that(created_outcall, has_properties(id=is_not(none()),
                                                    name='myoutcall',
                                                    context='to-extern',
                                                    hangupringtime=0,
                                                    ring_time=none(),
                                                    internal=0,
                                                    internal_caller_id=False,
                                                    preprocess_subroutine=none(),
                                                    description=none(),
                                                    commented=0,
                                                    enabled=True,
                                                    patterns=[]))

    def test_create_with_all_fields(self):
        outcall = Outcall(name='myOutcall',
                          ring_time=10,
                          internal_caller_id=True,
                          context='to-extern',
                          preprocess_subroutine='MySubroutine',
                          description='outcall description',
                          enabled=False,
                          patterns=[DialPattern(external_prefix='514',
                                                prefix='1',
                                                pattern='**.',
                                                strip_digits=3,
                                                caller_id='OUTCALL'),
                                    DialPattern(external_prefix='418',
                                                prefix='2',
                                                pattern='99999',
                                                strip_digits=2,
                                                caller_id='SECOND')])

        created_outcall = outcall_dao.create(outcall)

        row = self.session.query(Outcall).first()

        assert_that(created_outcall, equal_to(row))
        assert_that(created_outcall, has_properties(id=is_not(none()),
                                                    ring_time=10,
                                                    internal_caller_id=True,
                                                    preprocess_subroutine='MySubroutine',
                                                    description='outcall description',
                                                    enabled=False,
                                                    patterns=has_items(has_properties(external_prefix='514',
                                                                                      prefix='1',
                                                                                      pattern='**.',
                                                                                      strip_digits=3,
                                                                                      caller_id='OUTCALL'),
                                                                       has_properties(external_prefix='418',
                                                                                      prefix='2',
                                                                                      pattern='99999',
                                                                                      strip_digits=2,
                                                                                      caller_id='SECOND'))))

    def test_create_then_extension_entries_created(self):
        outcall = Outcall(name='myoutcall', context='from-extern',
                          patterns=[DialPattern(pattern='**.'),
                                    DialPattern(pattern='99999')])

        outcall_dao.create(outcall)

        extensions = self.session.query(Extension).all()
        assert_that(extensions, has_items(has_properties(exten='**.',
                                                         context='from-extern'),
                                          has_properties(exten='99999',
                                                         context='from-extern')))


class TestEdit(DAOTestCase):

    def test_edit_all_fields(self):
        outcall = outcall_dao.create(Outcall(name='MyOutcall',
                                             ring_time=10,
                                             internal_caller_id=True,
                                             context='to-extern',
                                             preprocess_subroutine='MySubroutine',
                                             description='outcall description',
                                             enabled=False,
                                             patterns=[DialPattern(external_prefix='514',
                                                                   prefix='1',
                                                                   pattern='**.',
                                                                   strip_digits=3,
                                                                   caller_id='OUTCALL'),
                                                       DialPattern(external_prefix='418',
                                                                   prefix='2',
                                                                   pattern='99999',
                                                                   strip_digits=2,
                                                                   caller_id='SECOND')]))

        outcall = outcall_dao.get(outcall.id)
        outcall.name = 'other_name'
        outcall.ring_time = 5
        outcall.internal_caller_id = False
        outcall.context = 'default'
        outcall.preprocess_subroutine = 'other_routine'
        outcall.description = 'other description'
        outcall.enabled = True
        outcall.patterns = [DialPattern(external_prefix='555',
                                        prefix='9',
                                        pattern='XX',
                                        strip_digits=1,
                                        caller_id='OTHER')]
        outcall_dao.edit(outcall)

        row = self.session.query(Outcall).first()

        assert_that(outcall, equal_to(row))
        assert_that(outcall, has_properties(id=is_not(none()),
                                            name='other_name',
                                            ring_time=5,
                                            internal_caller_id=False,
                                            context='default',
                                            preprocess_subroutine='other_routine',
                                            description='other description',
                                            enabled=True,
                                            patterns=has_items(has_properties(external_prefix='555',
                                                                              prefix='9',
                                                                              pattern='XX',
                                                                              strip_digits=1,
                                                                              caller_id='OTHER'))))

    def test_edit_set_fields_to_null(self):
        outcall = outcall_dao.create(Outcall(name='MyOutcall',
                                             context='from-extern',
                                             ring_time=10,
                                             preprocess_subroutine='MySubroutine',
                                             description='outcall description',
                                             patterns=[]))

        outcall = outcall_dao.get(outcall.id)
        outcall.preprocess_subroutine = None
        outcall.description = None
        outcall.ring_time = None
        outcall.patterns = [DialPattern(external_prefix=None,
                                        prefix=None,
                                        pattern='XX',
                                        caller_id=None)]

        outcall_dao.edit(outcall)

        row = self.session.query(Outcall).first()
        assert_that(outcall, equal_to(row))
        assert_that(row, has_properties(preprocess_subroutine=none(),
                                        description=none(),
                                        ring_time=none(),
                                        patterns=has_items(has_properties(external_prefix=none(),
                                                                          prefix=none(),
                                                                          caller_id=none()))))


class TestDelete(DAOTestCase):

    def test_delete(self):
        outcall = self.add_outcall()

        outcall_dao.delete(outcall)

        row = self.session.query(Outcall).first()
        assert_that(row, none())

    def test_when_deleting_then_dialpattern_are_deleted(self):
        outcall = self.add_outcall(patterns=[DialPattern(pattern='XX')])

        outcall_dao.delete(outcall)

        dialpattern = self.session.query(DialPattern).first()
        assert_that(dialpattern, none())

    def test_when_deleting_then_call_permission_are_dissociated(self):
        outcall = self.add_outcall()
        self.add_call_permission()
        self.add_outcall_call_permission(typeval=str(outcall.id))

        outcall_dao.delete(outcall)

        outcall_call_permission = self.session.query(RightCallMember).first()
        assert_that(outcall_call_permission, none())

    def test_when_deleting_then_schedule_are_dissociated(self):
        outcall = self.add_outcall()
        schedule = self.add_schedule()
        self.add_outcall_schedule(schedule_id=schedule.id, pathid=outcall.id)

        outcall_dao.delete(outcall)

        outcall_schedule = self.session.query(SchedulePath).first()
        assert_that(outcall_schedule, none())

    def test_when_deleting_then_extension_are_deleted(self):
        outcall = self.add_outcall(patterns=[DialPattern(pattern='XX')])

        outcall_dao.delete(outcall)

        extension = self.session.query(Extension).first()
        assert_that(extension, none())


class TestGroupExist(DAOTestCase):

    def test_given_no_outcall_then_returns_false(self):
        result = outcall_dao.exists(1)

        assert_that(result, equal_to(False))

    def test_given_outcall_exists_then_return_true(self):
        outcall_row = self.add_outcall()

        result = outcall_dao.exists(outcall_row.id)

        assert_that(result, equal_to(True))
