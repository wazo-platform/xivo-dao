# Copyright 2022-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import uuid

from hamcrest import (
    assert_that,
    contains_inanyorder,
    equal_to,
    has_properties,
    none,
    not_none,
)
from sqlalchemy.inspection import inspect

from xivo_dao.alchemy.meeting_authorization import MeetingAuthorization
from xivo_dao.helpers.exception import InputError, NotFoundError
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.tests.test_dao import DAOTestCase

from .. import dao

UNKNOWN_UUID = uuid.uuid4()


class TestFindBy(DAOTestCase):
    def test_given_column_does_not_exist_then_raise_error(self):
        meeting = self.add_meeting(name='my meeting')
        self.assertRaises(
            InputError, dao.find_by, meeting_uuid=meeting.uuid, not_found=True
        )

    def test_given_row_with_value_does_not_exist_then_returns_null(self):
        meeting = self.add_meeting(name='my meeting')
        result = dao.find_by(meeting.uuid, guest_name='not-found')
        assert_that(result, none())

    def test_find_by(self):
        meeting = self.add_meeting(name='my meeting')
        meeting_authorization = self.add_meeting_authorization(
            meeting.uuid, guest_name='jane doe'
        )
        result = dao.find_by(meeting.uuid, guest_name='jane doe')

        assert_that(result.uuid, equal_to(meeting_authorization.uuid))

    def test_find_by_any_meeting(self):
        meeting1 = self.add_meeting(name='my meeting1')
        meeting2 = self.add_meeting(name='my meeting2')
        meeting_authorization_1 = self.add_meeting_authorization(
            meeting1.uuid, guest_name='jane1 doe'
        )
        meeting_authorization_2 = self.add_meeting_authorization(
            meeting2.uuid, guest_name='jane2 doe'
        )

        result = dao.find_by(meeting_uuid=None, guest_name='jane1 doe')
        assert_that(result.uuid, equal_to(meeting_authorization_1.uuid))

        result = dao.find_by(meeting_uuid=None, guest_name='jane2 doe')
        assert_that(result.uuid, equal_to(meeting_authorization_2.uuid))

        result = dao.find_by(meeting_uuid=None, guest_name='jane4')
        assert_that(result, none())


class TestFindAllBy(DAOTestCase):
    def test_find_all_any_meeting(self):
        meeting1 = self.add_meeting(name='my meeting1')
        meeting2 = self.add_meeting(name='my meeting2')
        meeting_authorization_1 = self.add_meeting_authorization(
            meeting1.uuid, guest_name='jane1 doe'
        )
        meeting_authorization_2 = self.add_meeting_authorization(
            meeting2.uuid, guest_name='jane2 doe'
        )

        result = dao.find_all_by(meeting_uuid=None)
        assert_that(
            result,
            contains_inanyorder(meeting_authorization_1, meeting_authorization_2),
        )


