# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from hamcrest import (
    assert_that,
    contains,
    equal_to,
    empty,
    has_items,
    has_key,
    has_properties,
    has_property,
    is_not,
    none,
)

from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.callfilter import Callfilter as CallFilter
from xivo_dao.alchemy.callfiltermember import Callfiltermember as CallFilterMember
from xivo_dao.helpers.exception import NotFoundError, InputError
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.tests.test_dao import DAOTestCase

from .. import dao as call_filter_dao


class TestMemberExist(DAOTestCase):

    def test_not_exists(self):
        result = call_filter_dao.member_exists(1)

        assert_that(result, equal_to(False))

    def test_exists(self):
        member = self.add_call_filter_member()

        result = call_filter_dao.member_exists(member.id)

        assert_that(result, equal_to(True))


class TestFind(DAOTestCase):

    def test_find_no_call_filter(self):
        result = call_filter_dao.find(42)

        assert_that(result, none())

    def test_find(self):
        call_filter = self.add_call_filter()

        result = call_filter_dao.find(call_filter.id)

        assert_that(result, equal_to(call_filter))


class TestGet(DAOTestCase):

    def test_get_no_call_filter(self):
        self.assertRaises(NotFoundError, call_filter_dao.get, 42)

    def test_get(self):
        call_filter = self.add_call_filter()

        result = call_filter_dao.get(call_filter.id)

        assert_that(result, equal_to(call_filter))


class TestFindBy(DAOTestCase):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, call_filter_dao.find_by, invalid=42)

    def test_find_by_name(self):
        call_filter_row = self.add_call_filter(name='Jôhn')

        call_filter = call_filter_dao.find_by(name='Jôhn')

        assert_that(call_filter.id, equal_to(call_filter_row.id))
        assert_that(call_filter.name, equal_to('Jôhn'))

    def test_given_call_filter_does_not_exist_then_returns_null(self):
        call_filter = call_filter_dao.find_by(name='42')

        assert_that(call_filter, none())


class TestGetBy(DAOTestCase):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, call_filter_dao.get_by, invalid=42)

    def test_get_by_name(self):
        call_filter_row = self.add_call_filter(name='Jôhn')

        call_filter = call_filter_dao.get_by(name='Jôhn')

        assert_that(call_filter.id, equal_to(call_filter_row.id))
        assert_that(call_filter.name, equal_to('Jôhn'))

    def test_given_call_filter_does_not_exist_then_raises_error(self):
        self.assertRaises(NotFoundError, call_filter_dao.get_by, name='42')


class TestFindAllBy(DAOTestCase):

    def test_find_all_by_no_call_filters(self):
        result = call_filter_dao.find_all_by(name='toto')

        assert_that(result, contains())

    def test_find_all_by_renamed_column(self):
        call_filter1 = self.add_call_filter(name='bob', enabled=True)
        call_filter2 = self.add_call_filter(name='alice', enabled=True)

        call_filters = call_filter_dao.find_all_by(enabled=True)

        assert_that(call_filters, has_items(has_property('id', call_filter1.id),
                                            has_property('id', call_filter2.id)))

    def test_find_all_by_native_column(self):
        call_filter1 = self.add_call_filter(name='bob', description='description')
        call_filter2 = self.add_call_filter(name='alice', description='description')

        call_filters = call_filter_dao.find_all_by(description='description')

        assert_that(call_filters, has_items(has_property('id', call_filter1.id),
                                            has_property('id', call_filter2.id)))


class TestSearch(DAOTestCase):

    def assert_search_returns_result(self, search_result, **parameters):
        result = call_filter_dao.search(**parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestSearch):

    def test_given_no_call_filters_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_one_commented_call_filter_then_returns_one_result(self):
        call_filter = self.add_call_filter(name='bob')
        expected = SearchResult(1, [call_filter])

        self.assert_search_returns_result(expected)


