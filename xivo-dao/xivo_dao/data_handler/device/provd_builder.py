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

from xivo_dao.data_handler.device.model import Device
from xivo_dao.helpers import provd_connector
from xivo import caller_id
from xivo_dao.data_handler.exception import ProvdError


def build_create(device):
    provd_device = _create_provd_device(device)
    provd_config = _create_provd_config(device)

    return (provd_device, provd_config)


def _create_provd_device(device):
    parameters = _filter_device_parameters(device)
    parameters['config'] = device.id

    return parameters


def _filter_device_parameters(device):
    parameters = {}

    for key in Device.PROVD_KEYS:
        value = getattr(device, key)
        if value is not None:
            parameters[key] = value

    if 'mac' in parameters:
        parameters['mac'] = parameters['mac'].lower()

    return parameters


def _create_provd_config(device):
    parameters = {
        'id': device.id,
        'deletable': True,
        'parent_ids': _build_parent_ids(device),
        'configdevice': device.template_id or 'defaultconfigdevice',
        'raw_config': {}
    }

    return parameters


def _build_parent_ids(device):
    parent_ids = ['base', device.template_id or 'defaultconfigdevice']
    return parent_ids


def link_device_config(device):
    provd_device_manager = provd_connector.device_manager()
    try:
        provd_device = provd_device_manager.get(device.id)
        provd_device['config'] = device.id
        provd_device_manager.update(provd_device)
    except Exception as e:
        raise ProvdError('error while linking config to device.', e)


def populate_sip_line(config, confregistrar, line, extension):
    provd_config_manager = provd_connector.config_manager()
    if 'sip_lines' not in config['raw_config']:
        config['raw_config']['sip_lines'] = dict()
    config['raw_config']['sip_lines'][str(line.device_slot)] = dict()
    line_dict = config['raw_config']['sip_lines'][str(line.device_slot)]
    line_dict['auth_username'] = line.name
    line_dict['username'] = line.name
    line_dict['password'] = line.secret
    line_dict['display_name'] = caller_id.extract_displayname(line.callerid)
    line_dict['number'] = extension.exten
    line_dict['registrar_ip'] = confregistrar['registrar_main']
    line_dict['proxy_ip'] = confregistrar['proxy_main']
    if 'proxy_backup' in confregistrar and len(confregistrar['proxy_backup']) > 0:
        line_dict['backup_registrar_ip'] = confregistrar['registrar_backup']
        line_dict['backup_proxy_ip'] = confregistrar['proxy_backup']
    provd_config_manager.update(config)


def populate_sccp_line(config, confregistrar):
    provd_config_manager = provd_connector.config_manager()
    config['raw_config']['sccp_call_managers'] = dict()
    config['raw_config']['sccp_call_managers'][1] = dict()
    config['raw_config']['sccp_call_managers'][1]['ip'] = confregistrar['proxy_main']
    if 'proxy_backup' in confregistrar and len(confregistrar['proxy_backup']) > 0:
        config['raw_config']['sccp_call_managers'][2] = dict()
        config['raw_config']['sccp_call_managers'][2]['ip'] = confregistrar['proxy_backup']
    provd_config_manager.update(config)


def build_edit(device, provd_device, provd_config):
    new_provd_device = _update_provd_device(device, provd_device)
    new_provd_config = _update_provd_config(device, provd_config)

    return (new_provd_device, new_provd_config)


def generate_autoprov_config():
    provd_config_manager = provd_connector.config_manager()
    new_configid = provd_config_manager.autocreate()
    return new_configid


def reset_config(config):
    _reset_funckeys_config(config)
    _reset_sip_config(config)


def _reset_funckeys_config(config):
    if 'funckeys' in config['raw_config']:
        del config['raw_config']['funckeys']


def _reset_sip_config(config):
    if 'sip_lines' in config['raw_config']:
        del config['raw_config']['sip_lines']


def _update_provd_device(device, provd_device):
    parameters = _filter_device_parameters(device)
    provd_device.update(parameters)
    return provd_device


def _update_provd_config(device, provd_config):
    if not provd_config:
        return

    if 'configdevice' in provd_config and 'parent_ids' in provd_config:
        _remove_old_parent_ids(device, provd_config)
        _update_template_id(device, provd_config)
        _update_parent_ids(device, provd_config)
    else:
        _update_template_id(device, provd_config)

    return provd_config


def _remove_old_parent_ids(device, provd_device):
    if provd_device['configdevice'] in provd_device['parent_ids']:
        provd_device['parent_ids'].remove(provd_device['configdevice'])


def _update_template_id(device, provd_device):
    provd_device['configdevice'] = device.template_id or 'defaultconfigdevice'


def _update_parent_ids(device, provd_device):
    if device.template_id not in provd_device['parent_ids']:
        provd_device['parent_ids'].append(device.template_id)
