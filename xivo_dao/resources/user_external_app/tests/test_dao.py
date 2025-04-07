# Copyright 2020-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


from hamcrest import (
    assert_that,
    contains_exactly,
    equal_to,
    has_items,
    has_properties,
    has_property,
    none,
)
from sqlalchemy.inspection import inspect

from xivo_dao.alchemy.user_external_app import UserExternalApp
from xivo_dao.helpers.exception import InputError, NotFoundError
from xivo_dao.resources.user_external_app import dao as user_external_app_dao
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.tests.test_dao import DAOTestCase


class TestFind(DAOTestCase):
    def test_find_no_external_app(self):
        user = self.add_user()
        result = user_external_app_dao.find(user.uuid, '42')

        assert_that(result, none())

    def test_find(self):
        user = self.add_user()
        user_external_app = self.add_user_external_app(user_uuid=user.uuid)

        result = user_external_app_dao.find(user.uuid, user_external_app.name)

        assert_that(result, equal_to(user_external_app))


class TestGet(DAOTestCase):
    def test_get_no_user_external_app(self):
        user = self.add_user()
        self.assertRaises(NotFoundError, user_external_app_dao.get, user.uuid, '42')

    def test_get(self):
        user = self.add_user()
        user_external_app = self.add_user_external_app(user_uuid=user.uuid)

        result = user_external_app_dao.get(user.uuid, user_external_app.name)

        assert_that(result.name, equal_to(user_external_app.name))


class TestFindBy(DAOTestCase):
    def test_given_column_does_not_exist_then_error_raised(self):
        user = self.add_user()
        self.assertRaises(
            InputError, user_external_app_dao.find_by, user.uuid, invalid=42
        )

    def test_find_by_name(self):
        user = self.add_user()
        user_external_app = self.add_user_external_app(user_uuid=user.uuid, name='123')

        result = user_external_app_dao.find_by(user.uuid, name='123')

        assert_that(result, equal_to(user_external_app))
        assert_that(result.name, equal_to('123'))

    def test_given_external_app_does_not_exist_then_returns_null(self):
        user = self.add_user()
        result = user_external_app_dao.find_by(user.uuid, name='42')

        assert_that(result, none())


class TestGetBy(DAOTestCase):
    def test_given_column_does_not_exist_then_error_raised(self):
        user = self.add_user()
        self.assertRaises(
            InputError, user_external_app_dao.get_by, user.uuid, invalid=42
        )

    def test_get_by_name(self):
        user = self.add_user()
        user_external_app = self.add_user_external_app(user_uuid=user.uuid, name='123')

        result = user_external_app_dao.get_by(user.uuid, name='123')

        assert_that(result, equal_to(user_external_app))
        assert_that(result.name, equal_to('123'))

    def test_given_external_app_does_not_exist_then_raises_error(self):
        user = self.add_user()
        self.assertRaises(
            NotFoundError, user_external_app_dao.get_by, user.uuid, name='42'
        )


class TestFindAllBy(DAOTestCase):
    def test_find_all_by_no_external_apps(self):
        user = self.add_user()
        result = user_external_app_dao.find_all_by(user.uuid, name='123')

        assert_that(result, contains_exactly())

    def test_find_all_by_native_column(self):
        user = self.add_user()
        user_external_app1 = self.add_user_external_app(
            name='app1', user_uuid=user.uuid
        )
        self.add_user_external_app(name='app2', user_uuid=user.uuid)

        result = user_external_app_dao.find_all_by(user.uuid, name='app1')

        assert_that(
            result,
            has_items(
                has_property('name', user_external_app1.name),
            ),
        )


class TestSearch(DAOTestCase):
    def setUp(self):
        super().setUp()
        self.user = self.add_user()

    def assert_search_returns_result(self, search_result, **parameters):
        result = user_external_app_dao.search(self.user.uuid, **parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestSearch):
    def test_given_no_external_apps_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_one_external_app_then_returns_one_result(self):
        external_app = self.add_user_external_app(user_uuid=self.user.uuid)
        expected = SearchResult(1, [external_app])

        self.assert_search_returns_result(expected)


