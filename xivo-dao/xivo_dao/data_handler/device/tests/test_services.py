# -*- coding: UTF-8 -*-

import unittest
from mock import patch
from xivo_dao.data_handler.device import services as device_services
from xivo_dao.data_handler.device.model import Device
from xivo_dao.data_handler.extension.model import Extension
from xivo_dao.data_handler.line.model import LineSIP, LineSCCP
from xivo_dao.data_handler.user_line_extension.model import UserLineExtension


class Test(unittest.TestCase):

    def setUp(self):
        self.device_id = 1
        self.provd_deviceid = "ad0a12fd5f244ae68a3c626789203698"

    @patch('xivo_dao.data_handler.extension.dao.get')
    @patch('xivo_dao.data_handler.user_line_extension.dao.find_all_by_line_id')
    @patch('xivo_dao.helpers.provd_connector.config_manager')
    @patch('xivo_dao.helpers.provd_connector.device_manager')
    def test_add_line_to_device_with_a_sip_line(self, device_manager, config_manager, ule_find_all_by_line_id, extension_dao_get):
        username = '1234'
        secret = 'password'
        exten = '1250'
        context = 'default'
        callerid = 'Francis Dagobert <%s>' % exten
        proxy_ip = '10.39.5.1'
        registrar_ip = proxy_ip
        configregistrar = 'default'

        line = LineSIP(id=1,
                       num=1,
                       context=context,
                       username=username,
                       secret=secret,
                       callerid=callerid,
                       configregistrar=configregistrar)
        device = Device(id=self.device_id,
                        deviceid=self.provd_deviceid)

        provd_base_config = {
            "raw_config": {}
        }

        config_registrar_dict = self._give_me_a_provd_configregistrar(proxy_ip)
        config_manager.get.side_effect = (provd_base_config, config_registrar_dict)
        ule_find_all_by_line_id.return_value = [UserLineExtension(user_id=1,
                                                                  line_id=line.id,
                                                                  extension_id=3,
                                                                  main_user=True,
                                                                  main_line=True)]
        extension_dao_get.return_value = Extension(exten=exten,
                                                   context=context)

        expected_arg = {
            "raw_config": {
                "sip_lines": {
                    "1": {
                        'username': username,
                        'auth_username': username,
                        'display_name': callerid,
                        'number': exten,
                        'password': secret,
                        'proxy_ip': proxy_ip,
                        'registrar_ip': registrar_ip
                    }
                }
            }
        }

        device_services.add_line_to_device(device, line)

        config_manager.get.assert_any_call(self.provd_deviceid)
        config_manager.get.assert_any_call(configregistrar)
        config_manager.update.assert_called_with(expected_arg)

    @patch('xivo_dao.data_handler.extension.dao.get')
    @patch('xivo_dao.data_handler.user_line_extension.dao.find_all_by_line_id')
    @patch('xivo_dao.helpers.provd_connector.config_manager')
    @patch('xivo_dao.helpers.provd_connector.device_manager')
    def test_add_line_to_device_with_a_sip_line_with_proxy_backup(self, device_manager, config_manager, ule_find_all_by_line_id, extension_dao_get):
        username = '1234'
        secret = 'password'
        exten = '1250'
        context = 'default'
        callerid = 'Francis Dagobert <%s>' % exten
        proxy_ip = '10.39.5.1'
        registrar_ip = proxy_ip
        proxy_backup = '10.39.5.2'
        configregistrar = 'default'

        line = LineSIP(id=1,
                       num=1,
                       context=context,
                       username=username,
                       secret=secret,
                       callerid=callerid,
                       configregistrar=configregistrar)
        device = Device(id=self.device_id,
                        deviceid=self.provd_deviceid)

        provd_base_config = {
            "raw_config": {}
        }

        config_registrar_dict = self._give_me_a_provd_configregistrar(proxy_ip, proxy_backup)
        config_manager.get.side_effect = (provd_base_config, config_registrar_dict)
        ule_find_all_by_line_id.return_value = [UserLineExtension(user_id=1,
                                                                  line_id=line.id,
                                                                  extension_id=3,
                                                                  main_user=True,
                                                                  main_line=True)]
        extension_dao_get.return_value = Extension(exten=exten,
                                                   context=context)

        expected_arg = {
            "raw_config": {
                "sip_lines": {
                    "1": {
                        'username': username,
                        'auth_username': username,
                        'display_name': callerid,
                        'number': exten,
                        'password': secret,
                        'proxy_ip': proxy_ip,
                        'registrar_ip': registrar_ip,
                        'backup_registrar_ip': proxy_backup,
                        'backup_proxy_ip': proxy_backup
                    }
                }
            }
        }

        device_services.add_line_to_device(device, line)

        config_manager.get.assert_any_call(self.provd_deviceid)
        config_manager.get.assert_any_call(configregistrar)
        config_manager.update.assert_called_with(expected_arg)

    @patch('xivo_dao.data_handler.user_line_extension.dao.find_all_by_line_id')
    @patch('xivo_dao.helpers.provd_connector.config_manager')
    @patch('xivo_dao.helpers.provd_connector.device_manager')
    def test_add_line_to_device_with_a_sccp_line(self, device_manager, config_manager, ule_find_all_by_line_id):
        exten = '1250'
        context = 'default'
        callerid = 'Francis Dagobert <%s>' % exten
        proxy_ip = '10.39.5.1'
        configregistrar = 'default'

        line = LineSCCP(id=1,
                       num=1,
                       context=context,
                       callerid=callerid,
                       configregistrar=configregistrar)
        device = Device(id=self.device_id,
                        deviceid=self.provd_deviceid)

        provd_base_config = {
            "raw_config": {}
        }

        config_registrar_dict = self._give_me_a_provd_configregistrar(proxy_ip)
        config_manager.get.side_effect = (provd_base_config, config_registrar_dict)
        ule_find_all_by_line_id.return_value = [UserLineExtension(user_id=1,
                                                                  line_id=line.id,
                                                                  extension_id=3,
                                                                  main_user=True,
                                                                  main_line=True)]

        expected_arg = {
            "raw_config": {
                "sccp_call_managers": {
                    1: {'ip': proxy_ip}
                }
            }
        }

        device_services.add_line_to_device(device, line)

        config_manager.get.assert_any_call(self.provd_deviceid)
        config_manager.get.assert_any_call(configregistrar)
        config_manager.update.assert_called_with(expected_arg)

    @patch('xivo_dao.data_handler.user_line_extension.dao.find_all_by_line_id')
    @patch('xivo_dao.helpers.provd_connector.config_manager')
    @patch('xivo_dao.helpers.provd_connector.device_manager')
    def test_add_line_to_device_with_a_sccp_line_with_proxy_backup(self, device_manager, config_manager, ule_find_all_by_line_id):
        exten = '1250'
        context = 'default'
        callerid = 'Francis Dagobert <%s>' % exten
        proxy_ip = '10.39.5.1'
        proxy_backup = '10.39.5.2'
        configregistrar = 'default'

        line = LineSCCP(id=1,
                       num=1,
                       context=context,
                       callerid=callerid,
                       configregistrar=configregistrar)
        device = Device(id=self.device_id,
                        deviceid=self.provd_deviceid)

        provd_base_config = {
            "raw_config": {}
        }

        config_registrar_dict = self._give_me_a_provd_configregistrar(proxy_ip, proxy_backup)
        config_manager.get.side_effect = (provd_base_config, config_registrar_dict)
        ule_find_all_by_line_id.return_value = [UserLineExtension(user_id=1,
                                                                  line_id=line.id,
                                                                  extension_id=3,
                                                                  main_user=True,
                                                                  main_line=True)]

        expected_arg = {
            "raw_config": {
                "sccp_call_managers": {
                    1: {'ip': proxy_ip},
                    2: {'ip': proxy_backup}
                }
            }
        }

        device_services.add_line_to_device(device, line)

        config_manager.get.assert_any_call(self.provd_deviceid)
        config_manager.get.assert_any_call(configregistrar)
        config_manager.update.assert_called_with(expected_arg)

    @patch('xivo_dao.data_handler.device.dao.get')
    @patch('xivo_dao.helpers.provd_connector.config_manager')
    @patch('xivo_dao.helpers.provd_connector.device_manager')
    def test_remove_line_from_device(self, device_manager, config_manager, device_dao_get):
        config_dict = {
            "raw_config": {
                "sip_lines": {
                    "1": {"username": "1234"},
                    "2": {"username": "5678"}
                }
            }
        }
        config_manager.get.return_value = config_dict
        line = LineSIP(num=2)

        device = Device(id=self.device_id,
                        deviceid=self.provd_deviceid)
        device_dao_get.return_value = device

        expected_arg = {
            "raw_config": {
                "sip_lines": {
                    "1": {"username": "1234"}
                }
            }
        }

        device_services.remove_line_from_device(self.device_id, line)

        config_manager.get.assert_called_with(self.provd_deviceid)
        config_manager.update.assert_called_with(expected_arg)
        self.assertEquals(0, config_manager.autocreate.call_count)

    @patch('xivo_dao.data_handler.device.dao.get')
    @patch('xivo_dao.helpers.provd_connector.config_manager')
    @patch('xivo_dao.helpers.provd_connector.device_manager')
    def test_remove_line_from_device_autoprov(self, device_manager, config_manager, device_dao_get):
        autoprovid = "autoprov1234"
        config_dict = {
            "raw_config": {
                "sip_lines": {
                    "1": {"username": "1234"}
                },
               'funckeys': {
                    '1': {
                          'label': 'bob',
                          'line': 1,
                          'type': 'blf',
                          'value': '1001'
                          }
                }
            }
        }

        device_dict = {
           "ip": "10.60.0.109",
           "version": "3.2.2.1136",
           "config": self.provd_deviceid,
           "id": self.device_id
        }
        config_manager.get.return_value = config_dict
        device_manager.get.return_value = device_dict
        config_manager.autocreate.return_value = autoprovid
        line = LineSIP(num=1)

        device = Device(id=self.device_id,
                        deviceid=self.provd_deviceid)
        device_dao_get.return_value = device

        expected_arg_config = {"raw_config": {}}
        expected_arg_device = {
           "ip": "10.60.0.109",
           "version": "3.2.2.1136",
           "config": autoprovid,
           "id": self.device_id
        }

        device_services.remove_line_from_device(self.device_id, line)

        config_manager.get.assert_called_with(self.provd_deviceid)
        config_manager.autocreate.assert_called_with()
        device_manager.get.assert_called_with(self.provd_deviceid)
        device_manager.update.assert_called_with(expected_arg_device)
        config_manager.update.assert_called_with(expected_arg_config)

    @patch('xivo_dao.data_handler.device.dao.get')
    @patch('xivo_dao.helpers.provd_connector.config_manager')
    @patch('xivo_dao.helpers.provd_connector.device_manager')
    def test_remove_line_from_device_no_funckeys(self, device_manager, config_manager, device_dao_get):
        autoprovid = "autoprov1234"
        config_dict = {
            "raw_config": {
                "sip_lines": {
                    "1": {"username": "1234"}
                }
            }
        }
        device_dict = {
           "ip": "10.60.0.109",
           "version": "3.2.2.1136",
           "config": self.provd_deviceid,
           "id": self.device_id
        }
        line = LineSIP(num=1)

        device = Device(id=self.device_id,
                        deviceid=self.provd_deviceid)

        config_manager.get.return_value = config_dict
        device_manager.get.return_value = device_dict
        config_manager.autocreate.return_value = autoprovid
        device_dao_get.return_value = device

        try:
            device_services.remove_line_from_device(self.device_id, line)
        except:
            self.fail("An exception was raised whereas it should not")

    def _give_me_a_provd_configregistrar(self, proxy_main, proxy_backup=None):
        config_registrar_dict = {
            'id': 'default',
            'X_type': 'registrar',
            'raw_config': {'X_key': 'xivo'},
            'deletable': False,
            'displayname': 'local',
            'parent_ids': [],
            'proxy_main': proxy_main,
            'registrar_main': proxy_main
        }
        if proxy_backup is not None:
            config_registrar_dict.update({
                'proxy_backup': proxy_backup,
                'registrar_backup': proxy_backup
            })
        return config_registrar_dict
