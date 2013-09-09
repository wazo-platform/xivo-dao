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
from urllib2 import HTTPError


from xivo_dao.alchemy.devicefeatures import DeviceFeatures as DeviceSchema
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.data_handler.device.model import Device, DeviceOrdering
from xivo_dao.data_handler.exception import ElementNotExistsError, \
    ElementDeletionError, ElementCreationError
from sqlalchemy.exc import SQLAlchemyError
from xivo_dao.helpers import provd_connector


DEFAULT_ORDER = [DeviceOrdering.ip, DeviceOrdering.mac]


def get(device_id):
    provd_device = _get_provd_device(device_id)
    provd_config = _find_provd_config(provd_device)

    return Device.from_provd(provd_device, provd_config)


def _get_provd_device(device_id):
    device_manager = provd_connector.device_manager()

    try:
        provd_device = device_manager.get(device_id)
    except HTTPError as e:
        if e.code == 404:
            raise ElementNotExistsError('Device', id=device_id)
        raise e

    return provd_device


def _find_provd_config(provd_device):
    if 'config' not in provd_device:
        return None

    config_manager = provd_connector.config_manager()

    provd_config = config_manager.get(provd_device['config'])

    return provd_config


@daosession
def get_by_deviceid(session, device_id):
    res = (session.query(DeviceSchema).filter(DeviceSchema.deviceid == device_id)).first()

    if not res:
        raise ElementNotExistsError('Device', deviceid=device_id)

    return Device.from_data_source(res)


@daosession
def find(session, device_id):
    device_row = session.query(DeviceSchema).filter(DeviceSchema.id == device_id).first()

    if device_row:
        return Device.from_data_source(device_row)
    return None


@daosession
def find_all(session):
    rows = (session.query(DeviceSchema).all())

    return [Device.from_data_source(row) for row in rows]


@daosession
def delete(session, device):
    session.begin()
    try:
        nb_row_affected = session.query(DeviceSchema).filter(DeviceSchema.id == device.id).delete()
        session.commit()
    except SQLAlchemyError, e:
        session.rollback()
        raise ElementDeletionError('Device', e)

    if nb_row_affected == 0:
        raise ElementDeletionError('Device', 'device_id %s not exist' % device.id)

    return nb_row_affected


def create(device):
    _create_provd_device(device)
    _create_provd_config(device)

    return device


def _create_provd_device(device):
    device_manager = provd_connector.device_manager()

    provd_device = device.to_provd_device()

    try:
        device_id = device_manager.add(provd_device)
    except Exception as e:
        raise ElementCreationError('device', e)

    device.id = device_id

    provd_device = dict(provd_device)
    provd_device['id'] = device_id
    provd_device['config'] = device_id

    try:
        device_manager.update(provd_device)
    except Exception as e:
        device_manager.remove(device_id)
        raise ElementCreationError('device', e)


def _create_provd_config(device):
    config_manager = provd_connector.config_manager()
    provd_config = device.to_provd_config()

    try:
        config_manager.add(provd_config)
    except Exception as e:
        device_manager = provd_connector.device_manager()
        device_manager.remove(device.id)
        raise ElementCreationError('device', e)


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