class TestSearchGivenMultipleCallFilters(TestSearch):

    def setUp(self):
        super(TestSearch, self).setUp()
        self.call_filter1 = self.add_call_filter(
            name='Ashton',
            description='resto',
            strategy='all-recipients-then-linear-surrogates',
        )
        self.call_filter2 = self.add_call_filter(name='Beaugarton', description='bar')
        self.call_filter3 = self.add_call_filter(name='Casa', description='resto')
        self.call_filter4 = self.add_call_filter(name='Dunkin', description='resto')

    def test_when_searching_then_returns_one_result(self):
        expected = SearchResult(1, [self.call_filter2])

        self.assert_search_returns_result(expected, search='eau')

    def test_when_searching_with_an_extra_argument(self):
        expected_resto = SearchResult(1, [self.call_filter1])
        self.assert_search_returns_result(expected_resto, search='ton', description='resto')

        expected_bar = SearchResult(1, [self.call_filter2])
        self.assert_search_returns_result(expected_bar, search='ton', description='bar')

        expected_all_resto = SearchResult(3, [self.call_filter1, self.call_filter3, self.call_filter4])
        self.assert_search_returns_result(expected_all_resto, description='resto', order='name')

    def test_when_sorting_then_returns_result_in_ascending_order(self):
        expected = SearchResult(4, [self.call_filter1,
                                    self.call_filter2,
                                    self.call_filter3,
                                    self.call_filter4])

        self.assert_search_returns_result(expected, order='name')

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(self):
        expected = SearchResult(4, [self.call_filter4,
                                    self.call_filter3,
                                    self.call_filter2,
                                    self.call_filter1])

        self.assert_search_returns_result(expected, order='name', direction='desc')

    def test_when_limiting_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.call_filter1])

        self.assert_search_returns_result(expected, limit=1)

    def test_when_skipping_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.call_filter2, self.call_filter3, self.call_filter4])

        self.assert_search_returns_result(expected, skip=1)

    def test_when_doing_a_paginated_search_then_returns_a_paginated_result(self):
        expected = SearchResult(3, [self.call_filter2])

        self.assert_search_returns_result(expected,
                                          search='a',
                                          order='name',
                                          direction='desc',
                                          skip=1,
                                          limit=1)


class TestCreate(DAOTestCase):

    def setUp(self):
        super(TestCreate, self).setUp()
        self.add_tenant()
        self.entity = self.add_entity()

    def test_create_minimal_fields(self):
        call_filter = CallFilter(name='name')

        result = call_filter_dao.create(call_filter)

        row = self.session.query(CallFilter).first()
        assert_that(result, equal_to(row))
        assert_that(result, has_properties(
            name='name',
            strategy=none(),
            callfrom=none(),
            surrogates_timeout=none(),
            enabled=True,
            description=none(),
        ))

    def test_create_with_all_fields(self):
        call_filter = CallFilter(
            name='name',
            strategy='all-recipients-then-linear-surrogates',
            callfrom='all',
            surrogates_timeout=10,
            enabled=False,
            description='description',
        )

        result = call_filter_dao.create(call_filter)

        row = self.session.query(CallFilter).first()
        assert_that(result, equal_to(row))
        assert_that(result, has_properties(
            name='name',
            strategy='all-recipients-then-linear-surrogates',
            callfrom='all',
            surrogates_timeout=10,
            enabled=False,
            description='description',
        ))

    def test_create_fill_default_values(self):
        call_filter = CallFilter(name='name')

        result = call_filter_dao.create(call_filter)

        assert_that(result, has_properties(
            entity_id=self.entity.id,
            type='bosssecretary',
        ))


class TestEdit(DAOTestCase):

    def test_edit_all_fields(self):
        call_filter = self.add_call_filter(
            name='name',
            strategy='all-recipients-then-linear-surrogates',
            callfrom='all',
            surrogates_timeout=10,
            enabled=True,
            description='description',
        )

        call_filter = call_filter_dao.get(call_filter.id)
        call_filter.name = 'other_name'
        call_filter.strategy = 'all-recipients-then-all-surrogates'
        call_filter.callfrom = 'internal'
        call_filter.surrogates_timeout = 20
        call_filter.enabled = False
        call_filter.description = 'other_description'

        call_filter_dao.edit(call_filter)

        row = self.session.query(CallFilter).first()
        assert_that(row, has_properties(
            name='other_name',
            strategy='all-recipients-then-all-surrogates',
            callfrom='internal',
            surrogates_timeout=20,
            enabled=False,
            description='other_description',
        ))


