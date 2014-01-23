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
from mock import patch
from xivo_dao.data_handler.cti_profile.model import CtiProfile
from hamcrest.core.core.issame import same_instance
from xivo_dao.data_handler.cti_profile import services
from hamcrest.core import assert_that


class TestCtiProfileServices(unittest.TestCase):
    @patch('xivo_dao.data_handler.cti_profile.dao.find_all')
    def test_find_all(self, profile_dao_find_all):
        profile1 = CtiProfile()
        profile2 = CtiProfile()
        profile_dao_find_all.return_value = [profile1, profile2]

        [res1, res2] = services.find_all()

        assert_that(res1, same_instance(profile1))
        assert_that(res2, same_instance(profile2))

    @patch('xivo_dao.data_handler.cti_profile.dao.get')
    def test_get(self, profile_dao_get):
        profile = CtiProfile()
        profile_dao_get.return_value = profile

        result = services.get(1)

        assert_that(result, same_instance(profile))
        profile_dao_get.assert_called_with(1)
