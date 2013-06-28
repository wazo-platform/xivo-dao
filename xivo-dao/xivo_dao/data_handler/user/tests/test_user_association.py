# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

import unittest

from mock import Mock, patch, ANY
from xivo_dao.data_handler.user import user_association
from xivo_dao.data_handler.user.services import UserNotFoundError
from xivo_dao.data_handler.voicemail.dao import VoicemailNotFoundError
from xivo_dao.data_handler.voicemail.model import Voicemail
from xivo_dao.data_handler.user.model import User


class TestUserAssociation(unittest.TestCase):

    @patch('xivo_dao.data_handler.voicemail.dao.get_voicemail_by_id')
    @patch('xivo_dao.data_handler.user.services.user_dao.get_user_by_id')
    def test_associate_voicemail_when_user_inexistant(self, get_user, get_voicemail):
        user_id = 21
        voicemail_id = 32

        get_user.side_effect = LookupError()
        get_voicemail.return_value = Mock()

        self.assertRaises(UserNotFoundError, user_association.associate_voicemail, user_id, voicemail_id)

    @patch('xivo_dao.data_handler.voicemail.dao.get_voicemail_by_id')
    @patch('xivo_dao.data_handler.user.services.user_dao.get_user_by_id')
    def test_associate_voicemail_when_voicemail_inexistant(self, get_user, get_voicemail):
        user_id = 21
        voicemail_id = 32

        get_user.return_value = Mock()
        get_voicemail.side_effect = LookupError()

        self.assertRaises(VoicemailNotFoundError, user_association.associate_voicemail, user_id, voicemail_id)

    @patch('xivo_dao.data_handler.voicemail.dao.get_voicemail_by_id')
    @patch('xivo_dao.data_handler.voicemail.dao.edit')
    @patch('xivo_dao.data_handler.user.services.user_dao.get_user_by_id')
    def test_associate_voicemail(self, get_user, edit_voicemail, get_voicemail):
        user_id = 21
        voicemail_id = 32

        voicemail = Voicemail(
            number='42',
            context='super_context',
            name='voicemail name',
        )

        user = User(
            firstname='Johnny',
            lastname='Wilkins',
        )

        get_user.return_value = user
        get_voicemail.return_value = voicemail

        expected_voicemail = Voicemail(
            number='42',
            context='super_context',
            name='voicemail name',
            user=user
        )

        user_association.associate_voicemail(user_id, voicemail_id)

        edit_voicemail.assert_called_once_with(ANY)
        passed_voicemail = edit_voicemail.call_args[0][0]
        self.assertEquals(expected_voicemail, passed_voicemail)
