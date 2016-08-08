# -*- coding: utf-8 -*-

# Copyright (C) 2013-2016 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from hamcrest import assert_that, has_property, instance_of, equal_to, none, contains, has_items

from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.resources.user_voicemail import dao as user_voicemail_dao
from xivo_dao.resources.user_voicemail.model import UserVoicemail
from xivo_dao.helpers.exception import NotFoundError
from xivo_dao.tests.test_dao import DAOTestCase


class TestUserVoicemail(DAOTestCase):

    def create_user_and_voicemail(self, firstname, exten, context):
        user_row = self.add_user(enablevoicemail=1, firstname='King')
        voicemail_row = self.add_voicemail(mailbox='1000', context='default')
        self.link_user_and_voicemail(user_row, voicemail_row.uniqueid)
        return user_row, voicemail_row

    def prepare_voicemail(self, number):
        voicemail_row = self.add_voicemail(mailbox=number, context='default')
        return voicemail_row.uniqueid


class TestAssociateUserVoicemail(TestUserVoicemail):

    def test_associate(self):
        user_row = self.add_user()
        voicemail_row = self.add_voicemail(mailbox='1000', context='default')

        user_voicemail = UserVoicemail(user_id=user_row.id,
                                       voicemail_id=voicemail_row.uniqueid)
        user_voicemail_dao.associate(user_voicemail)

        self.assert_user_was_associated_with_voicemail(user_row.id,
                                                       voicemail_row.uniqueid,
                                                       enabled=True)

    def assert_user_was_associated_with_voicemail(self, user_id, voicemail_id, enabled):
        result_user_row = self.session.query(UserFeatures).get(user_id)

        assert_that(result_user_row.voicemailid, equal_to(voicemail_id))
        assert_that(result_user_row.enablevoicemail, equal_to(int(enabled)))


class TestUserVoicemailGetByUserId(TestUserVoicemail):

    def test_get_by_user_id_no_users_or_voicemail(self):
        self.assertRaises(NotFoundError, user_voicemail_dao.get_by_user_id, 1)

    def test_get_by_user_id_with_user_without_line_or_voicemail(self):
        user_row = self.add_user(firstname='King')

        self.assertRaises(NotFoundError, user_voicemail_dao.get_by_user_id, user_row.id)

    def test_get_by_user_id_with_user_without_voicemail(self):
        user_line = self.add_user_line_with_exten(firstname='King', exten='1000', context='default')

        self.assertRaises(NotFoundError, user_voicemail_dao.get_by_user_id, user_line.user.id)

    def test_get_by_user_id_with_voicemail(self):
        user_row, voicemail_row = self.create_user_and_voicemail(firstname='King', exten='1000', context='default')

        result = user_voicemail_dao.get_by_user_id(user_row.id)

        assert_that(result, instance_of(UserVoicemail))
        assert_that(result,
                    has_property('user_id', user_row.id),
                    has_property('voicemail_id', voicemail_row.uniqueid))


class TestUserVoicemailFindByUserId(TestUserVoicemail):

    def test_find_by_user_id_no_users_or_voicemail(self):
        result = user_voicemail_dao.find_by_user_id(1)

        assert_that(result, none())

    def test_find_by_user_id_with_user_without_line_or_voicemail(self):
        user_row = self.add_user(firstname='King')

        result = user_voicemail_dao.find_by_user_id(user_row.id)

        assert_that(result, none())

    def test_find_by_user_id_with_user_without_voicemail(self):
        user_line = self.add_user_line_with_exten(firstname='King', exten='1000', context='default')

        result = user_voicemail_dao.find_by_user_id(user_line.user.id)

        assert_that(result, none())

    def test_find_by_user_id_with_voicemail(self):
        user_row, voicemail_row = self.create_user_and_voicemail(firstname='King', exten='1000', context='default')

        result = user_voicemail_dao.find_by_user_id(user_row.id)

        assert_that(result, instance_of(UserVoicemail))
        assert_that(result,
                    has_property('user_id', user_row.id),
                    has_property('voicemail_id', voicemail_row.uniqueid))


class TestUserVoicemailFindAllByVoicemailId(TestUserVoicemail):

    def test_given_no_voicemails_then_returns_empty_list(self):
        result = user_voicemail_dao.find_all_by_voicemail_id(1)

        assert_that(result, contains())

    def test_given_voicemail_has_no_user_associated_then_returns_empty_list(self):
        voicemail_row = self.add_voicemail(mailbox='1000', context='default')

        result = user_voicemail_dao.find_all_by_voicemail_id(voicemail_row.uniqueid)

        assert_that(result, contains())

    def test_given_voicemail_is_associated_to_user_then_returns_one_item(self):
        user_row, voicemail_row = self.create_user_and_voicemail(firstname='Dolly',
                                                                 exten='1000',
                                                                 context='default')
        expected = UserVoicemail(user_id=user_row.id,
                                 voicemail_id=voicemail_row.uniqueid,
                                 enabled=True)

        result = user_voicemail_dao.find_all_by_voicemail_id(voicemail_row.uniqueid)

        assert_that(result, contains(expected))

    def test_given_voicemail_is_associated_to_two_users_then_returns_two_items(self):
        first_user, voicemail_row = self.create_user_and_voicemail(firstname='Dolly',
                                                                   exten='1000',
                                                                   context='default')
        second_user = self.add_user(enablevoicemail=1)
        self.link_user_and_voicemail(second_user, voicemail_row.uniqueid)

        expected = has_items(UserVoicemail(user_id=first_user.id,
                                           voicemail_id=voicemail_row.uniqueid,
                                           enabled=True),
                             UserVoicemail(user_id=second_user.id,
                                           voicemail_id=voicemail_row.uniqueid,
                                           enabled=True))

        result = user_voicemail_dao.find_all_by_voicemail_id(voicemail_row.uniqueid)

        assert_that(result, expected)


class TestDissociateUserVoicemail(TestUserVoicemail):

    def test_dissociate(self):
        voicemail_row = self.add_voicemail(mailbox='1000', context='default')
        user_row = self.add_user(voicemailid=voicemail_row.uniqueid,
                                 enablevoicemail=1)

        user_voicemail = UserVoicemail(user_id=user_row.id,
                                       voicemail_id=voicemail_row.uniqueid)
        user_voicemail_dao.dissociate(user_voicemail)

        self.assert_user_was_dissociated_from_voicemail(user_row.id)

    def assert_user_was_dissociated_from_voicemail(self, user_id):
        result_user_row = self.session.query(UserFeatures).get(user_id)

        assert_that(result_user_row.voicemailid, none())
        assert_that(result_user_row.enablevoicemail, equal_to(0))
