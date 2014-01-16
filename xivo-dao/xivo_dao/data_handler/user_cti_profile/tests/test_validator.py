# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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
from xivo_dao.data_handler.exception import MissingParametersError, \
    ElementNotExistsError, NonexistentParametersError, InvalidParametersError

from xivo_dao.data_handler.user_cti_profile import validator
from xivo_dao.data_handler.user_cti_profile.model import UserCtiProfile
from mock import patch


class TestUserCtiProfileValidator(unittest.TestCase):

    @patch('xivo_dao.data_handler.cti_profile.dao.get')
    @patch('xivo_dao.data_handler.user.dao.get')
    @patch('xivo_dao.data_handler.user_cti_profile.dao.get_profile_by_userid')
    def test_validate_missing_params(self, patch_get_profile_by_userid, patch_get_user, patch_get_profile):
        association = UserCtiProfile(user_id=1)
        self.assertRaises(MissingParametersError, validator.validate_association, association)

        association = UserCtiProfile(cti_profile_id=1)
        self.assertRaises(MissingParametersError, validator.validate_association, association)

    @patch('xivo_dao.data_handler.cti_profile.dao.get')
    @patch('xivo_dao.data_handler.user.dao.get')
    @patch('xivo_dao.data_handler.user_cti_profile.dao.get_profile_by_userid')
    def test_validate_unexisting_cti_profile(self, patch_get_profile_by_userid, patch_get_user, patch_get_profile):
        association = UserCtiProfile(user_id=1, cti_profile_id=2)
        patch_get_profile.side_effect = ElementNotExistsError('voicemail')

        self.assertRaises(NonexistentParametersError, validator.validate_association, association)
        patch_get_profile.assert_called_with(association.cti_profile_id)

    @patch('xivo_dao.data_handler.cti_profile.dao.get')
    @patch('xivo_dao.data_handler.user.dao.get')
    @patch('xivo_dao.data_handler.user_cti_profile.dao.get_profile_by_userid')
    def test_validate_unexisting_user(self, patch_get_profile_by_userid, patch_get_user, patch_get_profile):
        association = UserCtiProfile(user_id=1, cti_profile_id=2)
        patch_get_user.side_effect = ElementNotExistsError('user')

        self.assertRaises(NonexistentParametersError, validator.validate_association, association)
        patch_get_user.assert_called_with(association.user_id)

    @patch('xivo_dao.data_handler.cti_profile.dao.get')
    @patch('xivo_dao.data_handler.user.dao.get')
    @patch('xivo_dao.data_handler.user_cti_profile.dao.get_profile_by_userid')
    def test_validate_user_already_has_profile(self, patch_get_profile_by_userid, patch_get_user, patch_get_profile):
        association = UserCtiProfile(user_id=1, cti_profile_id=2)

        self.assertRaises(InvalidParametersError, validator.validate_association, association)
        patch_get_profile_by_userid.assert_called_with(association.user_id)
