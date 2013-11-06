# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import unittest

from mock import patch, Mock

from xivo_dao.data_handler.exception import NonexistentParametersError, ElementNotExistsError
from xivo_dao.data_handler.exception import MissingParametersError
from xivo_dao.data_handler.exception import InvalidParametersError
from xivo_dao.data_handler.user_voicemail.model import UserVoicemail
from xivo_dao.data_handler.user_line_extension.model import UserLineExtension
from xivo_dao.data_handler.user_voicemail import validator


class TestValidator(unittest.TestCase):

    def test_validate_association_missing_parameters(self):
        user_voicemail = UserVoicemail()

        self.assertRaises(MissingParametersError, validator.validate_association, user_voicemail)

    def test_validate_association_wrong_parameter_type_for_enabled(self):
        user_voicemail = UserVoicemail(user_id=1, voicemail_id=2, enabled=1)

        self.assertRaises(InvalidParametersError, validator.validate_association, user_voicemail)

    @patch('xivo_dao.data_handler.user.dao.get')
    def test_validate_association_when_user_does_not_exist(self, user_get):
        user_voicemail = UserVoicemail(user_id=1, voicemail_id=2)

        user_get.side_effect = ElementNotExistsError('user', id=user_voicemail.user_id)
        self.assertRaises(NonexistentParametersError, validator.validate_association, user_voicemail)
        user_get.assert_called_once_with(user_voicemail.user_id)

    @patch('xivo_dao.data_handler.user.dao.get')
    @patch('xivo_dao.data_handler.voicemail.dao.get')
    def test_validate_association_when_voicemail_does_not_exist(self, voicemail_get, user_get):
        user_voicemail = UserVoicemail(user_id=1, voicemail_id=2)

        voicemail_get.side_effect = ElementNotExistsError('voicemail', id=user_voicemail.voicemail_id)
        self.assertRaises(NonexistentParametersError, validator.validate_association, user_voicemail)
        voicemail_get.assert_called_once_with(user_voicemail.voicemail_id)

    @patch('xivo_dao.data_handler.user.dao.get')
    @patch('xivo_dao.data_handler.voicemail.dao.get')
    @patch('xivo_dao.data_handler.user_line_extension.dao.find_all_by_user_id')
    def test_validate_association_voicemail_when_user_has_no_line(self, ule_find_all_by_user_id, voicemail_get, user_get):
        user_voicemail = UserVoicemail(user_id=1, voicemail_id=2)

        ule_find_all_by_user_id.return_value = []

        self.assertRaises(InvalidParametersError, validator.validate_association, user_voicemail)
        ule_find_all_by_user_id.assert_called_once_with(user_voicemail.user_id)

    @patch('xivo_dao.data_handler.user.dao.get')
    @patch('xivo_dao.data_handler.voicemail.dao.get')
    @patch('xivo_dao.data_handler.user_line_extension.dao.find_all_by_user_id')
    @patch('xivo_dao.data_handler.user_voicemail.dao.get_by_user_id')
    def test_validate_association_voicemail_when_user_already_has_a_voicemail(self,
                                                                              voicemail_get_by_user_id,
                                                                              ule_find_all_by_user_id,
                                                                              voicemail_get,
                                                                              user_get):
        user_voicemail = UserVoicemail(user_id=1, voicemail_id=2)

        ule_find_all_by_user_id.return_value = [Mock(UserLineExtension)]
        voicemail_get_by_user_id.side_effect = Mock(UserVoicemail)

        self.assertRaises(InvalidParametersError, validator.validate_association, user_voicemail)
        voicemail_get_by_user_id.assert_called_once_with(user_voicemail.user_id)
        ule_find_all_by_user_id.assert_called_once_with(user_voicemail.user_id)

    @patch('xivo_dao.data_handler.user.dao.get')
    @patch('xivo_dao.data_handler.voicemail.dao.get')
    @patch('xivo_dao.data_handler.user_line_extension.dao.find_all_by_user_id')
    @patch('xivo_dao.data_handler.user_voicemail.dao.get_by_user_id')
    def test_validate_association(self,
                                  voicemail_get_by_user_id,
                                  ule_find_all_by_user_id,
                                  voicemail_get,
                                  user_get):
        user_voicemail = UserVoicemail(user_id=1, voicemail_id=2)

        ule_find_all_by_user_id.return_value = [Mock(UserLineExtension)]
        voicemail_get_by_user_id.side_effect = ElementNotExistsError('user_voicemail',
                                                                     user_id=user_voicemail.user_id)

        validator.validate_association(user_voicemail)
        user_get.assert_called_once_with(user_voicemail.user_id)
        voicemail_get.assert_called_once_with(user_voicemail.voicemail_id)
        ule_find_all_by_user_id.assert_called_once_with(user_voicemail.user_id)
        voicemail_get_by_user_id.assert_called_once_with(user_voicemail.user_id)
