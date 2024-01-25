# Copyright 2018-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains_exactly,
    equal_to,
    has_items,
    has_properties,
    has_property,
    none,
    not_none,
)

from sqlalchemy.inspection import inspect
from xivo_dao.alchemy.accessfeatures import AccessFeatures
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.helpers.exception import NotFoundError, InputError
from xivo_dao.tests.test_dao import DAOTestCase

from .. import dao as access_feature_dao


class TestFind(DAOTestCase):
    def test_find_no_access_feature(self):
        result = access_feature_dao.find(42)

        assert_that(result, none())

    def test_find(self):
        access_feature_row = self.add_accessfeatures(host='1.2.3.0/24')

        access_feature = access_feature_dao.find(access_feature_row.id)

        assert_that(access_feature, equal_to(access_feature_row))


class TestGet(DAOTestCase):
    def test_get_no_access_feature(self):
        self.assertRaises(NotFoundError, access_feature_dao.get, 42)

    def test_get(self):
        access_feature_row = self.add_accessfeatures(host='1.2.3.0/24')

        access_feature = access_feature_dao.get(access_feature_row.id)

        assert_that(access_feature.id, equal_to(access_feature_row.id))


class TestFindBy(DAOTestCase):
    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, access_feature_dao.find_by, invalid=42)

    def test_find_by_host(self):
        access_feature_row = self.add_accessfeatures(host='1.2.3.0/24')

        access_feature = access_feature_dao.find_by(host='1.2.3.0/24')

        assert_that(access_feature, equal_to(access_feature_row))
        assert_that(access_feature.host, equal_to('1.2.3.0/24'))

    def test_given_access_feature_does_not_exist_then_returns_null(self):
        access_feature = access_feature_dao.find_by(host='42')

        assert_that(access_feature, none())


class TestGetBy(DAOTestCase):
    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, access_feature_dao.get_by, invalid=42)

    def test_get_by_host(self):
        access_feature_row = self.add_accessfeatures(host='1.2.3.0/24')

        access_feature = access_feature_dao.get_by(host='1.2.3.0/24')

        assert_that(access_feature, equal_to(access_feature_row))
        assert_that(access_feature.host, equal_to('1.2.3.0/24'))

    def test_given_access_feature_does_not_exist_then_raises_error(self):
        self.assertRaises(NotFoundError, access_feature_dao.get_by, host='42')


class TestFindAllBy(DAOTestCase):
    def test_find_all_by_no_access_features(self):
        result = access_feature_dao.find_all_by(feature='noresult')

        assert_that(result, contains_exactly())

    def test_find_all_by(self):
        access_feature1 = self.add_accessfeatures(host='1.2.3.0/24', enabled=False)
        access_feature2 = self.add_accessfeatures(host='1.2.4.0/24', enabled=False)

        access_features = access_feature_dao.find_all_by(enabled=False)

        assert_that(
            access_features,
            has_items(
                has_property('id', access_feature1.id),
                has_property('id', access_feature2.id),
            ),
        )


class TestSearch(DAOTestCase):
    def assert_search_returns_result(self, search_result, **parameters):
        result = access_feature_dao.search(**parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestSearch):
    def test_given_no_access_features_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_one_access_feature_then_returns_one_result(self):
        access_feature = self.add_accessfeatures(host='1.2.3.0/24')
        expected = SearchResult(1, [access_feature])

        self.assert_search_returns_result(expected)


class TestSearchGivenMultipleAccessFeatures(TestSearch):
    def setUp(self):
        super(TestSearch, self).setUp()
        self.access_feature1 = self.add_accessfeatures(host='1.2.3.0/24', enabled=False)
        self.access_feature2 = self.add_accessfeatures(host='1.2.4.0/24')
        self.access_feature3 = self.add_accessfeatures(host='1.2.5.0/24')
        self.access_feature4 = self.add_accessfeatures(host='1.2.6.0/25')

    def test_when_searching_then_returns_one_result(self):
        expected = SearchResult(1, [self.access_feature2])

        self.assert_search_returns_result(expected, search='1.2.4')

    def test_when_searching_with_an_extra_argument(self):
        expected_host = SearchResult(1, [self.access_feature1])
        self.assert_search_returns_result(expected_host, search='1.2', enabled=False)

        expected_host = SearchResult(1, [self.access_feature2])
        self.assert_search_returns_result(expected_host, search='1.2.4', enabled=True)

        expected_all_hosts = SearchResult(
            3, [self.access_feature2, self.access_feature3, self.access_feature4]
        )
        self.assert_search_returns_result(
            expected_all_hosts, enabled=True, order='host'
        )

    def test_when_sorting_then_returns_result_in_ascending_order(self):
        expected = SearchResult(
            4,
            [
                self.access_feature1,
                self.access_feature2,
                self.access_feature3,
                self.access_feature4,
            ],
        )

        self.assert_search_returns_result(expected, order='host')

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(
        self,
    ):
        expected = SearchResult(
            4,
            [
                self.access_feature4,
                self.access_feature3,
                self.access_feature2,
                self.access_feature1,
            ],
        )

        self.assert_search_returns_result(expected, order='host', direction='desc')

    def test_when_limiting_then_returns_right_name_of_items(self):
        expected = SearchResult(4, [self.access_feature1])

        self.assert_search_returns_result(expected, limit=1)

    def test_when_offset_then_returns_right_name_of_items(self):
        expected = SearchResult(
            4, [self.access_feature2, self.access_feature3, self.access_feature4]
        )

        self.assert_search_returns_result(expected, offset=1)

    def test_when_doing_a_paginated_search_then_returns_a_paginated_result(self):
        expected = SearchResult(3, [self.access_feature2])

        self.assert_search_returns_result(
            expected,
            search='24',
            order='host',
            direction='desc',
            offset=1,
            limit=1,
        )


class TestCreate(DAOTestCase):
    def test_create_minimal_fields(self):
        access_feature = AccessFeatures(host='1.2.3.4/24')
        access_feature = access_feature_dao.create(access_feature)

        assert_that(inspect(access_feature).persistent)
        assert_that(
            access_feature,
            has_properties(
                id=not_none(),
                host='1.2.3.4/24',
                feature='phonebook',
                enabled=True,
            ),
        )

    def test_create_with_all_fields(self):
        access_feature = AccessFeatures(
            host='1.2.3.4/24',
            feature='phonebook',
            enabled=True,
        )
        access_feature = access_feature_dao.create(access_feature)

        assert_that(inspect(access_feature).persistent)
        assert_that(
            access_feature,
            has_properties(
                host='1.2.3.4/24',
                feature='phonebook',
                enabled=True,
            ),
        )


class TestEdit(DAOTestCase):
    def test_edit_all_fields(self):
        access_feature = self.add_accessfeatures(
            host='1.2.3.0/24',
            enabled=True,
        )

        self.session.expire_all()
        access_feature.host = '1.2.4.0/24'
        access_feature.enabled = False

        access_feature_dao.edit(access_feature)

        self.session.expire_all()
        assert_that(
            access_feature,
            has_properties(
                host='1.2.4.0/24',
                enabled=False,
            ),
        )


class TestDelete(DAOTestCase):
    def test_delete(self):
        access_feature = self.add_accessfeatures(host='1.2.3.0/24')

        access_feature_dao.delete(access_feature)

        assert_that(inspect(access_feature).deleted)
