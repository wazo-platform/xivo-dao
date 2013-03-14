# -*- coding: UTF-8 -*-
#
# Copyright (C) 2012  Avencall
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

import unittest
from xivo_dao.helpers import object_mapping


class TestObjectMapping(unittest.TestCase):

    def test_map_object(self):
        class MySampleClass:
            pass

        class YourSampleClass:
            pass

        object_from = MySampleClass()
        object_from.prop1_my = 'value1'
        object_from.prop2_my = 2
        object_to = YourSampleClass()
        mapping = {'prop0_my': 'unused',
                   'prop1_my': 'prop1_your',
                   'prop2_my': 'prop2_your'}

        default_values = {'prop2_your': 3,
                          'prop3_your': None,
                          'prop4_your': "c'est vache"
                          }
        object_mapping.map_attributes(object_from, object_to, mapping, default_values)
        self.assertEquals(object_from.prop1_my, object_to.prop1_your)
        self.assertEquals(object_from.prop2_my, object_to.prop2_your)
        self.assertEquals(object_to.prop3_your, None)
        self.assertEquals(object_to.prop4_your, "c'est vache")



