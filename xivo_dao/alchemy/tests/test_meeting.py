# Copyright 2021-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains_inanyorder,
    empty,
    equal_to,
    has_properties,
    is_,
    none,
    not_,
)

from xivo_dao.tests.test_dao import DAOTestCase

from ..endpoint_sip import EndpointSIP
from ..meeting import Meeting, MeetingOwner
from ..userfeatures import UserFeatures


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
            number=self.random_number(length=6),
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

    def test_owner_uuids(self):
        owner_1 = self.add_user()
        owner_2 = self.add_user()
        endpoint_sip = self.add_endpoint_sip()

        meeting = Meeting(
            name='My meeting',
            owners=[owner_1, owner_2],
            guest_endpoint_sip=endpoint_sip,
            tenant_uuid=self.default_tenant.uuid,
            number=self.random_number(length=6),
        )

        self.session.add(meeting)
        self.session.flush()
        self.session.expunge_all()

        row = self.session.query(Meeting).filter_by(uuid=meeting.uuid).first()
        assert_that(row.owner_uuids, contains_inanyorder(owner_1.uuid, owner_2.uuid))

    def test_that_endpoints_are_not_leaked(self):
        owner_1 = self.add_user()
        owner_2 = self.add_user()
        endpoint_sip = self.add_endpoint_sip()

        meeting = Meeting(
            name='My meeting',
            owners=[owner_1, owner_2],
            guest_endpoint_sip=endpoint_sip,
            tenant_uuid=self.default_tenant.uuid,
            number=self.random_number(length=6),
        )

        self.session.add(meeting)
        self.session.flush()

        self.session.delete(meeting)
        self.session.flush()
        self.session.expunge_all()

        row = self.session.query(EndpointSIP).filter_by(uuid=endpoint_sip.uuid).first()
        assert_that(row, is_(none()))

    def test_that_users_are_not_deleted(self):
        owner_1 = self.add_user()
        owner_2 = self.add_user()
        endpoint_sip = self.add_endpoint_sip()

        meeting = Meeting(
            name='My meeting',
            owners=[owner_1, owner_2],
            guest_endpoint_sip=endpoint_sip,
            tenant_uuid=self.default_tenant.uuid,
            number=self.random_number(length=6),
        )

        self.session.add(meeting)
        self.session.flush()

        self.session.delete(meeting)
        self.session.flush()
        self.session.expunge_all()

        row = self.session.query(UserFeatures).filter_by(uuid=owner_1.uuid).first()
        assert_that(row, is_(not_(none())))

        row = self.session.query(UserFeatures).filter_by(uuid=owner_2.uuid).first()
        assert_that(row, is_(not_(none())))

        rows = self.session.query(MeetingOwner).filter_by(meeting_uuid=meeting.uuid).all()
        assert_that(rows, empty())

    def test_that_deleting_an_owner_removes_it_from_the_owners(self):
        owner_1 = self.add_user()
        owner_2 = self.add_user()
        endpoint_sip = self.add_endpoint_sip()

        meeting = Meeting(
            name='My meeting',
            owners=[owner_1, owner_2],
            guest_endpoint_sip=endpoint_sip,
            tenant_uuid=self.default_tenant.uuid,
            number=self.random_number(length=6),
        )

        self.session.add(meeting)
        self.session.flush()

        self.session.delete(owner_1)
        self.session.flush()
        self.session.expunge_all()

        rows = self.session.query(MeetingOwner).filter_by(meeting_uuid=meeting.uuid).all()
        assert_that(rows, contains_inanyorder(
            has_properties(meeting_uuid=meeting.uuid, user_uuid=owner_2.uuid),
        ))

    def test_ingress_http(self):
        tenant = self.add_tenant()
        ingress_http = self.add_ingress_http(tenant_uuid=tenant.uuid)
        meeting = Meeting(
            name='My meeting',
            tenant_uuid=tenant.uuid,
            number=self.random_number(length=6),
        )

        self.session.add(meeting)
        self.session.flush()

        assert_that(meeting.ingress_http, equal_to(ingress_http))

    def test_ingress_http_no_config(self):
        tenant = self.add_tenant()
        meeting = Meeting(
            name='My meeting',
            tenant_uuid=tenant.uuid,
            number=self.random_number(length=6),
        )

        self.session.add(meeting)
        self.session.flush()

        assert_that(meeting.ingress_http, equal_to(None))
