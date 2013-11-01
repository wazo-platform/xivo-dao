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

from hamcrest import assert_that, has_length, all_of, has_property, instance_of, contains

from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_dao.alchemy.callfilter import Callfilter
from xivo_dao.alchemy.callfiltermember import Callfiltermember
from xivo_dao.alchemy.contextinclude import ContextInclude
from xivo_dao.alchemy.cti_profile import CtiProfile
from xivo_dao.alchemy.ctiphonehintsgroup import CtiPhoneHintsGroup
from xivo_dao.alchemy.ctipresences import CtiPresences
from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.extension import Extension as ExtensionSchema
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.alchemy.phonefunckey import PhoneFunckey
from xivo_dao.alchemy.rightcallmember import RightCallMember
from xivo_dao.alchemy.schedulepath import SchedulePath
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.voicemail import Voicemail as VoicemailSchema

from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.data_handler.user_voicemail import dao as user_voicemail_dao
from xivo_dao.data_handler.user_voicemail.model import UserVoicemail


USER_TABLES = [UserFeatures, LineFeatures, ContextInclude, AgentFeatures,
               CtiPresences, CtiPhoneHintsGroup, CtiProfile, QueueMember,
               RightCallMember, Callfiltermember, Callfilter, Dialaction,
               PhoneFunckey, SchedulePath, ExtensionSchema, UserLine]


class TestCase(DAOTestCase):

    tables = USER_TABLES + [
        VoicemailSchema,
        LineFeatures
    ]

    def setUp(self):
        self.empty_tables()

    def test_find_all_by_user_id_no_users_or_voicemail(self):
        result = user_voicemail_dao.find_all_by_user_id(1)

        assert_that(result, has_length(0))

    def test_find_all_by_user_id_with_user_without_line_or_voicemail(self):
        user_row = self.add_user(firstname='King')

        result = user_voicemail_dao.find_all_by_user_id(user_row.id)

        assert_that(result, has_length(0))

    def test_find_all_by_user_id_with_user_without_voicemail(self):
        user_row = self.add_user_line_with_exten(firstname='King', exten='1000', context='default')

        result = user_voicemail_dao.find_all_by_user_id(user_row.id)

        assert_that(result, has_length(0))

    def test_find_all_by_user_id_with_voicemail(self):
        user_row, voicemail_row = self.create_user_and_voicemail(firstname='King', exten='1000', context='default')

        result = user_voicemail_dao.find_all_by_user_id(user_row.id)

        assert_that(result, contains(all_of(
            instance_of(UserVoicemail),
            has_property('user_id', user_row.id),
            has_property('voicemail_id', voicemail_row.uniqueid)
        )))

    def create_user_and_voicemail(self, firstname, exten, context):
        user_line_row = self.add_user_line_with_exten(firstname='King', exten='1000', context='default')
        user_row = self.session.query(UserFeatures).get(user_line_row.user_id)
        voicemail_row = self.add_voicemail('1000', 'default')
        self.link_user_and_voicemail(user_row, voicemail_row.uniqueid)
        return user_row, voicemail_row