class TestGet(DAOTestCase):
    def test_given_no_rows_then_raises_error(self):
        self.assertRaises(NotFoundError, dao.get, UNKNOWN_UUID, UNKNOWN_UUID)
        self.assertRaises(NotFoundError, dao.get, str(UNKNOWN_UUID), str(UNKNOWN_UUID))

    def test_given_row_with_minimal_parameters_then_returns_model(self):
        meeting = self.add_meeting(name='my meeting')
        row = self.add_meeting_authorization(meeting.uuid, guest_name='jane doe')

        model = dao.get(meeting.uuid, row.uuid)
        assert_that(isinstance(model.uuid, uuid.UUID), equal_to(True))
        assert_that(
            model,
            has_properties(
                guest_name=row.guest_name,
                uuid=row.uuid,
            ),
        )

        model = dao.get(str(meeting.uuid), str(row.uuid))
        assert_that(
            model,
            has_properties(
                guest_name=row.guest_name,
                uuid=row.uuid,
            ),
        )

    def test_given_row_with_all_parameters_then_returns_model(self):
        guest_uuid = self._generate_uuid()
        guest_endpoint_sip = self.add_endpoint_sip(template=False)
        meeting = self.add_meeting(
            name='my meeting', guest_endpoint_sip=guest_endpoint_sip
        )
        row = self.add_meeting_authorization(
            meeting.uuid,
            guest_name='jane doe',
            status='accepted',
            guest_uuid=guest_uuid,
        )

        model = dao.get(meeting.uuid, row.uuid)
        assert_that(
            model,
            has_properties(
                guest_endpoint_sip=guest_endpoint_sip,
                guest_name='jane doe',
                status='accepted',
                guest_uuid=guest_uuid,
            ),
        )

    def test_get_any_meeting(self):
        meeting1 = self.add_meeting(name='my meeting1')
        meeting2 = self.add_meeting(name='my meeting2')
        meeting_authorization_1 = self.add_meeting_authorization(
            meeting1.uuid, guest_name='jane1 doe'
        )
        meeting_authorization_2 = self.add_meeting_authorization(
            meeting2.uuid, guest_name='jane2 doe'
        )

        result = dao.get(
            meeting_uuid=None, authorization_uuid=meeting_authorization_1.uuid
        )
        assert_that(result.uuid, equal_to(meeting_authorization_1.uuid))

        result = dao.get(
            meeting_uuid=None, authorization_uuid=meeting_authorization_2.uuid
        )
        assert_that(result.uuid, equal_to(meeting_authorization_2.uuid))


class TestSearch(DAOTestCase):
    def assert_search_returns_result(self, search_result, **parameters):
        result = dao.search(**parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestSearch):
    def test_given_no_meeting_authorization_then_returns_no_empty_result(self):
        meeting = self.add_meeting(name='my meeting')
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected, meeting_uuid=meeting.uuid)

    def test_given_one_meeting_authorization_then_returns_one_result(self):
        meeting = self.add_meeting(name='my meeting')
        model = self.add_meeting_authorization(meeting.uuid, guest_name='jane doe')
        expected = SearchResult(1, [model])

        self.assert_search_returns_result(expected, meeting_uuid=meeting.uuid)

    def test_search_any_meeting(self):
        meeting_1 = self.add_meeting(name='my meeting1')
        meeting_2 = self.add_meeting(name='my meeting2')
        model_1 = self.add_meeting_authorization(meeting_1.uuid, guest_name='jane1 doe')
        model_2 = self.add_meeting_authorization(meeting_2.uuid, guest_name='jane2 doe')

        expected = SearchResult(2, [model_1, model_2])
        self.assert_search_returns_result(expected, meeting_uuid=None)


