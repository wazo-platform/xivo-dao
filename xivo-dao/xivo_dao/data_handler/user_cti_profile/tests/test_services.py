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

from hamcrest.core import assert_that
from hamcrest.core.core.isequal import equal_to
from mock import patch, Mock
import unittest

from xivo_dao.data_handler.user_cti_profile import services as user_cti_profile_services
from xivo_dao.data_handler.user_cti_profile.model import UserCtiProfile


class TestUserCtiProfile(unittest.TestCase):

    @patch('xivo_dao.data_handler.user_cti_profile.validator.validate_association')
    @patch('xivo_dao.data_handler.user_cti_profile.dao.associate')
    def test_associate(self, dao_associate, validate_association):
        user_cti_profile = Mock(UserCtiProfile)

        result = user_cti_profile_services.associate(user_cti_profile)

        assert_that(result, equal_to(user_cti_profile))
        validate_association.assert_called_once_with(user_cti_profile)
        dao_associate.assert_called_once_with(user_cti_profile)
