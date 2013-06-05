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
from xivo_dao.alchemy.extenumber import ExteNumber
from xivo_dao.alchemy.linefeatures import LineFeatures as LineSchema
from xivo_dao.alchemy.phonefunckey import PhoneFunckey
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.alchemy.rightcallmember import RightCallMember
from xivo_dao.alchemy.schedulepath import SchedulePath
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.userfeatures import UserFeatures as UserSchema
from xivo_dao.dao import line_dao
from xivo_dao.tests.test_dao import DAOTestCase


class TestGetLineDao(DAOTestCase):

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
        ExteNumber,
        LineSchema,
        PhoneFunckey,
        QueueMember,
        RightCallMember,
        SchedulePath,
        UserSchema,
        UserLine,
    ]

    def setUp(self):
        self.empty_tables()

    def test_get_by_user_id_no_line(self):
        self.assertRaises(LookupError, line_dao.get_line_by_user_id, 666)

    def test_get_by_user_id(self):
        line_name = 'sdklfj'

        line_id = self.add_line(name=line_name)
        user_id = self.add_user()
        self.add_user_line(user_id=user_id, line_id=line_id)

        line = line_dao.get_line_by_user_id(user_id)

        assert_that(line.name, equal_to(line_name))

    def test_get_by_user_id_commented(self):
        line_name = 'sdklfj'

        line_id = self.add_line(name=line_name, commented=1)
        user_id = self.add_user()
        self.add_user_line(user_id=user_id, line_id=line_id)

        self.assertRaises(LookupError, line_dao.get_line_by_user_id, user_id)

    def test_get_by_number_context_no_line(self):
        self.assertRaises(LookupError, line_dao.get_line_by_number_context, '1234', 'default')

    def test_get_by_number_context(self):
        line_name = 'sdklfj'
        number = '1235'
        context = 'notdefault'

        line_id = self.add_line(name=line_name)
        self.add_extenumber(exten=number, context=context, type='user', typeval=str(line_id))

        line = line_dao.get_line_by_number_context(number, context)

        assert_that(line.name, equal_to(line_name))

    def test_get_by_number_context_commented(self):
        line_name = 'sdklfj'
        number = '1235'
        context = 'notdefault'

        line_id = self.add_line(name=line_name, commented=1)
        self.add_extenumber(exten=number, context=context, type='user', typeval=str(line_id))

        self.assertRaises(LookupError, line_dao.get_line_by_number_context, number, context)