class TestSearchGivenMultipleMeetingAuthorizations(TestSearch):
    def setUp(self):
        super(TestSearch, self).setUp()
        # Order got changed for such that the creation_time does not match the name order
        self.meeting = self.add_meeting(name='my meeting1')
        self.meeting_authorization_3 = self.add_meeting_authorization(
            meeting_uuid=self.meeting.uuid, guest_name='Casa'
        )
        self.meeting_authorization_4 = self.add_meeting_authorization(
            meeting_uuid=self.meeting.uuid, guest_name='Dunkin'
        )
        self.meeting_authorization_1 = self.add_meeting_authorization(
            meeting_uuid=self.meeting.uuid, guest_name='Ashton'
        )
        self.meeting_authorization_2 = self.add_meeting_authorization(
            meeting_uuid=self.meeting.uuid, guest_name='Beaugarton'
        )

    def test_when_searching_then_returns_one_result(self):
        expected = SearchResult(1, [self.meeting_authorization_2])

        self.assert_search_returns_result(
            expected, meeting_uuid=self.meeting.uuid, search='eau'
        )

    def test_when_sorting_then_returns_result_in_ascending_order(self):
        expected = SearchResult(
            4,
            [
                self.meeting_authorization_1,
                self.meeting_authorization_2,
                self.meeting_authorization_3,
                self.meeting_authorization_4,
            ],
        )

        self.assert_search_returns_result(
            expected, meeting_uuid=self.meeting.uuid, order='guest_name'
        )

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(
        self,
    ):
        expected = SearchResult(
            4,
            [
                self.meeting_authorization_4,
                self.meeting_authorization_3,
                self.meeting_authorization_2,
                self.meeting_authorization_1,
            ],
        )

        self.assert_search_returns_result(
            expected,
            meeting_uuid=self.meeting.uuid,
            order='guest_name',
            direction='desc',
        )

    def test_when_sorting_by_creation_time(self):
        expected = SearchResult(
            4,
            [
                self.meeting_authorization_3,
                self.meeting_authorization_4,
                self.meeting_authorization_1,
                self.meeting_authorization_2,
            ],
        )

        self.assert_search_returns_result(
            expected,
            meeting_uuid=self.meeting.uuid,
            order='creation_time',
            direction='asc',
        )

    def test_when_limiting_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.meeting_authorization_1])

        self.assert_search_returns_result(
            expected, meeting_uuid=self.meeting.uuid, limit=1
        )

    def test_when_offset_then_returns_right_number_of_items(self):
        expected = SearchResult(
            4,
            [
                self.meeting_authorization_2,
                self.meeting_authorization_3,
                self.meeting_authorization_4,
            ],
        )

        self.assert_search_returns_result(
            expected, meeting_uuid=self.meeting.uuid, offset=1
        )

    def test_when_doing_a_paginated_search_then_returns_a_paginated_result(self):
        expected = SearchResult(3, [self.meeting_authorization_2])

        self.assert_search_returns_result(
            expected,
            meeting_uuid=self.meeting.uuid,
            search='a',
            order='guest_name',
            direction='desc',
            offset=1,
            limit=1,
        )


class TestCreate(DAOTestCase):
    def test_create_minimal_parameters(self):
        meeting = self.add_meeting(name='my meeting')
        guest_uuid = self._generate_uuid()
        model = MeetingAuthorization(meeting_uuid=meeting.uuid, guest_uuid=guest_uuid)

        result = dao.create(model)

        assert_that(inspect(result).persistent)
        assert_that(
            result,
            has_properties(
                uuid=not_none(),
                meeting_uuid=meeting.uuid,
                guest_uuid=guest_uuid,
            ),
        )

    def test_create_all_parameters(self):
        meeting = self.add_meeting(name='my meeting')
        guest_uuid = self._generate_uuid()
        model = MeetingAuthorization(
            meeting_uuid=meeting.uuid,
            guest_name='name',
            guest_uuid=guest_uuid,
            status='pending',
        )

        result = dao.create(model)

        assert_that(inspect(result).persistent)
        assert_that(
            result,
            has_properties(
                uuid=not_none(),
                meeting_uuid=meeting.uuid,
                guest_name='name',
                guest_uuid=guest_uuid,
                status='pending',
            ),
        )


class TestEdit(DAOTestCase):
    def test_edit_all_parameters(self):
        meeting = self.add_meeting(name='my meeting')
        row = self.add_meeting_authorization(
            meeting.uuid,
            guest_name='jane doe',
            status='accepted',
        )

        model = dao.get(meeting.uuid, row.uuid)
        model.guest_name = 'new'

        dao.edit(model)

        self.session.expire_all()
        assert_that(
            model,
            has_properties(
                uuid=model.uuid,
                guest_name='new',
            ),
        )

    def test_edit_set_null(self):
        meeting = self.add_meeting(name='my meeting')
        row = self.add_meeting_authorization(
            meeting.uuid,
            guest_name='jane doe',
            status='accepted',
        )

        model = dao.get(meeting.uuid, row.uuid)
        model.guest_name = None

        dao.edit(model)
        self.session.expire_all()
        assert_that(
            model,
            has_properties(
                uuid=model.uuid,
                guest_name=None,
            ),
        )


class TestDelete(DAOTestCase):
    def test_delete(self):
        meeting = self.add_meeting(name='my meeting')
        model = self.add_meeting_authorization(
            meeting.uuid,
            guest_name='jane doe',
        )

        dao.delete(model)

        assert_that(inspect(model).deleted)
