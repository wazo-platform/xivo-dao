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
from xivo_dao.data_handler.user import association as user_association
from xivo_dao.data_handler.voicemail.model import Voicemail
from xivo_dao.data_handler.user.model import User
from xivo_dao.data_handler.exception import ElementNotExistsError, \
    ElementCreationError
from xivo_dao.data_handler.line.model import LineSIP
from xivo_dao.data_handler.extension.model import Extension
from xivo_dao.data_handler.user_line_extension.model import UserLineExtension


class TestUserAssociation(unittest.TestCase):

    @patch('xivo_dao.data_handler.voicemail.services.get')
    @patch('xivo_dao.data_handler.user.services.get')
    def test_associate_voicemail_when_user_inexistant(self, get_user, get_voicemail):
        user_id = 21
        voicemail_id = 32

        get_user.side_effect = ElementNotExistsError('voicemail')
        get_voicemail.return_value = Mock()

        self.assertRaises(ElementNotExistsError, user_association.associate_voicemail, user_id, voicemail_id)

    @patch('xivo_dao.data_handler.voicemail.services.get')
    @patch('xivo_dao.data_handler.user.services.get')
    def test_associate_voicemail_when_voicemail_inexistant(self, get_user, get_voicemail):
        user_id = 21
        voicemail_id = 32

        get_user.return_value = Mock()
        get_voicemail.side_effect = ElementNotExistsError('voicemail')

        self.assertRaises(ElementNotExistsError, user_association.associate_voicemail, user_id, voicemail_id)

    @patch('xivo_dao.data_handler.voicemail.services.get')
    @patch('xivo_dao.data_handler.user.services.edit')
    @patch('xivo_dao.data_handler.user.services.get')
    def test_associate_voicemail(self, get_user, edit_user, get_voicemail):
        user_id = 21
        voicemail_id = 32

        voicemail = Voicemail(
            id=voicemail_id,
            number='42',
            context='super_context',
            name='Johnny Wilkins',
        )

        user = User(
            id=user_id,
            firstname='Johnny',
            lastname='Wilkins',
        )

        get_user.return_value = user
        get_voicemail.return_value = voicemail

        user_association.associate_voicemail(user_id, voicemail_id)

        edit_user.assert_called_once_with(ANY)
        self.assertEquals(user.voicemail_id, voicemail_id)
