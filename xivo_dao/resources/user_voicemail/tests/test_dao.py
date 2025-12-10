# Copyright 2013-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains_exactly,
    contains_inanyorder,
    equal_to,
    has_properties,
    has_property,
    none,
)

from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.helpers.exception import NotFoundError
from xivo_dao.tests.test_dao import DAOTestCase

from .. import dao as user_voicemail_dao


class TestUserVoicemail(DAOTestCase):
    def create_user_and_voicemail(self, firstname, exten, context):
        user_row = self.add_user(enablevoicemail=1, firstname=firstname)
        voicemail_row = self.add_voicemail(mailbox=exten, context=context)
        self.link_user_and_voicemail(user_row, voicemail_row.uniqueid)
        return user_row, voicemail_row

    def prepare_voicemail(self, number, context):
        voicemail_row = self.add_voicemail(mailbox=number, context=context)
        return voicemail_row.uniqueid


class TestAssociateUserVoicemail(TestUserVoicemail):
    def test_associate(self):
        user_row = self.add_user()
        context = self.add_context(name='default')
        voicemail_row = self.add_voicemail(mailbox='1000', context=context.name)

        user_voicemail_dao.associate(user_row, voicemail_row)

        self.assert_user_was_associated_with_voicemail(
            user_row.id, voicemail_row.uniqueid, enabled=True
        )

    def assert_user_was_associated_with_voicemail(self, user_id, voicemail_id, enabled):
        result_user_row = self.session.get(UserFeatures, user_id)

        assert_that(result_user_row.voicemailid, equal_to(voicemail_id))
        assert_that(result_user_row.enablevoicemail, equal_to(int(enabled)))


class TestUserVoicemailGetByUserId(TestUserVoicemail):
    def test_get_by_user_id_no_users_or_voicemail(self):
        self.assertRaises(NotFoundError, user_voicemail_dao.get_by_user_id, 1)

    def test_get_by_user_id_with_user_without_line_or_voicemail(self):
        user_row = self.add_user(firstname='King')

        self.assertRaises(NotFoundError, user_voicemail_dao.get_by_user_id, user_row.id)

    def test_get_by_user_id_with_user_without_voicemail(self):
        context = self.add_context(name='default')
        user_line = self.add_user_line_with_exten(
            firstname='King', exten='1000', context=context.name
        )

        self.assertRaises(
            NotFoundError, user_voicemail_dao.get_by_user_id, user_line.user.id
        )

    def test_get_by_user_id_with_voicemail(self):
        context = self.add_context(name='default')
        user_row, voicemail_row = self.create_user_and_voicemail(
            firstname='King', exten='1000', context=context.name
        )

        result = user_voicemail_dao.get_by_user_id(user_row.id)

        assert_that(
            result,
            has_property('user_id', user_row.id),
            has_property('voicemail_id', voicemail_row.uniqueid),
        )


class TestUserVoicemailFindByUserId(TestUserVoicemail):
    def test_find_by_user_id_no_users_or_voicemail(self):
        result = user_voicemail_dao.find_by_user_id(1)

        assert_that(result, none())

    def test_find_by_user_id_with_user_without_line_or_voicemail(self):
        user_row = self.add_user(firstname='King')

        result = user_voicemail_dao.find_by_user_id(user_row.id)

        assert_that(result, none())

    def test_find_by_user_id_with_user_without_voicemail(self):
        context = self.add_context(name='default')
        user_line = self.add_user_line_with_exten(
            firstname='King', exten='1000', context=context.name
        )

        result = user_voicemail_dao.find_by_user_id(user_line.user.id)

        assert_that(result, none())

    def test_find_by_user_id_with_voicemail(self):
        context = self.add_context(name='default')
        user_row, voicemail_row = self.create_user_and_voicemail(
            firstname='King', exten='1000', context=context.name
        )

        result = user_voicemail_dao.find_by_user_id(user_row.id)

        assert_that(
            result,
            has_property('user_id', user_row.id),
            has_property('voicemail_id', voicemail_row.uniqueid),
        )


class TestUserVoicemailFindAllByVoicemailId(TestUserVoicemail):
    def test_given_no_voicemails_then_returns_empty_list(self):
        result = user_voicemail_dao.find_all_by_voicemail_id(1)

        assert_that(result, contains_exactly())

    def test_given_voicemail_has_no_user_associated_then_returns_empty_list(self):
        context = self.add_context(name='default')
        voicemail_row = self.add_voicemail(mailbox='1000', context=context.name)

        result = user_voicemail_dao.find_all_by_voicemail_id(voicemail_row.uniqueid)

        assert_that(result, contains_exactly())

    def test_given_voicemail_is_associated_to_user_then_returns_one_item(self):
        user = self.add_user()
        voicemail = self.add_voicemail()
        user_voicemail_dao.associate(user, voicemail)

        result = user_voicemail_dao.find_all_by_voicemail_id(voicemail.id)

        assert_that(
            result,
            contains_exactly(
                has_properties(user_id=user.id, voicemail_id=voicemail.id)
            ),
        )

    def test_given_voicemail_is_associated_to_two_users_then_returns_two_items(self):
        user1 = self.add_user()
        user2 = self.add_user()
        voicemail = self.add_voicemail()
        user_voicemail_dao.associate(user1, voicemail)
        user_voicemail_dao.associate(user2, voicemail)

        result = user_voicemail_dao.find_all_by_voicemail_id(voicemail.id)

        assert_that(
            result,
            contains_inanyorder(
                has_properties(user_id=user1.id, voicemail_id=voicemail.id),
                has_properties(user_id=user2.id, voicemail_id=voicemail.id),
            ),
        )


class TestDissociateUserVoicemail(TestUserVoicemail):
    def test_dissociate(self):
        context = self.add_context(name='default')
        voicemail_row = self.add_voicemail(mailbox='1000', context=context.name)
        user_row = self.add_user(voicemailid=voicemail_row.uniqueid, enablevoicemail=1)

        user_voicemail_dao.dissociate(user_row, voicemail_row)

        result = self.session.get(UserFeatures, user_row.id)
        assert_that(result.voicemailid, none())
        assert_that(result.enablevoicemail, equal_to(0))

    def test_dissociate_not_associated(self):
        context = self.add_context(name='default')
        voicemail1 = self.add_voicemail(mailbox='1000', context=context.name)
        voicemail2 = self.add_voicemail(mailbox='1001', context=context.name)
        user = self.add_user(voicemailid=voicemail1.uniqueid, enablevoicemail=1)

        user_voicemail_dao.dissociate(user, voicemail2)

        result = self.session.get(UserFeatures, user.id)
        assert_that(result.voicemailid, voicemail1.uniqueid)
        assert_that(result.enablevoicemail, equal_to(1))
