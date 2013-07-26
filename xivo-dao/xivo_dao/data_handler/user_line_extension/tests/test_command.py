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

from __future__ import unicode_literals

import unittest
from .. import command


class ConcreteUserLineExtensionIDParams(command.AbstractUserLineExtensionIDParams):

    name = 'foo'

ID = 4221
USER_ID = 4321
LINE_ID = 9213
EXTENSION_ID = 54365
MAIN_USER = True
MAIN_LINE = True


class TestAbstractUserLineExtensionIDParams(unittest.TestCase):

    def setUp(self):
        self.msg = {
            'id': ID,
            'user_id': USER_ID,
            'line_id': LINE_ID,
            'extension_id': EXTENSION_ID,
            'main_user': MAIN_USER,
            'main_line': MAIN_LINE
        }

    def test_marshal(self):
        command = ConcreteUserLineExtensionIDParams(ID, USER_ID, LINE_ID, EXTENSION_ID, MAIN_USER, MAIN_LINE)

        msg = command.marshal()

        self.assertEqual(msg, self.msg)

    def test_unmarshal(self):
        command = ConcreteUserLineExtensionIDParams.unmarshal(self.msg)

        self.assertEqual(command.name, ConcreteUserLineExtensionIDParams.name)
        self.assertEqual(command.id, ID)
        self.assertEqual(command.user_id, USER_ID)
        self.assertEqual(command.line_id, LINE_ID)
        self.assertEqual(command.extension_id, EXTENSION_ID)
        self.assertEqual(command.main_user, MAIN_USER)
        self.assertEqual(command.main_line, MAIN_LINE)
