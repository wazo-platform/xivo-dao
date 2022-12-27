# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import and_
from hamcrest import assert_that, contains_inanyorder, equal_to, none

from xivo_dao.tests.test_dao import DAOTestCase
from ..dialaction import Dialaction
from ..voicemail import Voicemail


class TestGetOldNumberContext(DAOTestCase):

    def test_when_number_context_are_modified(self):
        voicemail = self.add_voicemail(number='1000', context='default')
        voicemail.number = '1001'
        voicemail.context = 'not_default'

        old_number, old_context = voicemail.get_old_number_context()

        assert_that(old_number, equal_to('1000'))
        assert_that(old_context, equal_to('default'))

    def test_when_only_number_is_modified(self):
        voicemail = self.add_voicemail(number='1000', context='default')
        voicemail.number = '1001'

        old_number, old_context = voicemail.get_old_number_context()

        assert_that(old_number, equal_to('1000'))
        assert_that(old_context, equal_to('default'))

    def test_when_only_context_is_modified(self):
        voicemail = self.add_voicemail(number='1000', context='default')
        voicemail.context = 'not_default'

        old_number, old_context = voicemail.get_old_number_context()

        assert_that(old_number, equal_to('1000'))
        assert_that(old_context, equal_to('default'))


class TestTenantUUID(DAOTestCase):

    def test_tenant_uuid_getter(self):
        tenant = self.add_tenant()
        context = self.add_context(tenant_uuid=tenant.uuid)

        voicemail = self.add_voicemail(context=context.name)

        assert_that(voicemail.tenant_uuid, equal_to(tenant.uuid))

    def test_tenant_uuid_expression(self):
        tenant = self.add_tenant()
        context = self.add_context(tenant_uuid=tenant.uuid)

        voicemail = self.add_voicemail(context=context.name)

        result = self.session.query(Voicemail).filter(and_(
            Voicemail.id == voicemail.id,
            Voicemail.tenant_uuid.in_([tenant.uuid]),
        )).first()

        assert_that(result, equal_to(voicemail))


class TestUsers(DAOTestCase):

    def test_getter(self):
        voicemail = self.add_voicemail()
        user1 = self.add_user(voicemail_id=voicemail.id)
        user2 = self.add_user(voicemail_id=voicemail.id)

        assert_that(voicemail.users, contains_inanyorder(user1, user2))


class TestDelete(DAOTestCase):

    def test_dialaction_actions_are_deleted(self):
        voicemail = self.add_voicemail()
        self.add_dialaction(category='ivr_choice', action='voicemail', actionarg1=voicemail.id)
        self.add_dialaction(category='ivr', action='voicemail', actionarg1=voicemail.id)
        self.add_dialaction(category='user', action='voicemail', actionarg1=voicemail.id)
        self.add_dialaction(category='incall', action='voicemail', actionarg1=voicemail.id)

        self.session.delete(voicemail)
        self.session.flush()

        row = self.session.query(Dialaction).first()
        assert_that(row, none())
