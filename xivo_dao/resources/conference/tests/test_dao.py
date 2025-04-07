# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


from hamcrest import (
    all_of,
    assert_that,
    contains_exactly,
    equal_to,
    has_items,
    has_properties,
    has_property,
    is_not,
    none,
    not_,
)

from xivo_dao.alchemy.conference import Conference
from xivo_dao.alchemy.extension import Extension
from xivo_dao.helpers.exception import InputError, NotFoundError
from xivo_dao.resources.conference import dao as conference_dao
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.tests.test_dao import DAOTestCase


class TestFind(DAOTestCase):
    def test_find_no_conference(self):
        result = conference_dao.find(42)

        assert_that(result, none())

    def test_find(self):
        conference_row = self.add_conference()

        conference = conference_dao.find(conference_row.id)

        assert_that(conference, equal_to(conference_row))

    def test_find_multi_tenant(self):
        tenant = self.add_tenant()
        conference = self.add_conference(tenant_uuid=tenant.uuid)

        result = conference_dao.find(conference.id, tenant_uuids=[tenant.uuid])
        assert_that(result, equal_to(conference))

        result = conference_dao.find(
            conference.id, tenant_uuids=[self.default_tenant.uuid]
        )
        assert_that(result, none())


class TestGet(DAOTestCase):
    def test_get_no_conference(self):
        self.assertRaises(NotFoundError, conference_dao.get, 42)

    def test_get(self):
        conference_row = self.add_conference()

        conference = conference_dao.get(conference_row.id)

        assert_that(conference.id, equal_to(conference.id))

    def test_get_multi_tenant(self):
        tenant = self.add_tenant()

        conference_row = self.add_conference(tenant_uuid=tenant.uuid)
        conference = conference_dao.get(conference_row.id, tenant_uuids=[tenant.uuid])
        assert_that(conference, equal_to(conference_row))

        conference_row = self.add_conference()
        self.assertRaises(
            NotFoundError,
            conference_dao.get,
            conference_row.id,
            tenant_uuids=[tenant.uuid],
        )


class TestFindBy(DAOTestCase):
    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, conference_dao.find_by, invalid=42)

    def test_find_by_name(self):
        conference_row = self.add_conference(name='Jôhn')

        conference = conference_dao.find_by(name='Jôhn')

        assert_that(conference, equal_to(conference_row))
        assert_that(conference.name, equal_to('Jôhn'))

    def test_given_conference_does_not_exist_then_returns_null(self):
        conference = conference_dao.find_by(name='42')

        assert_that(conference, none())

    def test_find_by_multi_tenant(self):
        tenant = self.add_tenant()

        conference_row = self.add_conference()
        conference = conference_dao.find_by(
            name=conference_row.name, tenant_uuids=[tenant.uuid]
        )
        assert_that(conference, none())

        conference_row = self.add_conference(tenant_uuid=tenant.uuid)
        conference = conference_dao.find_by(
            name=conference_row.name, tenant_uuids=[tenant.uuid]
        )
        assert_that(conference, equal_to(conference_row))


class TestGetBy(DAOTestCase):
    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, conference_dao.get_by, invalid=42)

    def test_get_by_name(self):
        conference_row = self.add_conference(name='Jôhn')

        conference = conference_dao.get_by(name='Jôhn')

        assert_that(conference, equal_to(conference_row))
        assert_that(conference.name, equal_to('Jôhn'))

    def test_given_conference_does_not_exist_then_raises_error(self):
        self.assertRaises(NotFoundError, conference_dao.get_by, name='42')

    def test_get_by_multi_tenant(self):
        tenant = self.add_tenant()

        conference_row = self.add_conference()
        self.assertRaises(
            NotFoundError,
            conference_dao.get_by,
            id=conference_row.id,
            tenant_uuids=[tenant.uuid],
        )

        conference_row = self.add_conference(tenant_uuid=tenant.uuid)
        conference = conference_dao.get_by(
            id=conference_row.id, tenant_uuids=[tenant.uuid]
        )
        assert_that(conference, equal_to(conference_row))


