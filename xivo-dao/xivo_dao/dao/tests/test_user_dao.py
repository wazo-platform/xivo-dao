# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 Avencall
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

from hamcrest import assert_that
from hamcrest.core import equal_to
from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_dao.alchemy.callfilter import Callfilter
from xivo_dao.alchemy.callfiltermember import Callfiltermember
from xivo_dao.alchemy.contextinclude import ContextInclude
from xivo_dao.alchemy.contextnummember import ContextNumMember
from xivo_dao.alchemy.cti_profile import CtiProfile
from xivo_dao.alchemy.ctiphonehintsgroup import CtiPhoneHintsGroup
from xivo_dao.alchemy.ctipresences import CtiPresences
from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.linefeatures import LineFeatures as LineSchema
from xivo_dao.alchemy.phonefunckey import PhoneFunckey
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.alchemy.rightcallmember import RightCallMember
from xivo_dao.alchemy.schedulepath import SchedulePath
from xivo_dao.alchemy.userfeatures import UserFeatures as UserSchema
from xivo_dao.dao import user_dao
from xivo_dao.tests.test_dao import DAOTestCase


class TestUserDAO(DAOTestCase):

    tables = [
        AgentFeatures,
        Callfilter,
        Callfiltermember,
        ContextInclude,
        ContextNumMember,
        CtiPhoneHintsGroup,
        CtiPresences,
        CtiProfile,
        Dialaction,
        LineSchema,
        PhoneFunckey,
        QueueMember,
        RightCallMember,
        SchedulePath,
        UserSchema,
    ]

    def setUp(self):
        self.empty_tables()

    def test_get_user_by_id_inexistant(self):
        self.assertRaises(LookupError, user_dao.get_user_by_id, 42)

    def test_get_user_by_id(self):
        user_id = self._insert_user()

        user = user_dao.get_user_by_id(user_id)

        assert_that(user.id, equal_to(user_id))

    def _insert_user(self):
        properties = {
            'firstname': 'Paul',
        }
        user = UserSchema(**properties)
        self.add_me(user)
        return user.id
