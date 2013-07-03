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
from xivo_dao.data_handler.device import command


class ConcreteDeviceIDParams(command.AbstractDeviceIDParams):

    name = 'foo'


class TestAbstractDeviceIDParams(unittest.TestCase):

    def setUp(self):
        self.id = 42
        self.deviceid = 24
        self.msg = {
            'id': self.id,
            'deviceid': self.deviceid
        }

    def test_marshal(self):
        command = ConcreteDeviceIDParams(self.id, self.deviceid)

        msg = command.marshal()

        self.assertEqual(msg, self.msg)

    def test_unmarshal(self):
        command = ConcreteDeviceIDParams.unmarshal(self.msg)

        self.assertEqual(command.name, ConcreteDeviceIDParams.name)
        self.assertEqual(command.id, self.id)
        self.assertEqual(command.deviceid, self.deviceid)
