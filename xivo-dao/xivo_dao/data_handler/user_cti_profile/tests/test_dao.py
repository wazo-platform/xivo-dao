# -*- coding: utf-8 -*-
#
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

from hamcrest import assert_that, equal_to, none

from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_dao.alchemy.callfilter import Callfilter
from xivo_dao.alchemy.callfiltermember import Callfiltermember
from xivo_dao.alchemy.contextinclude import ContextInclude
from xivo_dao.alchemy.cti_profile import CtiProfile as CtiProfileSchema
from xivo_dao.alchemy.ctiphonehintsgroup import CtiPhoneHintsGroup
from xivo_dao.alchemy.ctipresences import CtiPresences
from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.phonefunckey import PhoneFunckey
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.alchemy.rightcallmember import RightCallMember
from xivo_dao.alchemy.sccpdevice import SCCPDevice
from xivo_dao.alchemy.schedulepath import SchedulePath
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.alchemy.usersip import UserSIP
from xivo_dao.data_handler.exception import ElementNotExistsError
from xivo_dao.data_handler.user_cti_profile import dao as user_cti_profile_dao
from xivo_dao.data_handler.user_cti_profile.exceptions import UserCtiProfileNotExistsError
from xivo_dao.data_handler.user_cti_profile.model import UserCtiProfile
from xivo_dao.tests.test_dao import DAOTestCase


class TestUserCtiProfile(DAOTestCase):

    tables = [UserFeatures,
              LineFeatures,
              ContextInclude,
              AgentFeatures,
              CtiPresences,
              CtiPhoneHintsGroup,
              CtiProfileSchema,
              QueueMember,
              RightCallMember,
              Callfiltermember,
              Callfilter,
              Dialaction,
              PhoneFunckey,
              SchedulePath,
              Extension,
              UserLine,
              UserSIP,
              SCCPDevice]

    def setUp(self):
        self.cleanTables()

    def test_associate(self):
        user = self.add_user()
        cti_profile = CtiProfileSchema(id=2, name='Test')
        self.add_me(cti_profile)
        user_cti_profile = UserCtiProfile(user_id=user.id, cti_profile_id=2)

        user_cti_profile_dao.associate(user_cti_profile)

        assert_that(user.cti_profile_id, equal_to(2))

    def test_get_by_userid(self):
        cti_profile = CtiProfileSchema(id=2, name='Test')
        self.add_me(cti_profile)
        user = self.add_user(cti_profile_id=2)

        result = user_cti_profile_dao.get_profile_by_userid(user.id)

        assert_that(result.name, equal_to('Test'))
        assert_that(result.id, equal_to(2))

    def test_get_by_user_id_not_found(self):
        user = self.add_user()
        self.assertRaises(UserCtiProfileNotExistsError, user_cti_profile_dao.get_profile_by_userid, user.id)

    def test_get_by_user_id_no_user(self):
        self.assertRaises(ElementNotExistsError, user_cti_profile_dao.get_profile_by_userid, 123)

    def test_dissociate(self):
        cti_profile = CtiProfileSchema(id=2, name='Test')
        self.add_me(cti_profile)
        user = self.add_user(cti_profile_id=cti_profile.id)
        user_cti_profile = UserCtiProfile(user_id=user.id, cti_profile_id=cti_profile.id)

        user_cti_profile_dao.dissociate(user_cti_profile)

        assert_that(user.cti_profile_id, none())
