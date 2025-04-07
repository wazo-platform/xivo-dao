# Copyright 2021-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import uuid

from hamcrest import assert_that, equal_to, has_properties, is_, is_not, none

from xivo_dao.tests.test_dao import DAOTestCase

from ..meeting import Meeting
from ..meeting_authorization import MeetingAuthorization


class TestMeeting(DAOTestCase):
    def test_create(self):
        meeting = self.add_meeting()
        guest_uuid = uuid.uuid4()

        meeting_authorization = MeetingAuthorization(
            guest_uuid=guest_uuid,
            meeting_uuid=meeting.uuid,
            guest_name='Jane Doe',
            status='pending',
        )

        self.session.add(meeting_authorization)
        self.session.flush()
        self.session.expunge_all()

        row = (
            self.session.query(MeetingAuthorization)
            .filter_by(uuid=meeting_authorization.uuid)
            .first()
        )
        assert_that(
            row,
            has_properties(
                uuid=meeting_authorization.uuid,
                guest_name='Jane Doe',
                guest_uuid=guest_uuid,
                status='pending',
            ),
        )

    def test_meeting(self):
        meeting = self.add_meeting()

        meeting_authorization = MeetingAuthorization(
            guest_uuid=uuid.uuid4(),
            meeting_uuid=meeting.uuid,
            guest_name='Jane Doe',
            status='pending',
        )

        self.session.add(meeting_authorization)
        self.session.flush()

        assert_that(meeting_authorization.meeting, equal_to(meeting))

    def test_guest_endpoint_sip(self):
        endpoint_sip = self.add_endpoint_sip()
        meeting = self.add_meeting(guest_endpoint_sip=endpoint_sip)

        meeting_authorization = MeetingAuthorization(
            guest_uuid=uuid.uuid4(),
            meeting_uuid=meeting.uuid,
            guest_name='Jane Doe',
            status='pending',
        )

        self.session.add(meeting_authorization)
        self.session.flush()

        assert_that(meeting_authorization.guest_endpoint_sip, equal_to(endpoint_sip))

    def test_meeting_is_not_deleted(self):
        meeting = self.add_meeting()

        meeting_authorization = MeetingAuthorization(
            guest_uuid=uuid.uuid4(),
            meeting_uuid=meeting.uuid,
            guest_name='Jane Doe',
            status='pending',
        )

        self.session.add(meeting_authorization)
        self.session.flush()

        assert_that(meeting_authorization.meeting, equal_to(meeting))

        self.session.delete(meeting_authorization)
        self.session.flush()
        self.session.expunge_all()

        row = self.session.query(Meeting).filter_by(uuid=meeting.uuid).first()
        assert_that(row, is_not(none()))

    def test_deleting_a_meeting_deletes_authorizations(self):
        meeting = self.add_meeting()

        meeting_authorization = MeetingAuthorization(
            guest_uuid=uuid.uuid4(),
            meeting_uuid=meeting.uuid,
            guest_name='Jane Doe',
            status='pending',
        )

        self.session.add(meeting_authorization)
        self.session.flush()

        self.session.delete(meeting)
        self.session.flush()
        self.session.expunge_all()

        row = self.session.query(Meeting).filter_by(uuid=meeting.uuid).first()
        assert_that(row, is_(none()))
        row = (
            self.session.query(MeetingAuthorization)
            .filter_by(uuid=meeting_authorization.uuid)
            .first()
        )
        assert_that(row, is_(none()))