class TestFindAllBy(DAOTestCase):
    def test_find_all_by_no_conferences(self):
        result = conference_dao.find_all_by(name='toto')

        assert_that(result, contains_exactly())

    def test_find_all_by_renamed_column(self):
        pass

    def test_find_all_by_native_column(self):
        conference1 = self.add_conference(
            name='bob', preprocess_subroutine='subroutine'
        )
        conference2 = self.add_conference(
            name='alice', preprocess_subroutine='subroutine'
        )

        conferences = conference_dao.find_all_by(preprocess_subroutine='subroutine')

        assert_that(
            conferences,
            has_items(
                has_property('id', conference1.id),
                has_property('id', conference2.id),
            ),
        )

    def test_find_all_multi_tenant(self):
        tenant = self.add_tenant()
        kwargs = {'preprocess_subroutine': 'subroutine'}

        conference1 = self.add_conference(tenant_uuid=tenant.uuid, **kwargs)
        conference2 = self.add_conference(**kwargs)

        tenants = [tenant.uuid, self.default_tenant.uuid]
        conferences = conference_dao.find_all_by(tenant_uuids=tenants, **kwargs)
        assert_that(conferences, has_items(conference1, conference2))

        tenants = [tenant.uuid]
        conferences = conference_dao.find_all_by(tenant_uuids=tenants, **kwargs)
        assert_that(
            conferences, all_of(has_items(conference1), not_(has_items(conference2)))
        )


class TestSearch(DAOTestCase):
    def assert_search_returns_result(self, search_result, **parameters):
        result = conference_dao.search(**parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestSearch):
    def test_given_no_conferences_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_one_conference_then_returns_one_result(self):
        conference = self.add_conference(name='bob')
        expected = SearchResult(1, [conference])

        self.assert_search_returns_result(expected)

    def test_search_multi_tenant(self):
        tenant = self.add_tenant()

        conference1 = self.add_conference()
        conference2 = self.add_conference(tenant_uuid=tenant.uuid)

        expected = SearchResult(2, [conference1, conference2])
        tenants = [tenant.uuid, self.default_tenant.uuid]
        self.assert_search_returns_result(expected, tenant_uuids=tenants)

        expected = SearchResult(1, [conference2])
        tenants = [tenant.uuid]
        self.assert_search_returns_result(expected, tenant_uuids=tenants)


class TestSearchGivenMultipleConferences(TestSearch):
    def setUp(self):
        super(TestSearch, self).setUp()
        self.conference1 = self.add_conference(
            name='Ashton', preprocess_subroutine='resto'
        )
        self.conference2 = self.add_conference(
            name='Beaugarton', preprocess_subroutine='bar'
        )
        self.conference3 = self.add_conference(
            name='Casa', preprocess_subroutine='resto'
        )
        self.conference4 = self.add_conference(
            name='Dunkin', preprocess_subroutine='resto'
        )

    def test_when_searching_then_returns_one_result(self):
        expected = SearchResult(1, [self.conference2])

        self.assert_search_returns_result(expected, search='eau')

    def test_when_searching_with_an_extra_argument(self):
        expected_resto = SearchResult(1, [self.conference1])
        self.assert_search_returns_result(
            expected_resto, search='ton', preprocess_subroutine='resto'
        )

        expected_bar = SearchResult(1, [self.conference2])
        self.assert_search_returns_result(
            expected_bar, search='ton', preprocess_subroutine='bar'
        )

        expected_all_resto = SearchResult(
            3, [self.conference1, self.conference3, self.conference4]
        )
        self.assert_search_returns_result(
            expected_all_resto, preprocess_subroutine='resto', order='name'
        )

    def test_when_searching_with_a_custom_extra_argument(self):
        expected_allow = SearchResult(1, [self.conference2])
        self.assert_search_returns_result(expected_allow, preprocess_subroutine='bar')

        expected_all_deny = SearchResult(
            3, [self.conference1, self.conference3, self.conference4]
        )
        self.assert_search_returns_result(
            expected_all_deny, preprocess_subroutine='resto'
        )

    def test_when_sorting_then_returns_result_in_ascending_order(self):
        expected = SearchResult(
            4, [self.conference1, self.conference2, self.conference3, self.conference4]
        )

        self.assert_search_returns_result(expected, order='name')

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(
        self,
    ):
        expected = SearchResult(
            4, [self.conference4, self.conference3, self.conference2, self.conference1]
        )

        self.assert_search_returns_result(expected, order='name', direction='desc')

    def test_when_limiting_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.conference1])

        self.assert_search_returns_result(expected, limit=1)

    def test_when_offset_then_returns_right_number_of_items(self):
        expected = SearchResult(
            4, [self.conference2, self.conference3, self.conference4]
        )

        self.assert_search_returns_result(expected, offset=1)

    def test_when_doing_a_paginated_search_then_returns_a_paginated_result(self):
        expected = SearchResult(3, [self.conference2])

        self.assert_search_returns_result(
            expected, search='a', order='name', direction='desc', offset=1, limit=1
        )


