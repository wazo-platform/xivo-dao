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

from . import dao
from . import validator
from .model import DeviceOrdering
from . import notifier

from urllib2 import URLError

from xivo import caller_id
from xivo_dao.helpers import provd_connector
from xivo_dao.data_handler.user_line_extension import dao as user_line_extension_dao
from xivo_dao.data_handler.extension import dao as extension_dao
from xivo_dao.data_handler.line import dao as line_dao
from xivo_dao.data_handler.exception import InvalidParametersError, ProvdError


def get(device_id):
    return dao.get(device_id)


def total():
    return dao.total()


def find_all(order=None, direction=None, skip=None, limit=None, search=None):
    if order:
        DeviceOrdering.validate_order(order)
    if direction:
        DeviceOrdering.validate_direction(direction)
    if skip:
        _validate_skip(skip)
    if limit:
        _validate_limit(limit)

    return dao.find_all(order=order, direction=direction, skip=skip, limit=limit, search=search)


def _validate_skip(skip):
    if not (isinstance(skip, int) and skip > 0):
        raise InvalidParametersError(["skip must be a positive number"])
    return int(skip)


def _validate_limit(limit):
    if not (isinstance(limit, int) and limit > 0):
        raise InvalidParametersError(["limit must be a positive number"])
    return int(limit)


def create(device):
    validator.validate_create(device)
    device = dao.create(device)
    notifier.created(device)
    return device


def edit(device):
    validator.validate_edit(device)
    dao.edit(device)
    notifier.edited(device)
    return device


def delete(device):
    dao.delete(device)
    line_dao.reset_device(device.id)
    notifier.deleted(device)


def _generate_new_deviceid(device):
    provd_device_manager = provd_connector.device_manager()
    device_dict = device.to_data_dict()
    if 'id' in device_dict:
        del device_dict['id']
    deviceid = provd_device_manager.add(device_dict)
    return deviceid


def associate_line_to_device(device, line):
    line.device = str(device.id)
    line_dao.edit(line)
    _link_device_config(device)
    rebuild_device_config(device)


def _link_device_config(device):
    provd_device_manager = provd_connector.device_manager()
    try:
        provd_device = provd_device_manager.get(device.id)
        provd_device['config'] = device.id
        provd_device_manager.update(provd_device)
    except Exception as e:
        raise ProvdError('error while linking config to device.', e)


def rebuild_device_config(device):
    lines_device = line_dao.find_all_by_device_id(device.id)
    try:
        for line in lines_device:
            build_line_for_device(device, line)
    except Exception as e:
        raise ProvdError('error while rebuilding config device.', e)


def build_line_for_device(device, line):
    provd_config_manager = provd_connector.config_manager()
    config = provd_config_manager.get(device.id)
    confregistrar = provd_config_manager.get(line.configregistrar)
    ules = user_line_extension_dao.find_all_by_line_id(line.id)
    for ule in ules:
        if line.protocol == 'sip':
            extension = extension_dao.get(ule.extension_id)
            _populate_sip_line(config, confregistrar, line, extension)
        elif line.protocol == 'sccp':
            _populate_sccp_line(config, confregistrar)


def _populate_sip_line(config, confregistrar, line, extension):
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


def _populate_sccp_line(config, confregistrar):
    provd_config_manager = provd_connector.config_manager()
    config['raw_config']['sccp_call_managers'] = dict()
    config['raw_config']['sccp_call_managers'][1] = dict()
    config['raw_config']['sccp_call_managers'][1]['ip'] = confregistrar['proxy_main']
    if 'proxy_backup' in confregistrar and len(confregistrar['proxy_backup']) > 0:
        config['raw_config']['sccp_call_managers'][2] = dict()
        config['raw_config']['sccp_call_managers'][2]['ip'] = confregistrar['proxy_backup']
    provd_config_manager.update(config)


def remove_line_from_device(device, line):
    provd_config_manager = provd_connector.config_manager()
    try:
        config = provd_config_manager.get(device.id)
        if 'sip_lines' in config['raw_config']:
            del config['raw_config']['sip_lines'][str(line.device_slot)]
            if len(config['raw_config']['sip_lines']) == 0:
                # then we reset to autoprov
                _reset_config(config)
                reset_to_autoprov(device)
            provd_config_manager.update(config)
    except URLError as e:
        raise ProvdError('error during remove line %s from device %s' % (line.device_slot, device.id), e)


def reset_to_autoprov(device):
    provd_device_manager = provd_connector.device_manager()
    provd_config_manager = provd_connector.config_manager()
    try:
        device = provd_device_manager.get(device.id)
        new_configid = provd_config_manager.autocreate()
        device['config'] = new_configid
        provd_device_manager.update(device)
    except Exception as e:
        raise ProvdError('error while synchronize device.', e)


def synchronize(device):
    try:
        provd_device_manager = provd_connector.device_manager()
        provd_device_manager.synchronize(device.id)
    except Exception as e:
        raise ProvdError('error while reset to autoprov.', e)


def _reset_config(config):
    del config['raw_config']['sip_lines']
    if 'funckeys' in config['raw_config']:
        del config['raw_config']['funckeys']
