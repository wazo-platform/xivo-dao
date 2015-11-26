# -*- coding: utf-8 -*-

# Copyright (C) 2012-2015 Avencall
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

from hamcrest import any_of
from hamcrest import assert_that
from hamcrest import equal_to

from xivo_dao import user_dao
from xivo_dao.tests.test_dao import DAOTestCase


class TestUserFeaturesDAO(DAOTestCase):

    def test_get_user_by_number_context(self):
        context, number = 'default', '1234'
        user_line = self.add_user_line_with_exten(exten=number,
                                                  context=context)

        user = user_dao.get_user_by_number_context(number, context)

        assert_that(user.id, equal_to(user_line.user.id))

    def test_get_user_by_number_context_line_commented(self):
        context, number = 'default', '1234'
        self.add_user_line_with_exten(exten=number,
                                      context=context,
                                      commented_line=1)

        self.assertRaises(LookupError, user_dao.get_user_by_number_context, number, context)

    def test_get_uuid_by_email_with_unknown_email(self):
        user = self.add_user()
        voicemail = self.add_voicemail(email='bob@cat.example.com')
        self.link_user_and_voicemail(user, voicemail.uniqueid)

        self.assertRaises(LookupError, user_dao.get_uuid_by_email, 'alice@merveille.com')

    def test_get_uuid_by_email(self):
        user = self.add_user()
        voicemail = self.add_voicemail(email='alice@merveille.com')
        self.link_user_and_voicemail(user, voicemail.uniqueid)

        result = user_dao.get_uuid_by_email('alice@merveille.com')

        assert_that(result, equal_to(user.uuid))

    def test_get_uuid_by_email_with_multiple_results(self):
        user1 = self.add_user()
        user2 = self.add_user()
        voicemail = self.add_voicemail(email='alice@merveille.com')
        self.link_user_and_voicemail(user1, voicemail.uniqueid)
        self.link_user_and_voicemail(user2, voicemail.uniqueid)

        result = user_dao.get_uuid_by_email('alice@merveille.com')

        assert_that(result, any_of(user1.uuid, user2.uuid))
