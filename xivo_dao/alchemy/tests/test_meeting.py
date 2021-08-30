# -*- coding: utf-8 -*-
# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, contains_inanyorder, has_properties

from xivo_dao.tests.test_dao import DAOTestCase

from ..meeting import Meeting, MeetingOwner


class TestMeeting(DAOTestCase):

    def test_create_all_relations(self):
        owner_1 = self.add_user()
        owner_2 = self.add_user()
        endpoint_sip = self.add_endpoint_sip()

        meeting = Meeting(
            name='My meeting',
            owners=[owner_1, owner_2],
            guest_endpoint_sip=endpoint_sip,
            tenant_uuid=self.default_tenant.uuid,
        )

        self.session.add(meeting)
        self.session.flush()
        self.session.expunge_all()

        row = self.session.query(Meeting).filter_by(uuid=meeting.uuid).first()
        assert_that(row, has_properties(
            uuid=meeting.uuid,
            name='My meeting',
            tenant_uuid=self.default_tenant.uuid,
            guest_endpoint_sip_uuid=endpoint_sip.uuid,
        ))
        rows = self.session.query(MeetingOwner).filter_by(meeting_uuid=meeting.uuid).all()
        assert_that(rows, contains_inanyorder(
            has_properties(meeting_uuid=meeting.uuid, user_uuid=owner_1.uuid),
            has_properties(meeting_uuid=meeting.uuid, user_uuid=owner_2.uuid),
        ))
