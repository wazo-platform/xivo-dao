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
from xivo_dao.data_handler.line import command


class ConcreteLineIDParams(command.AbstractLineIDParams):

    name = 'foo'


class TestAbstractLineIDParams(unittest.TestCase):

    def setUp(self):
        self.id = 42
        self.msg = {'id': self.id}

    def test_marshal(self):
        command = ConcreteLineIDParams(self.id)

        msg = command.marshal()

        self.assertEqual(msg, self.msg)

    def test_unmarshal(self):
        command = ConcreteLineIDParams.unmarshal(self.msg)

        self.assertEqual(command.name, ConcreteLineIDParams.name)
        self.assertEqual(command.id, self.id)
