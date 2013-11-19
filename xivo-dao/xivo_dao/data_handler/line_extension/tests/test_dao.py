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

from hamcrest import assert_that, equal_to, all_of, has_property

from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.data_handler.line_extension import dao
from xivo_dao.data_handler.line_extension.model import LineExtension
from xivo_dao.data_handler.line_extension.exception import LineExtensionNotExistsError
from xivo_dao.data_handler.exception import ElementNotExistsError

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


class TestLineExtensionDAO(DAOTestCase):

    tables = USER_TABLES

    def setUp(self):
        self.empty_tables()


class TestAssociateLineExtension(TestLineExtensionDAO):

    def test_associate_main_user(self):
        ule_row = self.prepare_user_and_line()
        extension_row = self.prepare_extension()

        line_extension = LineExtension(line_id=ule_row.line_id,
                                       extension_id=extension_row.id)

        dao.associate(line_extension)

        self.assert_extension_is_associated(ule_row, extension_row)

    def test_associate_main_and_secondary_user(self):
        main_ule = self.prepare_user_and_line()
        secondary_ule = self.prepare_secondary_user_and_line(line_id=main_ule.line_id)
        extension_row = self.prepare_extension()

        line_extension = LineExtension(line_id=main_ule.line_id,
                                       extension_id=extension_row.id)

        dao.associate(line_extension)

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


class TestGetByLineId(TestLineExtensionDAO):

    def test_get_by_line_id_no_line(self):
        self.assertRaises(ElementNotExistsError, dao.get_by_line_id, 1)

    def test_get_by_line_id_no_extension(self):
        user_line_row = self.prepare_user_line_without_extension()

        self.assertRaises(LineExtensionNotExistsError, dao.get_by_line_id, user_line_row.line_id)

    def test_get_by_line_id_with_extension(self):
        user_line_row = self.prepare_user_line_with_extension()

        line_extension = dao.get_by_line_id(user_line_row.line_id)

        assert_that(line_extension, all_of(
            has_property('line_id', user_line_row.line_id),
            has_property('extension_id', user_line_row.extension_id)))

    def test_get_by_line_id_with_multiple_users(self):
        user_line_row_1 = self.prepare_user_line_with_extension()
        user_row = self.add_user()
        user_line_row_2 = self.associate_secondary_user(user_line_row_1, user_row)

        line_extension = dao.get_by_line_id(user_line_row_2.line_id)

        assert_that(line_extension, all_of(
            has_property('line_id', user_line_row_1.line_id),
            has_property('extension_id', user_line_row_1.extension_id)))

    def prepare_user_line_without_extension(self):
        user_line_row = self.add_user_line_without_exten()
        return user_line_row

    def prepare_user_line_with_extension(self):
        user_line_row = self.add_user_line_with_exten()
        return user_line_row

    def associate_secondary_user(self, user_line_row, user_row):
        user_line_row = self.add_user_line(user_id=user_row.id,
                                           line_id=user_line_row.line_id,
                                           extension_id=user_line_row.extension_id,
                                           main_user=False,
                                           main_line=True)
        return user_line_row
