import unittest

from hamcrest import *
from xivo_dao.data_handler.device import provd_builder
from xivo_dao.data_handler.device.model import Device


class TestProvdBuilder(unittest.TestCase):

    def test_build_create_empty_device(self):
        device_id = 'abcd1234'
        device = Device(id=device_id)

        expected_provd_device = {
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

        provd_device, provd_config = provd_builder.build_create(device)
        assert_that(provd_device, equal_to(expected_provd_device))
        assert_that(provd_config, equal_to(expected_provd_config))

    def test_build_create_with_parameters(self):
        device_id = 'abcd1234'
        device_mac = 'AB:11:22:33:44:55'
        expected_mac = 'ab:11:22:33:44:55'

        device = Device(id=device_id,
                        ip='10.0.0.1',
                        mac=device_mac,
                        plugin='xivo-aastra-3.2.2-SP3',
                        vendor='Aastra',
                        model='6731i')

        expected_provd_device = {
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

        provd_device, provd_config = provd_builder.build_create(device)
        assert_that(provd_device, equal_to(expected_provd_device))
        assert_that(provd_config, equal_to(expected_provd_config))

    def test_build_create_with_template_id(self):
        device_id = 'abcd1234'
        template_id = 'efgh5678'

        device = Device(id=device_id, template_id=template_id)

        expected_provd_device = {
            'id': device_id,
            'config': device_id
        }

        expected_provd_config = {
            'configdevice': template_id,
            'deletable': True,
            'id': device_id,
            'parent_ids': ['base', template_id],
            'raw_config': {}
        }

        provd_device, provd_config = provd_builder.build_create(device)
        assert_that(provd_device, equal_to(expected_provd_device))
        assert_that(provd_config, equal_to(expected_provd_config))

    def test_build_edit_with_an_empty_device_and_no_config(self):
        device_id = 'abc123'
        device = Device(id=device_id)

        provd_device = {
            'configured': False,
            'id': device_id,
        }

        expected_provd_device = {
            'configured': False,
            'id': device_id,
        }

        result_device, result_config = provd_builder.build_edit(device, provd_device, None)

        assert_that(result_device, equal_to(expected_provd_device))

    def test_build_edit_with_new_properties_and_no_config(self):
        device_id = 'abc123'

        device = Device(
            id=device_id,
            ip='10.0.0.1',
            mac='00:11:22:33:44:55',
            plugin='aastraplugin',
            model='6735i',
            vendor='Aastra',
            version='0.0.1'
        )

        provd_device = {
            'configured': False,
            'id': device_id
        }

        expected_provd_device = {
            'configured': False,
            'id': device_id,
            'ip': '10.0.0.1',
            'mac': '00:11:22:33:44:55',
            'plugin': 'aastraplugin',
            'model': '6735i',
            'vendor': 'Aastra',
            'version': '0.0.1'
        }

        result_device, result_config = provd_builder.build_edit(device, provd_device, None)

        assert_that(result_device, equal_to(expected_provd_device))

    def test_build_edit_with_a_template_id_and_a_bare_config(self):
        device_id = 'def456'
        config_id = 'abc123'

        device = Device(
            id=device_id,
            template_id='mytemplate'
        )

        provd_device = {
            'configured': False,
            'id': device_id,
            'config': config_id
        }

        provd_config = {
            'configdevice': 'defaultconfigdevice',
            'deletable': True,
            'id': config_id,
            'parent_ids': ['base', 'defaultconfigdevice'],
            'raw_config': {}
        }

        expected_provd_device = {
            'configured': False,
            'id': device_id,
            'config': config_id
        }

        expected_provd_config = {
            'configdevice': 'mytemplate',
            'deletable': True,
            'id': config_id,
            'parent_ids': ['base', 'mytemplate'],
            'raw_config': {}
        }

        result_device, result_config = provd_builder.build_edit(device, provd_device, provd_config)

        assert_that(result_device, equal_to(expected_provd_device))
        assert_that(result_config, equal_to(expected_provd_config))

    def test_build_edit_with_template_id_to_default(self):
        device_id = 'def456'
        config_id = 'abc123'

        device = Device(
            id=device_id,
            template_id='defaultconfigdevice'
        )

        provd_device = {
            'configured': True,
            'id': device_id,
            'config': config_id
        }

        provd_config = {
            'configdevice': 'mytemplate',
            'deletable': True,
            'id': config_id,
            'parent_ids': ['base', 'defaultconfigdevice', 'mytemplate'],
            'raw_config': {
            }
        }

        expected_provd_device = {
            'configured': True,
            'id': device_id,
            'config': config_id
        }

        expected_provd_config = {
            'configdevice': 'defaultconfigdevice',
            'deletable': True,
            'id': config_id,
            'parent_ids': ['base', 'defaultconfigdevice'],
            'raw_config': {
            }
        }

        result_device, result_config = provd_builder.build_edit(device, provd_device, provd_config)

        assert_that(result_device, equal_to(expected_provd_device))
        assert_that(result_config, equal_to(expected_provd_config))

    def test_build_edit_with_a_template_id_and_a_custom_config(self):
        device_id = 'def456'
        config_id = 'abc123'

        device = Device(
            id=device_id,
            template_id='mytemplate'
        )

        provd_device = {
            'configured': True,
            'id': device_id,
            'config': config_id
        }

        provd_config = {
            'configdevice': 'defaultconfigdevice',
            'deletable': True,
            'id': config_id,
            'parent_ids': ['base', 'defaultconfigdevice'],
            'raw_config': {
            }
        }

        expected_provd_device = {
            'configured': True,
            'id': device_id,
            'config': config_id
        }

        expected_provd_config = {
            'configdevice': 'mytemplate',
            'deletable': True,
            'id': config_id,
            'parent_ids': ['base', 'mytemplate'],
            'raw_config': {
            }
        }

        result_device, result_config = provd_builder.build_edit(device, provd_device, provd_config)

        assert_that(result_device, equal_to(expected_provd_device))
        assert_that(result_config, equal_to(expected_provd_config))
