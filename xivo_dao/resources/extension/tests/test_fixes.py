# -*- coding: UTF-8 -*-

# Copyright (C) 2015-2016 Avencall
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

from xivo_dao.alchemy.linefeatures import LineFeatures as Line
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.incall import Incall
from xivo_dao.tests.test_dao import DAOTestCase

from xivo_dao.resources.extension.fixes import ExtensionFixes


class TestExtensionFixes(DAOTestCase):

    def setUp(self):
        super(TestExtensionFixes, self).setUp()
        self.fixes = ExtensionFixes(self.session)

    def test_given_extension_associated_to_nothing_then_fixes_pass(self):
        extension = self.add_extension(exten="1000", context="default")
        self.fixes.fix(extension.id)

    def test_given_extension_associated_to_line_then_number_and_context_updated(self):
        line = self.add_line(context="mycontext", number="2000")
        extension = self.add_extension(exten="1000", context="default")
        self.add_line_extension(line_id=line.id, extension_id=extension.id)

        self.fixes.fix(extension.id)

        line = self.session.query(Line).first()
        assert_that(line.number, equal_to('1000'))
        assert_that(line.context, equal_to('default'))

    def test_given_user_has_extension_then_destination_updated(self):
        extension = self.add_extension()
        line = self.add_line()
        user = self.add_user()
        self.add_user_line(user_id=user.id, line_id=line.id)
        self.add_line_extension(line_id=line.id, extension_id=extension.id)

        self.fixes.fix(extension.id)

        extension = self.session.query(Extension).first()
        assert_that(extension.type, equal_to('user'))
        assert_that(extension.typeval, equal_to(str(user.id)))

    def test_given_line_has_multiple_users_then_main_extension_updated(self):
        extension = self.add_extension()
        line = self.add_line()
        main_user = self.add_user()
        other_user = self.add_user()
        self.add_line_extension(line_id=line.id, extension_id=extension.id)
        self.add_user_line(user_id=main_user.id, line_id=line.id,
                           main_user=True, main_line=True)
        self.add_user_line(user_id=other_user.id, line_id=line.id,
                           main_user=False, main_line=True)

        self.fixes.fix(extension.id)

        extension = self.session.query(Extension).first()
        assert_that(extension.type, equal_to('user'))
        assert_that(extension.typeval, equal_to(str(main_user.id)))

    def test_given_user_has_multiple_lines_then_all_extensions_updated(self):
        extension1 = self.add_extension(exten='1800')
        extension2 = self.add_extension(exten='1801')
        line1 = self.add_line()
        line2 = self.add_line()
        user = self.add_user()
        self.add_user_line(user_id=user.id, line_id=line1.id,
                           main_user=True, main_line=True)
        self.add_user_line(user_id=user.id, line_id=line2.id,
                           main_user=True, main_line=False)
        self.add_line_extension(line_id=line1.id, extension_id=extension1.id,
                                main_extension=True)
        self.add_line_extension(line_id=line2.id, extension_id=extension2.id,
                                main_extension=True)

        self.fixes.fix(extension1.id)
        self.fixes.fix(extension2.id)

        extension = self.session.query(Extension).filter(Extension.exten == extension1.exten).first()
        assert_that(extension.type, equal_to('user'))
        assert_that(extension.typeval, equal_to(str(user.id)))

        extension = self.session.query(Extension).filter(Extension.exten == extension2.exten).first()
        assert_that(extension.type, equal_to('user'))
        assert_that(extension.typeval, equal_to(str(user.id)))

    def test_given_extension_is_not_associated_to_user_then_destination_reset(self):
        extension = self.add_extension(exten="1000", context="default",
                                       type="user", typeval="1234")

        self.fixes.fix(extension.id)

        extension = self.session.query(Extension).first()
        assert_that(extension.type, equal_to('user'))
        assert_that(extension.typeval, equal_to('0'))

    def test_given_extension_is_not_associated_to_incall_then_destination_reset(self):
        extension = self.add_extension(exten="1000", context="from-extern",
                                       type="incall", typeval="1234")

        self.fixes.fix(extension.id)
        extension = self.session.query(Extension).first()
        assert_that(extension.type, equal_to('user'))
        assert_that(extension.typeval, equal_to('0'))

    def test_given_extension_destination_is_other_than_user_or_incall_then_destination_is_unchanged(self):
        extension = self.add_extension(exten="1000", context="default",
                                       type="queue", typeval="1234")

        self.fixes.fix(extension.id)

        extension = self.session.query(Extension).first()
        assert_that(extension.type, equal_to('queue'))
        assert_that(extension.typeval, equal_to('1234'))

    def test_given_extension_destination_is_incall_then_incall_updated(self):
        incall = self.add_incall(exten="1000", context="other-extern")
        extension = self.add_extension(exten="1001", context="from-extern",
                                       type="incall", typeval=str(incall.id))
        self.add_dialaction(event='answer',
                            category='incall',
                            categoryval=str(incall.id),
                            action='user',
                            actionarg1='1234')

        self.fixes.fix(extension.id)

        incall = self.session.query(Incall).first()
        assert_that(incall.exten, equal_to('1001'))
        assert_that(incall.context, equal_to('from-extern'))
