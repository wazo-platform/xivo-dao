# Copyright 2021-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import uuid

from hamcrest import (
    all_of,
    assert_that,
    contains_inanyorder,
    equal_to,
    has_items,
    has_properties,
    is_not,
    none,
    not_,
    not_none,
)
from sqlalchemy.inspection import inspect

from xivo_dao.alchemy.meeting import Meeting
from xivo_dao.helpers.exception import InputError, NotFoundError
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.tests.test_dao import DAOTestCase

from .. import dao

UNKNOWN_UUID = uuid.uuid4()


class TestFindBy(DAOTestCase):
    def test_given_column_does_not_exist_then_raise_error(self):
        self.assertRaises(InputError, dao.find_by, column=1)

    def test_given_row_with_value_does_not_exist_then_returns_null(self):
        result = dao.find_by(name='abcd')
        assert_that(result, none())

    def test_find_by(self):
        meeting = self.add_meeting(name='my meeting')
        result = dao.find_by(name='my meeting')

        assert_that(result.uuid, equal_to(meeting.uuid))

    def test_find_by_owner(self):
        user_1 = self.add_user()
        user_2 = self.add_user()
        user_3 = self.add_user()

        meeting_1 = self.add_meeting(owners=[user_1, user_3])
        self.add_meeting()

        result = dao.find_by(owner=user_1.uuid)
        assert_that(result.uuid, equal_to(meeting_1.uuid))

        result = dao.find_by(owner=user_2.uuid)
        assert_that(result, none())

    def test_find_by_multi_tenant(self):
        tenant = self.add_tenant()

        row = self.add_meeting()
        resource = dao.find_by(name=row.name, tenant_uuids=[tenant.uuid])
        assert_that(resource, none())

        row = self.add_meeting(tenant_uuid=tenant.uuid)
        resource = dao.find_by(name=row.name, tenant_uuids=[tenant.uuid])
        assert_that(resource, equal_to(row))


class TestFindAllBy(DAOTestCase):
    def test_find_all_multi_tenant(self):
        tenant = self.add_tenant()

        resource1 = self.add_meeting(name='my meeting', tenant_uuid=tenant.uuid)
        resource2 = self.add_meeting(name='my meeting')

        tenants = [tenant.uuid, self.default_tenant.uuid]
        meetings = dao.find_all_by(name='my meeting', tenant_uuids=tenants)
        assert_that(meetings, has_items(resource1, resource2))

        tenants = [tenant.uuid]
        meetings = dao.find_all_by(name='my meeting', tenant_uuids=tenants)
        assert_that(meetings, all_of(has_items(resource1), not_(has_items(resource2))))


class TestGet(DAOTestCase):
    def test_given_no_rows_then_raises_error(self):
        self.assertRaises(NotFoundError, dao.get, UNKNOWN_UUID)
        self.assertRaises(NotFoundError, dao.get, str(UNKNOWN_UUID))

    def test_given_row_with_minimal_parameters_then_returns_model(self):
        row = self.add_meeting()

        model = dao.get(row.uuid)
        assert_that(isinstance(row.uuid, uuid.UUID), equal_to(True))
        assert_that(
            model,
            has_properties(
                name=row.name,
                uuid=row.uuid,
            ),
        )

        model = dao.get(str(row.uuid))
        assert_that(
            model,
            has_properties(
                name=row.name,
                uuid=row.uuid,
            ),
        )

    def test_given_row_with_all_parameters_then_returns_model(self):
        guest_endpoint_sip = self.add_endpoint_sip(template=False)
        owner_1 = self.add_user()
        owner_2 = self.add_user()

        row = self.add_meeting(
            name='the meeting',
            guest_endpoint_sip=guest_endpoint_sip,
            owners=[owner_1, owner_2],
            tenant_uuid=self.default_tenant.uuid,
        )

        model = dao.get(row.uuid)
        assert_that(
            model,
            has_properties(
                name='the meeting',
                guest_endpoint_sip=guest_endpoint_sip,
                guest_endpoint_sip_uuid=guest_endpoint_sip.uuid,
                owners=contains_inanyorder(owner_1, owner_2),
                owner_uuids=contains_inanyorder(owner_1.uuid, owner_2.uuid),
                tenant_uuid=self.default_tenant.uuid,
            ),
        )

    def test_get_multi_tenant(self):
        tenant = self.add_tenant()

        row = self.add_meeting(tenant_uuid=tenant.uuid)
        model = dao.get(row.uuid, tenant_uuids=[tenant.uuid])
        assert_that(model, equal_to(row))

        row = self.add_meeting()
        self.assertRaises(
            NotFoundError,
            dao.get,
            row.uuid,
            tenant_uuids=[tenant.uuid],
        )


class TestSearch(DAOTestCase):
    def assert_search_returns_result(self, search_result, **parameters):
        result = dao.search(**parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestSearch):
    def test_given_no_sip_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_on_sip_then_returns_one_result(self):
        model = self.add_meeting()
        expected = SearchResult(1, [model])

        self.assert_search_returns_result(expected)

    def test_search_multi_tenant(self):
        tenant = self.add_tenant()

        model_1 = self.add_meeting(name='sort1')
        model_2 = self.add_meeting(name='sort2', tenant_uuid=tenant.uuid)

        expected = SearchResult(2, [model_1, model_2])
        tenants = [tenant.uuid, self.default_tenant.uuid]
        self.assert_search_returns_result(expected, tenant_uuids=tenants)

        expected = SearchResult(1, [model_2])
        tenants = [tenant.uuid]
        self.assert_search_returns_result(expected, tenant_uuids=tenants)


