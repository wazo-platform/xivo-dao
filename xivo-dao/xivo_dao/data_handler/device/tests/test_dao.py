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

from hamcrest import *
from mock import Mock, patch
from urllib2 import HTTPError
from StringIO import StringIO
from contextlib import contextmanager

from xivo_dao.data_handler.device import dao as device_dao
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.alchemy.devicefeatures import DeviceFeatures as DeviceSchema
from xivo_dao.data_handler.device.model import Device
from xivo_dao.data_handler.exception import ElementDeletionError, ElementCreationError, \
    ElementNotExistsError


class TestDeviceDao(DAOTestCase):

    tables = [
        DeviceSchema
    ]

    def _has_properties(self, properties):
        matchers = []
        for key, value in properties.iteritems():
            matchers.append(has_property(key, value))
        return all_of(*matchers)

    def setUp(self):
        self.empty_tables()
        self.deviceid = "ad0a12fd5f244ae68a3c626789203698"

    @contextmanager
    def provd_managers(self):
        config_patcher = patch('xivo_dao.helpers.provd_connector.config_manager')
        device_patcher = patch('xivo_dao.helpers.provd_connector.device_manager')
        plugin_patcher = patch('xivo_dao.helpers.provd_connector.plugin_manager')

        mock_device_manager = device_patcher.start()
        mock_config_manager = config_patcher.start()
        mock_plugin_manager = plugin_patcher.start()

        device_manager = Mock()
        config_manager = Mock()
        plugin_manager = Mock()

        mock_device_manager.return_value = device_manager
        mock_config_manager.return_value = config_manager
        mock_plugin_manager.return_value = plugin_manager

        yield (device_manager, config_manager, plugin_manager)

        config_patcher.stop()
        device_patcher.stop()
        plugin_patcher.stop()

    def test_get_no_device(self):
        with self.provd_managers() as (device_manager, config_manager, _):

            device_manager.get.side_effect = HTTPError('', 404, '', '', StringIO(''))

            self.assertRaises(ElementNotExistsError, device_dao.get, self.deviceid)
            device_manager.get.assert_called_once_with(self.deviceid)

    def test_get_no_template(self):
        expected_device = Device(
            id=self.deviceid,
            ip='10.0.0.1',
            mac='00:11:22:33:44:55',
            model='6731i',
            vendor='Aastra',
            version='3.2.2.3077',
            plugin='xivo-aastra-3.2.2-SP3',
        )

        provd_device = {
            u'added': u'auto',
            u'configured': True,
            u'id': expected_device.id,
            u'ip': expected_device.ip,
            u'mac': expected_device.mac,
            u'model': expected_device.model,
            u'plugin': expected_device.plugin,
            u'vendor': expected_device.vendor,
            u'version': expected_device.version,
        }

        with self.provd_managers() as (device_manager, config_manager, _):
            device_manager.get.return_value = provd_device

            device = device_dao.get(expected_device.id)

            assert_that(device, all_of(
                has_property('id', expected_device.id),
                has_property('ip', expected_device.ip),
                has_property('mac', expected_device.mac),
                has_property('model', expected_device.model),
                has_property('vendor', expected_device.vendor),
                has_property('version', expected_device.version),
                has_property('plugin', expected_device.plugin),
            ))

            device_manager.get.assert_called_once_with(expected_device.id)
            assert_that(config_manager.get.call_count, equal_to(0))

    def test_get(self):
        config_id = 'abcdefghijklmnopqurstuvwxyz123456'

        expected_device = Device(
            id=self.deviceid,
            ip='10.0.0.1',
            mac='00:11:22:33:44:55',
            model='6731i',
            vendor='Aastra',
            version='3.2.2.3077',
            plugin='xivo-aastra-3.2.2-SP3',
            template_id='defaultconfigdevice'
        )

        provd_device = {
            u'added': u'auto',
            u'config': config_id,
            u'configured': True,
            u'id': expected_device.id,
            u'ip': expected_device.ip,
            u'mac': expected_device.mac,
            u'model': expected_device.model,
            u'plugin': expected_device.plugin,
            u'vendor': expected_device.vendor,
            u'version': expected_device.version,
        }

        provd_config = {
            u'configdevice': u'defaultconfigdevice',
            u'deletable': True,
            u'id': config_id,
            u'parent_ids': [u'base', u'defaultconfigdevice'],
            u'raw_config': {}
        }

        with self.provd_managers() as (device_manager, config_manager, _):
            device_manager.get.return_value = provd_device
            config_manager.get.return_value = provd_config

            device = device_dao.get(expected_device.id)

            assert_that(device, all_of(
                has_property('id', expected_device.id),
                has_property('ip', expected_device.ip),
                has_property('mac', expected_device.mac),
                has_property('model', expected_device.model),
                has_property('vendor', expected_device.vendor),
                has_property('version', expected_device.version),
                has_property('plugin', expected_device.plugin),
                has_property('template_id', expected_device.template_id)
            ))

            device_manager.get.assert_called_once_with(expected_device.id)
            config_manager.get.assert_called_once_with(config_id)

    def test_get_custom_template(self):
        config_id = 'abcdefghijklmnopqurstuvwxyz123456'

        expected_device = Device(
            id=self.deviceid,
            ip='10.0.0.1',
            mac='00:11:22:33:44:55',
            model='6731i',
            vendor='Aastra',
            version='3.2.2.3077',
            plugin='xivo-aastra-3.2.2-SP3',
            template_id='mytemplate'
        )

        provd_device = {
            u'added': u'auto',
            u'config': config_id,
            u'configured': True,
            u'id': expected_device.id,
            u'ip': expected_device.ip,
            u'mac': expected_device.mac,
            u'model': expected_device.model,
            u'plugin': expected_device.plugin,
            u'vendor': expected_device.vendor,
            u'version': expected_device.version,
        }

        provd_config = {
            u'configdevice': u'defaultconfigdevice',
            u'deletable': True,
            u'id': config_id,
            u'parent_ids': [u'base', u'defaultconfigdevice', 'mytemplate'],
            u'raw_config': {}
        }

        with self.provd_managers() as (device_manager, config_manager, _):
            device_manager.get.return_value = provd_device
            config_manager.get.return_value = provd_config

            device = device_dao.get(expected_device.id)

            assert_that(device, all_of(
                has_property('id', expected_device.id),
                has_property('ip', expected_device.ip),
                has_property('mac', expected_device.mac),
                has_property('model', expected_device.model),
                has_property('vendor', expected_device.vendor),
                has_property('version', expected_device.version),
                has_property('plugin', expected_device.plugin),
                has_property('template_id', expected_device.template_id)
            ))

            device_manager.get.assert_called_once_with(expected_device.id)
            config_manager.get.assert_called_once_with(config_id)

    def test_find_not_found(self):
        device_id = 39784

        result = device_dao.find(device_id)

        assert_that(result, none())

    def test_find_found(self):
        device_id = 39784
        device_row = self.add_device(deviceid=device_id)
        expected_device = Device.from_data_source(device_row)

        result = device_dao.find(expected_device.id)

        assert_that(result, equal_to(expected_device))

    def test_find_all_no_devices(self):
        expected = []

        result = device_dao.find_all()

        assert_that(result, equal_to(expected))

    def test_find_all(self):
        device1 = {
            'deviceid': 'deviceid1',
            'config': 'config1',
            'plugin': 'plugin1',
            'ip': 'ip1',
            'mac': 'mac1',
            'sn': 'sn1',
            'vendor': 'vendor1',
            'model': 'model1',
            'version': 'version1',
            'proto': 'proto1',
            'internal': 1,
            'configured': 1,
            'commented': 1,
            'description': 'description1'
        }
        device2 = {
            'deviceid': 'deviceid2',
            'config': 'config2',
            'plugin': 'plugin2',
            'ip': 'ip2',
            'mac': 'mac2',
            'sn': 'sn2',
            'vendor': 'vendor2',
            'model': 'model2',
            'version': 'version2',
            'proto': 'proto2',
            'internal': 2,
            'configured': 2,
            'commented': 2,
            'description': 'description2'
        }
        self.add_device(**device1)
        self.add_device(**device2)

        result = device_dao.find_all()

        assert_that(result, has_items(
            self._has_properties(device1),
            self._has_properties(device2),
        ))

    def test_delete_not_exist(self):
        extension = Device(id=1)

        self.assertRaises(ElementDeletionError, device_dao.delete, extension)

    @patch('xivo_dao.helpers.provd_connector.config_manager')
    @patch('xivo_dao.helpers.provd_connector.device_manager')
    def test_create_empty_device(self, mock_device_manager, mock_config_manager):
        device_id = 'abcd1234'
        device = Device()

        device_manager = Mock()
        mock_device_manager.return_value = device_manager

        config_manager = Mock()
        mock_config_manager.return_value = config_manager

        device_manager.add.return_value = device_id

        expected_provd_device = {}
        expected_device_update = {
            'id': device_id,
            'config': device_id
        }
        expected_provd_config = {
            'configdevice': 'defaultconfigdevice',
            'deletable': True,
            'id': device_id,
            'parent_ids': ['base', 'defaultconfigdevice'],
            'raw_config': {}
        }

        result = device_dao.create(device)

        device_manager.add.assert_called_once_with(expected_provd_device)
        device_manager.update.assert_called_once_with(expected_device_update)
        config_manager.add.assert_called_once_with(expected_provd_config)

        assert_that(result.id, equal_to(device_id))

    @patch('xivo_dao.helpers.provd_connector.config_manager')
    @patch('xivo_dao.helpers.provd_connector.device_manager')
    def test_create_with_parameters(self, mock_device_manager, mock_config_manager):
        device_id = 'abcd1234'
        device_mac = 'AB:11:22:33:44:55'
        expected_mac = 'ab:11:22:33:44:55'

        device = Device(ip='10.0.0.1',
                        mac=device_mac,
                        plugin='xivo-aastra-3.2.2-SP3',
                        vendor='Aastra',
                        model='6731i')

        device_manager = Mock()
        mock_device_manager.return_value = device_manager

        config_manager = Mock()
        mock_config_manager.return_value = config_manager

        device_manager.add.return_value = device_id

        expected_provd_device = {
            'ip': device.ip,
            'mac': expected_mac,
            'plugin': device.plugin,
            'vendor': device.vendor,
            'model': device.model,
        }

        expected_device_update = {
            'id': device_id,
            'ip': device.ip,
            'mac': expected_mac,
            'plugin': device.plugin,
            'vendor': device.vendor,
            'model': device.model,
            'config': device_id,
        }

        expected_provd_config = {
            'configdevice': 'defaultconfigdevice',
            'deletable': True,
            'id': device_id,
            'parent_ids': ['base', 'defaultconfigdevice'],
            'raw_config': {}
        }

        result = device_dao.create(device)

        device_manager.add.assert_called_once_with(expected_provd_device)
        config_manager.add.assert_called_once_with(expected_provd_config)
        device_manager.update.assert_called_once_with(expected_device_update)

        assert_that(result, all_of(
            has_property('id', device_id),
            has_property('mac', device.mac),
            has_property('ip', device.ip),
            has_property('plugin', device.plugin),
            has_property('vendor', device.vendor),
            has_property('model', device.model)
        ))

    @patch('xivo_dao.helpers.provd_connector.config_manager')
    @patch('xivo_dao.helpers.provd_connector.device_manager')
    def test_create_with_template_id(self, mock_device_manager, mock_config_manager):
        device_id = 'abcd1234'
        template_id = 'efgh5678'

        device = Device(template_id=template_id)

        device_manager = Mock()
        mock_device_manager.return_value = device_manager

        config_manager = Mock()
        mock_config_manager.return_value = config_manager

        device_manager.add.return_value = device_id

        expected_provd_device = {}
        expected_device_update = {
            'id': device_id,
            'config': device_id
        }

        expected_provd_config = {
            'configdevice': template_id,
            'deletable': True,
            'id': device_id,
            'parent_ids': ['base', 'defaultconfigdevice', template_id],
            'raw_config': {}
        }

        result = device_dao.create(device)

        device_manager.add.assert_called_once_with(expected_provd_device)
        device_manager.update.assert_called_once_with(expected_device_update)
        config_manager.add.assert_called_once_with(expected_provd_config)

        assert_that(result.template_id, equal_to(template_id))

    @patch('xivo_dao.helpers.provd_connector.config_manager')
    @patch('xivo_dao.helpers.provd_connector.device_manager')
    def test_create_with_device_manager_error(self, mock_device_manager, mock_config_manager):
        device = Device()

        device_manager = Mock()
        mock_device_manager.return_value = device_manager

        config_manager = Mock()
        mock_config_manager.return_value = config_manager

        device_manager.add.side_effect = Exception()

        self.assertRaises(ElementCreationError, device_dao.create, device)

        assert_that(config_manager.add.call_count, equal_to(0))

    @patch('xivo_dao.helpers.provd_connector.config_manager')
    @patch('xivo_dao.helpers.provd_connector.device_manager')
    def test_create_with_device_manager_error_on_update(self, mock_device_manager, mock_config_manager):
        device = Device()

        device_manager = Mock()
        mock_device_manager.return_value = device_manager

        config_manager = Mock()
        mock_config_manager.return_value = config_manager

        device_manager.add.return_value = 'abcd1234'
        device_manager.update.side_effect = Exception()

        self.assertRaises(ElementCreationError, device_dao.create, device)

        assert_that(config_manager.add.call_count, equal_to(0))

    @patch('xivo_dao.helpers.provd_connector.config_manager')
    @patch('xivo_dao.helpers.provd_connector.device_manager')
    def test_create_with_config_manager_error(self, mock_device_manager, mock_config_manager):
        device_id = 'abcd1234'
        device = Device()

        device_manager = Mock()
        mock_device_manager.return_value = device_manager

        config_manager = Mock()
        mock_config_manager.return_value = config_manager

        device_manager.add.return_value = device_id
        config_manager.add.side_effect = Exception()

        self.assertRaises(ElementCreationError, device_dao.create, device)
        device_manager.remove.assert_called_once_with(device_id)

    @patch('xivo_dao.helpers.provd_connector.device_manager')
    def test_mac_exists_no_mac(self, mock_device_manager):
        device_manager = Mock()
        mock_device_manager.return_value = device_manager
        device_manager.find.return_value = []

        mac = 'FF:FF:FF:FF:FF'

        result = device_dao.mac_exists(mac)

        assert_that(result, equal_to(False))
        device_manager.find.assert_called_once_with({'mac': mac})

    @patch('xivo_dao.helpers.provd_connector.device_manager')
    def test_mac_exists_with_a_mac(self, mock_device_manager):
        device_manager = Mock()
        mock_device_manager.return_value = device_manager
        device_manager.find.return_value = [{u'added': u'auto',
                                             u'config': u'cb20ee7c27e2483ba737e8061b40113d',
                                             u'configured': True,
                                             u'id': u'cb20ee7c27e2483ba737e8061b40113d',
                                             u'ip': u'10.0.0.1',
                                             u'mac': u'FF:FF:FF:FF:FF:FF',
                                             u'model': u'820',
                                             u'plugin': u'xivo-snom-8.7.3.19',
                                             u'vendor': u'Snom',
                                             u'version': u'8.7.3.19'}]

        mac = 'FF:FF:FF:FF:FF'

        result = device_dao.mac_exists(mac)

        assert_that(result, equal_to(True))
        device_manager.find.assert_called_once_with({'mac': mac})

    @patch('xivo_dao.helpers.provd_connector.plugin_manager')
    def test_plugin_exists_no_plugin(self, mock_plugin_manager):
        plugin_manager = Mock()
        mock_plugin_manager.return_value = plugin_manager
        plugin_manager.plugins.return_value = []

        plugin = 'null'

        result = device_dao.plugin_exists(plugin)

        assert_that(result, equal_to(False))
        plugin_manager.plugins.assert_called_once_with()

    @patch('xivo_dao.helpers.provd_connector.plugin_manager')
    def test_plugin_exists_with_a_plugin_installed(self, mock_plugin_manager):
        plugin_manager = Mock()
        mock_plugin_manager.return_value = plugin_manager
        plugin_manager.plugins.return_value = ['null']

        plugin = 'null'

        result = device_dao.plugin_exists(plugin)

        assert_that(result, equal_to(True))
        plugin_manager.plugins.assert_called_once_with()

    @patch('xivo_dao.helpers.provd_connector.config_manager')
    def test_template_id_exists_no_template(self, mock_config_manager):
        config_manager = Mock()
        mock_config_manager.return_value = config_manager

        config_manager.find.return_value = []

        template_id = 'abcd1234'

        result = device_dao.template_id_exists(template_id)

        assert_that(result, equal_to(False))
        config_manager.find.assert_called_once_with({'X_type': 'device', 'id': template_id})

    @patch('xivo_dao.helpers.provd_connector.config_manager')
    def test_template_id_exists_with_a_template(self, mock_config_manager):
        config_manager = Mock()
        mock_config_manager.return_value = config_manager

        template_id = 'abcd1234'

        config_manager.find.return_value = [{
            u'X_type': u'device',
            u'deletable': True,
            u'id': template_id,
            u'label': u'testtemplate',
            u'parent_ids': [],
            u'raw_config': {}}]

        result = device_dao.template_id_exists(template_id)

        assert_that(result, equal_to(True))
        config_manager.find.assert_called_once_with({'X_type': 'device', 'id': template_id})
