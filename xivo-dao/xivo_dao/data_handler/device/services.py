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

from xivo_dao.helpers import provd_connector
from xivo_dao.data_handler.device import dao as device_dao
from xivo_dao.data_handler.user_line_extension import dao as user_line_extension_dao
from xivo_dao.data_handler.extension import dao as extension_dao


def get(device_id):
    return device_dao.get(device_id)


def get_by_deviceid(session, device_id):
    return device_dao.get_by_deviceid(device_id)


def add_line_to_device(device, line):
    config = provd_connector.config_manager.get(device.deviceid)
    confregistrar = provd_connector.config_manager.get(line.configregistrar)
    ules = user_line_extension_dao.find_all_by_line_id(line.id)
    for ule in ules:
        if line.protocol == 'sip':
            extension = extension_dao.get(ule.extension_id)
            _populate_sip_line(config, confregistrar, line, extension)
        elif line.protocol == 'sccp':
            _populate_sccp_line(config, confregistrar)


def _populate_sip_line(config, confregistrar, line, extension):
        if 'sip_lines' not in config['raw_config']:
            config['raw_config']['sip_lines'] = dict()
        config['raw_config']['sip_lines'][str(line.num)] = dict()
        line_dict = config['raw_config']['sip_lines'][str(line.num)]
        line_dict['auth_username'] = line.username
        line_dict['username'] = line.username
        line_dict['password'] = line.secret
        line_dict['display_name'] = line.callerid
        line_dict['number'] = extension.exten
        line_dict['registrar_ip'] = confregistrar['registrar_main']
        line_dict['proxy_ip'] = confregistrar['proxy_main']
        if 'proxy_backup' in confregistrar and len(confregistrar['proxy_backup']) > 0:
            line_dict['backup_registrar_ip'] = confregistrar['registrar_backup']
            line_dict['backup_proxy_ip'] = confregistrar['proxy_backup']
        provd_connector.config_manager.update(config)


def _populate_sccp_line(config, confregistrar):
        config['raw_config']['sccp_call_managers'] = dict()
        config['raw_config']['sccp_call_managers'][1] = dict()
        config['raw_config']['sccp_call_managers'][1]['ip'] = confregistrar['proxy_main']
        if 'proxy_backup' in confregistrar and len(confregistrar['proxy_backup']) > 0:
            config['raw_config']['sccp_call_managers'][2] = dict()
            config['raw_config']['sccp_call_managers'][2]['ip'] = confregistrar['proxy_backup']
        provd_connector.config_manager.update(config)


def remove_line_from_device(device_id, line):
    device = device_dao.get(device_id)
    config = provd_connector.config_manager.get(device.deviceid)
    del config['raw_config']['sip_lines'][str(line.num)]
    if len(config['raw_config']['sip_lines']) == 0:
        # then we reset to autoprov
        _reset_config(config)
        reset_to_autoprov(device.deviceid)
    provd_connector.config_manager.update(config)


def reset_to_autoprov(deviceid):
    device = provd_connector.device_manager.get(deviceid)
    new_configid = provd_connector.config_manager.autocreate()
    device['config'] = new_configid
    provd_connector.device_manager.update(device)


def _reset_config(config):
    del config['raw_config']['sip_lines']
    if 'funckeys' in config['raw_config']:
        del config['raw_config']['funckeys']