class TestSearchGivenMultipleMeetings(TestSearch):
    def setUp(self):
        super(TestSearch, self).setUp()
        # Order got changed for such that the creation_time does not match the name order
        self.meeting3 = self.add_meeting(name='Casa')
        self.meeting4 = self.add_meeting(name='Dunkin')
        self.meeting1 = self.add_meeting(name='Ashton')
        self.meeting2 = self.add_meeting(name='Beaugarton')

    def test_when_searching_then_returns_one_result(self):
        expected = SearchResult(1, [self.meeting2])

        self.assert_search_returns_result(expected, search='eau')

    def test_when_sorting_then_returns_result_in_ascending_order(self):
        expected = SearchResult(
            4,
            [
                self.meeting1,
                self.meeting2,
                self.meeting3,
                self.meeting4,
            ],
        )

        self.assert_search_returns_result(expected, order='name')

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(
        self,
    ):
        expected = SearchResult(
            4,
            [
                self.meeting4,
                self.meeting3,
                self.meeting2,
                self.meeting1,
            ],
        )

        self.assert_search_returns_result(expected, order='name', direction='desc')

    def test_when_sorting_by_creation_time(self):
        expected = SearchResult(
            4,
            [
                self.meeting3,
                self.meeting4,
                self.meeting1,
                self.meeting2,
            ],
        )

        self.assert_search_returns_result(
            expected, order='creation_time', direction='asc'
        )

    def test_when_limiting_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.meeting1])

        self.assert_search_returns_result(expected, limit=1)

    def test_when_offset_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.meeting2, self.meeting3, self.meeting4])

        self.assert_search_returns_result(expected, offset=1)

    def test_when_doing_a_paginated_search_then_returns_a_paginated_result(self):
        expected = SearchResult(3, [self.meeting2])

        self.assert_search_returns_result(
            expected,
            search='a',
            order='name',
            direction='desc',
            offset=1,
            limit=1,
        )


class TestCreate(DAOTestCase):
    def test_create_minimal_parameters(self):
        model = Meeting(tenant_uuid=self.default_tenant.uuid)

        result = dao.create(model)

        assert_that(inspect(result).persistent)
        assert_that(
            result,
            has_properties(
                uuid=not_none(),
                name=None,
                tenant_uuid=self.default_tenant.uuid,
                number=not_none(),
                require_authorization=False,
            ),
        )

    def test_create_all_parameters(self):
        endpoint_sip = self.add_endpoint_sip(template=False)
        owners = [
            self.add_user(),
            self.add_user(),
        ]

        model = Meeting(
            tenant_uuid=self.default_tenant.uuid,
            name='name',
            guest_endpoint_sip=endpoint_sip,
            owners=owners,
            require_authorization=True,
        )

        result = dao.create(model)

        assert_that(inspect(result).persistent)
        assert_that(
            result,
            has_properties(
                uuid=not_none(),
                name='name',
                tenant_uuid=self.default_tenant.uuid,
                owners=owners,
                guest_endpoint_sip_uuid=endpoint_sip.uuid,
                created_at=is_not(none()),
                number=not_none(),
                require_authorization=True,
            ),
        )


class TestEdit(DAOTestCase):
    def test_edit_all_parameters(self):
        row = self.add_meeting()

        endpoint = self.add_endpoint_sip(template=False)
        owners = [self.add_user(), self.add_user()]

        model = dao.get(row.uuid)
        model.name = 'new'
        model.guest_endpoint_sip = endpoint
        model.owners = owners

        dao.edit(model)

        self.session.expire_all()
        assert_that(
            model,
            has_properties(
                uuid=model.uuid,
                name='new',
                guest_endpoint_sip_uuid=endpoint.uuid,
                owner_uuids=[owner.uuid for owner in owners],
            ),
        )

    def test_edit_set_null(self):
        endpoint = self.add_endpoint_sip(template=False)
        owners = [self.add_user(), self.add_user()]

        row = self.add_meeting(
            name='meeting', guest_endpoint_sip=endpoint, owners=owners
        )

        model = dao.get(row.uuid)
        model.name = None
        model.guest_endpoint_sip = None
        model.owners = []

        dao.edit(model)
        self.session.expire_all()
        assert_that(
            model,
            has_properties(
                uuid=model.uuid,
                name=None,
                guest_endpoint_sip_uuid=None,
                owner_uuids=[],
            ),
        )


class TestDelete(DAOTestCase):
    def test_delete(self):
        model = self.add_meeting()

        dao.delete(model)

        assert_that(inspect(model).deleted)

    def test_delete_when_associated_to_an_ingress(self):
        tenant = self.add_tenant()
        ingress_http = self.add_ingress_http(tenant_uuid=tenant.uuid)
        meeting = self.add_meeting(tenant_uuid=tenant.uuid)

        dao.delete(meeting)

        assert_that(inspect(meeting).deleted)

        new_meeting = self.add_meeting(tenant_uuid=tenant.uuid)
        assert_that(
            new_meeting.ingress_http,
            equal_to(ingress_http),
            'the ingress should not have been deleted',
        )