class TestCreate(DAOTestCase):
    def test_create_minimal_fields(self):
        conference = Conference(tenant_uuid=self.default_tenant.uuid)
        created_conference = conference_dao.create(conference)

        row = self.session.query(Conference).first()

        assert_that(created_conference, equal_to(row))
        assert_that(
            row,
            has_properties(
                id=is_not(none()),
                tenant_uuid=self.default_tenant.uuid,
                name=None,
                preprocess_subroutine=None,
                max_users=50,
                record=False,
                pin=None,
                admin_pin=None,
                quiet_join_leave=False,
                announce_join_leave=False,
                announce_user_count=False,
                announce_only_user=True,
                music_on_hold=None,
            ),
        )

    def test_create_with_all_fields(self):
        conference = Conference(
            name='conference',
            preprocess_subroutine='subroutine',
            max_users=100,
            record=True,
            pin='1234',
            admin_pin='5678',
            quiet_join_leave=True,
            announce_join_leave=True,
            announce_user_count=True,
            announce_only_user=False,
            music_on_hold='music',
            tenant_uuid=self.default_tenant.uuid,
        )
        created_conference = conference_dao.create(conference)

        row = self.session.query(Conference).first()

        assert_that(created_conference, equal_to(row))
        assert_that(
            row,
            has_properties(
                name='conference',
                preprocess_subroutine='subroutine',
                max_users=100,
                record=True,
                pin='1234',
                admin_pin='5678',
                quiet_join_leave=True,
                announce_join_leave=True,
                announce_user_count=True,
                announce_only_user=False,
                music_on_hold='music',
                tenant_uuid=self.default_tenant.uuid,
            ),
        )


class TestEdit(DAOTestCase):
    def test_edit_all_fields(self):
        conference = conference_dao.create(
            Conference(
                name='conference',
                preprocess_subroutine='subroutine',
                max_users=100,
                record=True,
                pin='1234',
                admin_pin='5678',
                quiet_join_leave=True,
                announce_join_leave=True,
                announce_user_count=True,
                announce_only_user=False,
                music_on_hold='music',
                tenant_uuid=self.default_tenant.uuid,
            )
        )

        conference = conference_dao.get(conference.id)
        conference.name = 'other_conference'
        conference.preprocess_subroutine = 'other_subroutine'
        conference.max_users = 0
        conference.record = False
        conference.pin = '0987'
        conference.admin_pin = '1234'
        conference.quiet_join_leave = False
        conference.announce_join_leave = False
        conference.announce_user_count = False
        conference.announce_only_user = True
        conference.music_on_hold = 'other_music'

        conference_dao.edit(conference)

        row = self.session.query(Conference).first()

        assert_that(
            row,
            has_properties(
                name='other_conference',
                preprocess_subroutine='other_subroutine',
                max_users=0,
                record=False,
                pin='0987',
                admin_pin='1234',
                quiet_join_leave=False,
                announce_join_leave=False,
                announce_user_count=False,
                announce_only_user=True,
                music_on_hold='other_music',
            ),
        )

    def test_edit_set_fields_to_null(self):
        conference = conference_dao.create(
            Conference(
                name='conference',
                preprocess_subroutine='subroutine',
                pin='1234',
                admin_pin='5678',
                music_on_hold='music',
                tenant_uuid=self.default_tenant.uuid,
            )
        )

        conference = conference_dao.get(conference.id)
        conference.name = None
        conference.preprocess_subroutine = None
        conference.pin = None
        conference.admin_pin = None
        conference.music_on_hold = None

        conference_dao.edit(conference)

        row = self.session.query(Conference).first()
        assert_that(
            row,
            has_properties(
                name=none(),
                preprocess_subroutine=none(),
                pin=none(),
                admin_pin=none(),
                music_on_hold=none(),
            ),
        )


class TestDelete(DAOTestCase):
    def test_delete(self):
        conference = self.add_conference()

        conference_dao.delete(conference)

        row = self.session.query(Conference).first()
        assert_that(row, none())

    def test_when_deleting_then_extension_are_dissociated(self):
        conference = self.add_conference()
        extension = self.add_extension(type='conference', typeval=str(conference.id))

        conference_dao.delete(conference)

        row = self.session.query(Extension).first()
        assert_that(row.id, equal_to(extension.id))
        assert_that(row, has_properties(type='user', typeval='0'))
