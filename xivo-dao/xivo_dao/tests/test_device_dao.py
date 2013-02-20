# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 Avencall
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

from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.alchemy.devicefeatures import DeviceFeatures
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao import device_dao


class TestDeviceDAO(DAOTestCase):

    tables = [DeviceFeatures, LineFeatures]

    def setUp(self):
        self.empty_tables()

    def test_get_vendor_model_cisco(self):
        device = DeviceFeatures()
        device.deviceid = 'sdfjhdf83498erw8'
        device.config = '893247987djfkh'
        device.mac = '00:14:7f:e1:37:62'
        device.vendor = 'Cisco'
        device.model = 'abcde'
        device.proto = 'sip'

        self.session.begin()
        self.session.add(device)
        self.session.commit()

        vendor, model = device_dao.get_vendor_model(device.id)

        self.assertEqual(vendor, device.vendor)
        self.assertEqual(model, device.model)

    def test_get_vendor_model_aastra(self):
        device = DeviceFeatures()
        device.deviceid = 'sdfjhdf83498erw8'
        device.config = '893247987djfkh'
        device.mac = '00:14:7f:e1:37:62'
        device.vendor = 'Aastra'
        device.model = 'qwerty'
        device.proto = 'sip'

        self.session.begin()
        self.session.add(device)
        self.session.commit()

        vendor, model = device_dao.get_vendor_model(device.id)

        self.assertEqual(vendor, device.vendor)
        self.assertEqual(model, device.model)

    def test_get_vendor_model_various(self):
        cisco = DeviceFeatures()
        cisco.deviceid = 'sdfjhdf83498erw8'
        cisco.config = '893247987djfkh'
        cisco.mac = '00:14:7f:e1:37:62'
        cisco.vendor = 'Cisco'
        cisco.model = 'abcde'
        cisco.proto = 'sip'

        aastra = DeviceFeatures()
        aastra.deviceid = 'sdfjhdf83498erw8'
        aastra.config = '893247987djfkh'
        aastra.mac = '00:14:7f:e1:37:62'
        aastra.vendor = 'Aastra'
        aastra.model = 'qwerty'
        aastra.proto = 'sip'

        self.session.begin()
        self.session.add(cisco)
        self.session.add(aastra)
        self.session.commit()

        vendor, model = device_dao.get_vendor_model(cisco.id)
        self.assertEqual(cisco.vendor, vendor)
        self.assertEqual(cisco.model, model)

        vendor, model = device_dao.get_vendor_model(aastra.id)
        self.assertEqual(vendor, aastra.vendor)
        self.assertEqual(model, aastra.model)

    def test_get_vendor_model_with_unknow_device_id(self):
        self.assertRaises(LookupError, device_dao.get_vendor_model, 666)

    def test_get_peer_name_abcde(self):
        protocol = 'SIP'
        name = 'abcde'
        expected_name = '/'.join([protocol, name])
        device = DeviceFeatures()
        device.deviceid = 'sdfjhdf83498erw8'
        device.config = '893247987djfkh'
        device.mac = '00:14:7f:e1:37:62'
        device.vendor = 'Aastra'
        device.model = '6731i'
        device.proto = 'sip'

        self.session.begin()
        self.session.add(device)
        self.session.commit()

        line = LineFeatures()
        line.device = str(device.id)
        line.protocolid = 0
        line.context = 'myctx'
        line.iduserfeatures = 5
        line.number = '1002'
        line.name = name
        line.provisioningid = 123
        line.protocol = protocol

        self.session.begin()
        self.session.add(line)
        self.session.commit()

        peer_name = device_dao.get_peer_name(device.id)

        self.assertEqual(peer_name, expected_name)

    def test_get_peer_name_qwerty(self):
        protocol = 'SIP'
        name = 'qwerty'
        expected_name = '/'.join([protocol, name])
        device = DeviceFeatures()
        device.deviceid = 'sdfjhdf83498erw8'
        device.config = '893247987djfkh'
        device.mac = '00:14:7f:e1:37:62'
        device.vendor = 'Aastra'
        device.model = '6731i'
        device.proto = 'sip'

        self.session.begin()
        self.session.add(device)
        self.session.commit()

        line = LineFeatures()
        line.device = str(device.id)
        line.protocolid = 0
        line.context = 'myctx'
        line.iduserfeatures = 5
        line.number = '1002'
        line.name = name
        line.provisioningid = 123
        line.protocol = protocol

        self.session.begin()
        self.session.add(line)
        self.session.commit()

        peer_name = device_dao.get_peer_name(device.id)

        self.assertEqual(peer_name, expected_name)

    def test_get_peer_name_no_matching_line(self):
        device = DeviceFeatures()
        device.deviceid = 'sdfjhdf83498erw8'
        device.config = '893247987djfkh'
        device.mac = '00:14:7f:e1:37:62'
        device.vendor = 'Aastra'
        device.model = '6731i'
        device.proto = 'sip'

        self.session.begin()
        self.session.add(device)
        self.session.commit()

        self.assertRaises(LookupError, device_dao.get_peer_name, device.id)
