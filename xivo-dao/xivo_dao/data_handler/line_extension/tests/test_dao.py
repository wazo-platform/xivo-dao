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

from hamcrest import assert_that, equal_to

from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.data_handler.line_extension import dao as line_extension_dao
from xivo_dao.data_handler.line_extension.model import LineExtension

from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_dao.alchemy.callfilter import Callfilter
from xivo_dao.alchemy.callfiltermember import Callfiltermember
from xivo_dao.alchemy.contextinclude import ContextInclude
from xivo_dao.alchemy.cti_profile import CtiProfile
from xivo_dao.alchemy.ctiphonehintsgroup import CtiPhoneHintsGroup
from xivo_dao.alchemy.ctipresences import CtiPresences
from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.extension import Extension as ExtensionSchema
from xivo_dao.alchemy.linefeatures import LineFeatures as LineSchema
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.alchemy.phonefunckey import PhoneFunckey
from xivo_dao.alchemy.rightcallmember import RightCallMember
from xivo_dao.alchemy.schedulepath import SchedulePath
from xivo_dao.alchemy.sccpdevice import SCCPDevice as SCCPDeviceSchema
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.alchemy.usersip import UserSIP as UserSIPSchema
from xivo_dao.alchemy.user_line import UserLine


USER_TABLES = [UserFeatures, LineSchema, ContextInclude, AgentFeatures,
               CtiPresences, CtiPhoneHintsGroup, CtiProfile, QueueMember,
               RightCallMember, Callfiltermember, Callfilter, Dialaction,
               PhoneFunckey, SchedulePath, ExtensionSchema, UserLine, UserSIPSchema,
               SCCPDeviceSchema]

class TestAssociateUserVoicemail(DAOTestCase):

    tables = USER_TABLES

    def setUp(self):
        self.empty_tables()

    def test_associate_main_user(self):
        ule_row = self.prepare_user_and_line()
        extension_row = self.prepare_extension()

        line_extension = LineExtension(line_id=ule_row.line_id,
                                       extension_id=extension_row.id)

        line_extension_dao.associate(line_extension)

        self.assert_extension_is_associated(ule_row, extension_row)

    def test_associate_main_and_secondary_user(self):
        main_ule = self.prepare_user_and_line()
        secondary_ule = self.prepare_secondary_user_and_line(line_id=main_ule.line_id)
        extension_row = self.prepare_extension()

        line_extension = LineExtension(line_id=main_ule.line_id,
                                       extension_id=extension_row.id)

        line_extension_dao.associate(line_extension)

        self.assert_extension_is_associated(main_ule, extension_row)
        self.assert_extension_is_associated(secondary_ule, extension_row)

    def prepare_user_and_line(self):
        ule_row = self.add_user_line_without_exten(main_user=True,
                                                    main_line=True)
        return ule_row

    def prepare_secondary_user_and_line(self, line_id):
        user_row = self.add_user()
        ule_row = self.add_user_line(user_id=user_row.id,
                                     line_id=line_id,
                                     extension_id=None,
                                     main_user=False,
                                     main_line=True)
        return ule_row

    def prepare_extension(self):
        extension_row = self.add_extension()
        return extension_row

    def assert_extension_is_associated(self, ule_row, extension_row):
        updated_ule = (self.session.query(UserLine)
                       .filter(UserLine.id == ule_row.id)
                       .filter(UserLine.user_id == ule_row.user_id)
                       .filter(UserLine.line_id == ule_row.line_id)
                       .first())
        assert_that(updated_ule.extension_id, equal_to(extension_row.id))
