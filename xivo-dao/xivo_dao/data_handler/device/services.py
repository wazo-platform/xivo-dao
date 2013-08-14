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
from . import notifier
import re

from xivo_dao.helpers import provd_connector
from xivo_dao.data_handler.user_line_extension import dao as user_line_extension_dao
from xivo_dao.data_handler.extension import dao as extension_dao
from xivo_dao.data_handler.line import dao as line_dao
from xivo_dao.data_handler.exception import InvalidParametersError, \
    ElementNotExistsError, ElementDeletionError

IP_REGEX = re.compile(r'(1?\d{1,2}|2[0-5]{2})(\.(1?\d{1,2}|2[0-5]{2})){3}$')


def get(device_id):
    return dao.get(device_id)


def get_by_deviceid(session, device_id):
    return dao.get_by_deviceid(device_id)


def find_all():
    return dao.find_all()


def create(device):
    _validate(device)
    device.deviceid = _generate_new_deviceid(device)
    device = dao.create(device)
    notifier.created(device)
    return device


def delete(device):
    try:
        get(device.id)
    except ElementNotExistsError:
        raise ElementDeletionError('Device', 'device_id %s not exist' % device.id)
    _remove_device_from_provd(device)
    dao.delete(device)
    line_dao.reset_device(device.id)
    notifier.deleted(device)


def _remove_device_from_provd(device):
    provd_device_manager = provd_connector.device_manager()
    provd_device_manager.remove(device.deviceid)
    if len(device.config) > 0:
        provd_config_manager = provd_connector.config_manager()
        provd_config_manager.remove(device.deviceid)


def _generate_new_deviceid(device):
    provd_device_manager = provd_connector.device_manager()
    device_dict = device.to_data_dict()
    if 'id' in device_dict:
        del device_dict['id']
    deviceid = provd_device_manager.add(device_dict)
    return deviceid


def _validate(device):
    _check_invalid_parameters(device)


def _check_invalid_parameters(device):
    invalid_parameters = []
    if hasattr(device, 'ip') and not IP_REGEX.match(device.ip):
        invalid_parameters.append('ip')
    if invalid_parameters:
        raise InvalidParametersError(invalid_parameters)


def associate_line_to_device(device, line):
    line.device = str(device.id)
    line_dao.edit(line)
    rebuild_device_config(device)


def rebuild_device_config(device):
    lines_device = line_dao.find_all_by_device_id(device.id)
    for line in lines_device:
        build_line_for_device(device, line)


def build_line_for_device(device, line):
    provd_config_manager = provd_connector.config_manager()
    config = provd_config_manager.get(device.deviceid)
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


def remove_line_from_device(device_id, line):
    device = dao.get(device_id)
    provd_config_manager = provd_connector.config_manager()
    config = provd_config_manager.get(device.deviceid)
    del config['raw_config']['sip_lines'][str(line.num)]
    if len(config['raw_config']['sip_lines']) == 0:
        # then we reset to autoprov
        _reset_config(config)
        reset_to_autoprov(device.deviceid)
    provd_config_manager.update(config)


def reset_to_autoprov(deviceid):
    provd_device_manager = provd_connector.device_manager()
    provd_config_manager = provd_connector.config_manager()
    device = provd_device_manager.get(deviceid)
    new_configid = provd_config_manager.autocreate()
    device['config'] = new_configid
    provd_device_manager.update(device)


def _reset_config(config):
    del config['raw_config']['sip_lines']
    if 'funckeys' in config['raw_config']:
        del config['raw_config']['funckeys']
