# -*- coding: utf-8 -*-
#
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

from urllib2 import HTTPError

from xivo_dao.data_handler.device.model import DeviceOrdering
from xivo_dao.data_handler.device import provd_converter
from xivo_dao.data_handler.exception import ElementNotExistsError, \
    ElementDeletionError, ElementCreationError, InvalidParametersError, \
    ElementEditionError
from xivo_dao.helpers import provd_connector
from xivo_dao.helpers.abstract_model import SearchResult

DEFAULT_ORDER = [DeviceOrdering.ip, DeviceOrdering.mac]


def get(device_id):
    device, config = fetch_device_and_config(device_id)
    if not device:
        raise ElementNotExistsError('device', id=device_id)
    return provd_converter.to_model(device, config)


def fetch_device_and_config(device_id):
    device = _find_device_from_provd(device_id)

    config = None
    if device:
        config = _find_config_from_device(device)
    return device, config


def _find_config_from_device(device):
    config = None
    if 'config' in device:
        config_id = device['config']
        config = _get_config_from_provd(config_id)
    return config


def _find_device_from_provd(device_id):
    try:
        device = provd_connector.device_manager().get(device_id)
    except HTTPError as e:
        if e.code == 404:
            return None
        raise
    return device


def _get_config_from_provd(config_id):
    config = provd_connector.config_manager().find({'id': config_id})
    if not config:
        raise ElementNotExistsError('device config', id=config_id)
    return config[0]


def _find_provd_config(provd_device):
    if 'config' not in provd_device:
        return None

    config_manager = provd_connector.config_manager()

    provd_config = config_manager.get(provd_device['config'])

    return provd_config


def find(device_id):
    device, config = fetch_device_and_config(device_id)
    if device:
        return provd_converter.to_model(device, config)
    return None


def find_all(order=None, direction=None, limit=None, skip=None, search=None):
    provd_devices = find_devices_ordered(order, direction)
    provd_devices = filter_list(search, provd_devices)
    total = len(provd_devices)
    provd_devices = paginate_devices(skip, limit, provd_devices)
    items = convert_devices_to_model(provd_devices)

    return SearchResult(total=total, items=items)


def find_devices_ordered(order, direction):
    parameters = _convert_provd_parameters(order, direction)

    device_manager = provd_connector.device_manager()
    return device_manager.find(**parameters)


def paginate_devices(skip, limit, devices):
    skip = skip or 0
    if limit:
        devices = devices[skip:skip + limit]
    else:
        devices = devices[skip:]
    return devices


def convert_devices_to_model(devices):
    devices_configs = [(device, _find_config_from_device(device)) for device in devices]
    return [provd_converter.to_model(device, config) for device, config in devices_configs]


def filter_list(search, devices):
    if search is None:
        return devices

    found = []
    search = search.lower().strip()

    for device in devices:
        if _device_matches_search(search, device):
            found.append(device)

    return found


def _device_matches_search(search, device):
    for key in provd_converter.PROVD_DEVICE_KEYS:
        if key in device and search in unicode(device[key]).lower():
            return True
    return False


def _convert_provd_parameters(order, direction):
    parameters = {}

    sort = _convert_order_and_direction(order, direction)
    if sort:
        parameters['sort'] = sort

    return parameters


def _convert_order_and_direction(order, direction):
    if direction and not order:
        raise InvalidParametersError("cannot use a direction without an order")

    if not order:
        return None

    if direction == 'asc':
        sort_direction = 1
    elif direction == 'desc':
        sort_direction = -1
    else:
        sort_direction = 1

    return (order, sort_direction)


def delete(device):
    _delete_provd_device(device)
    _delete_provd_config(device)


def _delete_provd_device(device):
    provd_device_manager = provd_connector.device_manager()
    try:
        provd_device_manager.remove(device.id)
    except HTTPError as e:
        if e.code == 404:
            raise ElementNotExistsError('Device', id=device.id)
        raise e
    except Exception as e:
        raise ElementDeletionError('Device', e)


def _delete_provd_config(device):
    provd_config_manager = provd_connector.config_manager()
    try:
        provd_config_manager.remove(device.id)
    except Exception:
        pass


def create(device):
    device.id = generate_device_id()

    provd_device, provd_config = provd_converter.to_source(device)
    _create_provd_device(device.id, provd_device)
    _create_provd_config(device.id, provd_config)

    return device


def _create_provd_device(device_id, provd_device):
    device_manager = provd_connector.device_manager()

    try:
        device_manager.update(provd_device)
    except Exception as e:
        device_manager.remove(device_id)
        raise ElementCreationError('device', e)


def _create_provd_config(device_id, provd_config):
    config_manager = provd_connector.config_manager()

    try:
        config_manager.add(provd_config)
    except Exception as e:
        device_manager = provd_connector.device_manager()
        device_manager.remove(device_id)
        raise ElementCreationError('device', e)


def generate_device_id():
    device_manager = provd_connector.device_manager()
    try:
        return device_manager.add({})
    except Exception as e:
        raise ElementCreationError('device', e)


def edit(device):
    device_manager = provd_connector.device_manager()

    provd_device = device_manager.get(device.id)
    provd_config = _find_provd_config(provd_device)

    provd_device, provd_config = provd_converter.build_edit(device, provd_device, provd_config)

    if provd_config:
        _update_provd_config(provd_config)

    _update_provd_device(provd_device)


def _update_provd_config(provd_config):
    config_manager = provd_connector.config_manager()
    try:
        config_manager.update(provd_config)
    except Exception as e:
        raise ElementEditionError('device', e)


def _update_provd_device(provd_device):
    device_manager = provd_connector.device_manager()
    try:
        device_manager.update(provd_device)
    except Exception as e:
        raise ElementEditionError('device', e)


def mac_exists(mac):
    device_manager = provd_connector.device_manager()
    existing_macs = device_manager.find({'mac': mac})
    return len(existing_macs) > 0


def plugin_exists(plugin):
    plugin_manager = provd_connector.plugin_manager()
    existing_plugins = plugin_manager.plugins()
    return plugin in existing_plugins


def template_id_exists(plugin):
    config_manager = provd_connector.config_manager()
    existing_templates = config_manager.find({
        'X_type': 'device',
        'id': plugin})
    return len(existing_templates) > 0
