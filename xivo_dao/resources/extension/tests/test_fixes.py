# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
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
from xivo_dao.tests.test_dao import DAOTestCase

from xivo_dao.resources.extension.fixes import ExtensionFixes


class TestExtensionFixes(DAOTestCase):

    def setUp(self):
        super(TestExtensionFixes, self).setUp()
        self.fixes = ExtensionFixes(self.session)

    def test_given_extension_associated_to_nothing_then_fixes_pass(self):
        extension = self.add_extension(exten="1000", context="default")
        self.fixes.fix_extension(extension.id)

    def test_given_extension_associated_to_line_then_number_and_context_updated(self):
        line = self.add_line(context="mycontext", number="2000")
        extension = self.add_extension(exten="1000", context="default")
        self.add_user_line(user_id=None, line_id=line.id, extension_id=extension.id)

        self.fixes.fix_extension(extension.id)

        line = self.session.query(Line).first()
        assert_that(line.number, equal_to('1000'))
        assert_that(line.context, equal_to('default'))
