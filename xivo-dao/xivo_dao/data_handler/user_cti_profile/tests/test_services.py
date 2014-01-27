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

from hamcrest import assert_that, equal_to
from mock import patch, Mock

from xivo_dao.data_handler.user_cti_profile import services as user_cti_profile_services
from xivo_dao.data_handler.user_cti_profile.model import UserCtiProfile
from xivo_dao.data_handler.cti_profile.model import CtiProfile
from xivo_dao.data_handler.exception import ElementNotExistsError
from xivo_dao.data_handler.user_cti_profile.exceptions import UserCtiProfileNotExistsError


class TestUserCtiProfile(unittest.TestCase):

    @patch('xivo_dao.data_handler.user_cti_profile.validator.validate_association')
    @patch('xivo_dao.data_handler.user_cti_profile.dao.associate')
    @patch('xivo_dao.data_handler.user_cti_profile.notifier.associated')
    def test_associate(self, notifier_associated, dao_associate, validate_association):
        user_cti_profile = Mock(UserCtiProfile)

        result = user_cti_profile_services.associate(user_cti_profile)

        assert_that(result, equal_to(user_cti_profile))
        validate_association.assert_called_once_with(user_cti_profile)
        dao_associate.assert_called_once_with(user_cti_profile)
        notifier_associated.assert_called_with(user_cti_profile)

    @patch('xivo_dao.data_handler.user.dao.is_cti_enabled')
    @patch('xivo_dao.data_handler.user_cti_profile.dao.find_profile_by_userid')
    def test_get(self, dao_find_profile_by_userid, dao_is_cti_enabled):
        userid = 1
        cti_profile = CtiProfile(id=2)
        dao_find_profile_by_userid.return_value = cti_profile
        dao_is_cti_enabled.return_value = True

        result = user_cti_profile_services.get(userid)

        assert_that(result.user_id, equal_to(userid))
        assert_that(result.cti_profile_id, equal_to(cti_profile.id))
        self.assertTrue(result.enabled)
        dao_is_cti_enabled.assert_called_with(userid)

    @patch('xivo_dao.data_handler.user_cti_profile.dao.find_profile_by_userid')
    def test_get_not_found(self, dao_find_profile_by_userid):
        userid = 1
        dao_find_profile_by_userid.return_value = None

        self.assertRaises(UserCtiProfileNotExistsError, user_cti_profile_services.get, userid)

    @patch('xivo_dao.data_handler.user_cti_profile.validator.validate_dissociation')
    @patch('xivo_dao.data_handler.user_cti_profile.dao.dissociate')
    @patch('xivo_dao.data_handler.user_cti_profile.notifier.dissociated')
    def test_dissociate(self, notifier_dissociated, dao_dissociate, validate_dissociation):
        user_cti_profile = Mock(UserCtiProfile)

        user_cti_profile_services.dissociate(user_cti_profile)

        validate_dissociation.assert_called_once_with(user_cti_profile)
        dao_dissociate.assert_called_once_with(user_cti_profile)
        notifier_dissociated.assert_called_with(user_cti_profile)

    @patch('xivo_dao.data_handler.user_cti_profile.validator.validate_edit')
    @patch('xivo_dao.data_handler.user_cti_profile.dao.edit')
    @patch('xivo_dao.data_handler.user_cti_profile.notifier.edited')
    def test_edit(self, notifier_edited, dao_edit, validate_edit):
        user_cti_profile = Mock(UserCtiProfile)

        user_cti_profile_services.edit(user_cti_profile)

        validate_edit.assert_called_once_with(user_cti_profile)
        dao_edit.assert_called_once_with(user_cti_profile)
        notifier_edited.assert_called_with(user_cti_profile)
