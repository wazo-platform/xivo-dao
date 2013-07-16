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
from xivo_dao.data_handler.extension import command


class ConcreteExtensionIDParams(command.AbstractExtensionIDParams):

    name = 'foo'

ID = 42
EXTEN = '1001'
CONTEXT = 'default'


class TestAbstractExtensionIDParams(unittest.TestCase):

    def setUp(self):
        self.msg = {
            'id': ID,
            'exten': EXTEN,
            'context': CONTEXT
        }

    def test_marshal(self):
        command = ConcreteExtensionIDParams(ID, EXTEN, CONTEXT)

        msg = command.marshal()

        self.assertEqual(msg, self.msg)

    def test_unmarshal(self):
        command = ConcreteExtensionIDParams.unmarshal(self.msg)

        self.assertEqual(command.name, ConcreteExtensionIDParams.name)
        self.assertEqual(command.id, ID)
        self.assertEqual(command.exten, EXTEN)
        self.assertEqual(command.context, CONTEXT)