class TestDelete(DAOTestCase):

    def test_delete(self):
        call_filter = self.add_call_filter()

        call_filter_dao.delete(call_filter)

        row = self.session.query(CallFilter).first()
        assert_that(row, none())


class TestAssociateTargets(DAOTestCase):

    def test_associate(self):
        call_filter = self.add_call_filter()
        recipient = self.add_call_filter_member(bstype='boss')

        call_filter_dao.associate_recipients(call_filter, [recipient])

        self.session.expire_all()
        assert_that(call_filter.recipients, contains(recipient))

    def test_associate_multiple(self):
        call_filter = self.add_call_filter()
        recipient1 = self.add_call_filter_member(bstype='boss')
        recipient2 = self.add_call_filter_member(bstype='boss')

        call_filter_dao.associate_recipients(call_filter, [recipient1, recipient2])

        self.session.expire_all()
        assert_that(call_filter.recipients, contains(recipient1, recipient2))

    def test_dissociate(self):
        call_filter = self.add_call_filter()
        recipient = self.add_call_filter_member(bstype='boss')
        call_filter_dao.associate_recipients(call_filter, [recipient])

        call_filter_dao.associate_recipients(call_filter, [])

        self.session.expire_all()
        assert_that(call_filter.recipients, empty())

        row = self.session.query(CallFilterMember).first()
        assert_that(row, none())


class TestAssociateInterceptors(DAOTestCase):

    def test_associate(self):
        call_filter = self.add_call_filter()
        surrogate = self.add_call_filter_member(bstype='secretary')

        call_filter_dao.associate_surrogates(call_filter, [surrogate])

        self.session.expire_all()
        assert_that(call_filter.surrogates, contains(surrogate))

    def test_associate_multiple(self):
        call_filter = self.add_call_filter()
        surrogate1 = self.add_call_filter_member(bstype='secretary')
        surrogate2 = self.add_call_filter_member(bstype='secretary')

        call_filter_dao.associate_surrogates(call_filter, [surrogate1, surrogate2])

        self.session.expire_all()
        assert_that(call_filter.surrogates, contains(surrogate1, surrogate2))

    def test_dissociate(self):
        call_filter = self.add_call_filter()
        surrogate = self.add_call_filter_member(bstype='secretary')
        call_filter_dao.associate_surrogates(call_filter, [surrogate])

        call_filter_dao.associate_surrogates(call_filter, [])

        self.session.expire_all()
        assert_that(call_filter.surrogates, empty())

        row = self.session.query(CallFilterMember).first()
        assert_that(row, none())


class TestUpdateFallbacks(DAOTestCase):

    def test_update(self):
        call_filter = self.add_call_filter()
        dialaction = Dialaction(action='none')

        call_filter_dao.update_fallbacks(call_filter, {'key': dialaction})

        self.session.expire_all()
        assert_that(call_filter.fallbacks['key'], has_properties(action='none'))

    def test_update_to_none(self):
        call_filter = self.add_call_filter()

        call_filter_dao.update_fallbacks(call_filter, {'key': None})

        self.session.expire_all()
        assert_that(call_filter.fallbacks, empty())

    def test_update_existing_key(self):
        call_filter = self.add_call_filter()

        dialaction1 = Dialaction(action='none')
        call_filter_dao.update_fallbacks(call_filter, {'key': dialaction1})
        self.session.expire_all()

        dialaction2 = Dialaction(action='user', actionarg1='1')
        call_filter_dao.update_fallbacks(call_filter, {'key': dialaction2})
        self.session.expire_all()

        self.session.expire_all()
        assert_that(call_filter.fallbacks['key'], has_properties(action='user', actionarg1='1'))

    def test_update_delete_undefined_key(self):
        call_filter = self.add_call_filter()

        dialaction1 = Dialaction(action='none')
        call_filter_dao.update_fallbacks(call_filter, {'old_key': dialaction1})
        self.session.expire_all()

        dialaction2 = Dialaction(action='user', actionarg1='1')
        call_filter_dao.update_fallbacks(call_filter, {'key': dialaction2})
        self.session.expire_all()

        self.session.expire_all()
        assert_that(call_filter.fallbacks, is_not(has_key('old_key')))