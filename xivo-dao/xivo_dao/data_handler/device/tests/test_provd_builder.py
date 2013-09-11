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
