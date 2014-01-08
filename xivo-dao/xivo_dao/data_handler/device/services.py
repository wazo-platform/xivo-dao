# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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

from xivo_dao.helpers import provd_connector
from xivo_dao.data_handler.user_line_extension import dao as user_line_extension_dao
from xivo_dao.data_handler.extension import dao as extension_dao
from xivo_dao.data_handler.line import dao as line_dao
from xivo_dao.data_handler.exception import InvalidParametersError, ProvdError
from xivo_dao.data_handler.device import provd_converter


def get(device_id):
    return dao.get(device_id)


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
    validator.validate_delete(device)
    dao.delete(device)
    line_dao.reset_device(device.id)
    notifier.deleted(device)


def associate_line_to_device(device, line):
    line.device = str(device.id)
    line_dao.edit(line)
    provd_converter.link_device_config(device)
    rebuild_device_config(device)


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
            provd_converter.populate_sip_line(config, confregistrar, line, extension)
        elif line.protocol == 'sccp':
            provd_converter.populate_sccp_line(config, confregistrar)


def remove_line_from_device(device, line):
    provd_config_manager = provd_connector.config_manager()
    try:
        config = provd_config_manager.get(device.id)
        if 'sip_lines' in config['raw_config']:
            del config['raw_config']['sip_lines'][str(line.device_slot)]
            if len(config['raw_config']['sip_lines']) == 0:
                provd_converter.reset_config(config)
                reset_to_autoprov(device)
            provd_config_manager.update(config)
    except URLError as e:
        raise ProvdError('error during remove line %s from device %s' % (line.device_slot, device.id), e)


def remove_all_line_from_device(device):
    provd_config_manager = provd_connector.config_manager()
    try:
        config = provd_config_manager.get(device.id)
        provd_converter.reset_config(config)
        provd_config_manager.update(config)
    except URLError as e:
        raise ProvdError('error during remove all lines from device %s' % (device.id), e)


def reset_to_autoprov(device):
    provd_device_manager = provd_connector.device_manager()
    try:
        provd_device = provd_device_manager.get(device.id)
        provd_device['config'] = provd_converter.generate_autoprov_config()
        provd_device_manager.update(provd_device)
    except Exception as e:
        raise ProvdError('error while synchronize device.', e)
    else:
        remove_all_line_from_device(device)
        line_dao.reset_device(device.id)


def synchronize(device):
    try:
        provd_device_manager = provd_connector.device_manager()
        provd_device_manager.synchronize(device.id)
    except Exception as e:
        raise ProvdError('error while reset to autoprov.', e)
