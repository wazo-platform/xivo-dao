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
from xivo_dao.notifiers.command.user import abstract


class ConcreteNoDataParams(abstract.AbstractNoDataParams):

    name = 'foobar'


class TestAbstractNoDataParams(unittest.TestCase):

    def test_marshal(self):
        command = ConcreteNoDataParams()

        msg = command.marshal()

        self.assertEqual(msg, None)

    def test_unmarshal(self):
        msg = None

        command = ConcreteNoDataParams.unmarshal(msg)

        self.assertEqual(command.name, ConcreteNoDataParams.name)


class ConcreteAgentIDParams(abstract.AbstractUserIDParams):

    name = 'foo'


class TestAbstractUserIDParams(unittest.TestCase):

    def setUp(self):
        self.user_id = 42
        self.msg = {'user_id': self.user_id}

    def test_marshal(self):
        command = ConcreteAgentIDParams(self.user_id)

        msg = command.marshal()

        self.assertEqual(msg, self.msg)

    def test_unmarshal(self):
        command = ConcreteAgentIDParams.unmarshal(self.msg)

        self.assertEqual(command.name, ConcreteAgentIDParams.name)
        self.assertEqual(command.user_id, self.user_id)

