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
        if hasattr(device, key):
            parameters[key] = getattr(device, key)

    if 'mac' in parameters:
        parameters['mac'] = parameters['mac'].lower()

    return parameters


def _create_provd_config(device):
    parameters = {
        'id': device.id,
        'deletable': True,
        'parent_ids': _build_parent_ids(device),
        'configdevice': getattr(device, 'template_id', 'defaultconfigdevice'),
        'raw_config': {}
    }

    return parameters


def _build_parent_ids(device):
    parent_ids = ['base', getattr(device, 'template_id', 'defaultconfigdevice')]
    return parent_ids


def build_edit(device, provd_device, provd_config):
    new_provd_device = _update_provd_device(device, provd_device)
    new_provd_config = _update_provd_config(device, provd_config)

    return (new_provd_device, new_provd_config)


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
    provd_device['configdevice'] = getattr(device, 'template_id', 'defaultconfigdevice')


def _update_parent_ids(device, provd_device):
    if device.template_id not in provd_device['parent_ids']:
        provd_device['parent_ids'].append(device.template_id)