class TestSearchGivenMultipleUserExternalApps(TestSearch):
    def setUp(self):
        super().setUp()
        self.app1 = self.add_user_external_app(user_uuid=self.user.uuid, name='Ashton')
        self.app2 = self.add_user_external_app(
            user_uuid=self.user.uuid, name='Beaugarton'
        )
        self.app3 = self.add_user_external_app(user_uuid=self.user.uuid, name='Casa')
        self.app4 = self.add_user_external_app(user_uuid=self.user.uuid, name='Dunkin')

    def test_when_searching_then_returns_one_result(self):
        expected = SearchResult(1, [self.app2])

        self.assert_search_returns_result(expected, search='eau')

    def test_when_searching_with_an_extra_argument(self):
        expected_resto = SearchResult(1, [self.app1])
        self.assert_search_returns_result(expected_resto, search='ton', name='Ashton')

    def test_when_searching_with_a_custom_extra_argument(self):
        expected_allow = SearchResult(1, [self.app2])
        self.assert_search_returns_result(expected_allow, name='Beaugarton')

    def test_when_sorting_then_returns_result_in_ascending_order(self):
        expected = SearchResult(4, [self.app1, self.app2, self.app3, self.app4])

        self.assert_search_returns_result(expected, order='name')

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(
        self,
    ):
        expected = SearchResult(4, [self.app4, self.app3, self.app2, self.app1])

        self.assert_search_returns_result(expected, order='name', direction='desc')

    def test_when_limiting_then_returns_right_name_of_items(self):
        expected = SearchResult(4, [self.app1])

        self.assert_search_returns_result(expected, limit=1)

    def test_when_offset_then_returns_right_name_of_items(self):
        expected = SearchResult(4, [self.app2, self.app3, self.app4])

        self.assert_search_returns_result(expected, offset=1)

    def test_when_doing_a_paginated_search_then_returns_a_paginated_result(self):
        expected = SearchResult(3, [self.app2])

        self.assert_search_returns_result(
            expected,
            search='a',
            order='name',
            direction='desc',
            offset=1,
            limit=1,
        )


class TestCreate(DAOTestCase):
    def test_create_minimal_fields(self):
        user = self.add_user()
        external_app_model = UserExternalApp(user_uuid=user.uuid, name='required')
        external_app = user_external_app_dao.create(external_app_model)

        self.session.expire_all()
        assert_that(inspect(external_app).persistent)
        assert_that(
            external_app,
            has_properties(
                name='required',
                user_uuid=user.uuid,
                configuration=None,
            ),
        )

    def test_create_with_all_fields(self):
        user = self.add_user()
        external_app_model = UserExternalApp(
            user_uuid=user.uuid,
            name='user_external_app',
            label='External App',
            configuration={'key': {'subkey': 'value'}},
        )
        external_app = user_external_app_dao.create(external_app_model)

        self.session.expire_all()
        assert_that(inspect(external_app).persistent)
        assert_that(
            external_app,
            has_properties(
                user_uuid=user.uuid,
                name='user_external_app',
                label='External App',
                configuration={'key': {'subkey': 'value'}},
            ),
        )


class TestEdit(DAOTestCase):
    def test_edit_all_fields(self):
        user = self.add_user()
        external_app = self.add_user_external_app(
            user_uuid=user.uuid,
            name='user_external_app',
            label='External App',
            configuration={'original': 'data'},
        )

        self.session.expire_all()
        external_app.name = 'other_user_external_app'
        external_app.configuration = {'edited': 'data'}
        external_app.label = ('Other External App',)

        user_external_app_dao.edit(external_app)

        self.session.expire_all()
        assert_that(
            external_app,
            has_properties(
                user_uuid=user.uuid,
                name='other_user_external_app',
                label='Other External App',
                configuration={'edited': 'data'},
            ),
        )


class TestDelete(DAOTestCase):
    def test_delete(self):
        user = self.add_user()
        external_app = self.add_user_external_app(user_uuid=user.uuid)

        user_external_app_dao.delete(external_app)

        assert_that(inspect(external_app).deleted)
