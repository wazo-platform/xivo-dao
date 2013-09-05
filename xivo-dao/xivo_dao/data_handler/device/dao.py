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
from xivo_dao.alchemy.devicefeatures import DeviceFeatures as DeviceSchema
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.data_handler.device.model import Device, DeviceOrdering
from xivo_dao.data_handler.exception import ElementNotExistsError, \
    ElementDeletionError, ElementCreationError
from sqlalchemy.exc import SQLAlchemyError
from xivo_dao.helpers import provd_connector


DEFAULT_ORDER = [DeviceOrdering.ip, DeviceOrdering.mac]


@daosession
def get(session, device_id):
    try:
        res = (session.query(DeviceSchema).filter(DeviceSchema.id == int(device_id))).first()
    except ValueError:
        raise ElementNotExistsError('Device', id=device_id)

    if not res:
        raise ElementNotExistsError('Device', id=device_id)

    return Device.from_data_source(res)


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
def create(session, device):
    device_row = device.to_data_source(DeviceSchema)
    session.begin()
    session.add(device_row)

    try:
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise ElementCreationError('Device', e)
    except IntegrityError as e:
        session.rollback()
        raise ElementCreationError('Device', e)

    device.id = device_row.id

    return device


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


def mac_exists(mac):
    device_manager = provd_connector.device_manager()
    existing_macs = device_manager.find({'mac': mac})
    return len(existing_macs) > 0


def plugin_exists(plugin):
    plugin_manager = provd_connector.plugin_manager()
    existing_plugins = plugin_manager.installed(plugin)
    return len(existing_plugins) > 0


def template_id_exists(plugin):
    config_manager = provd_connector.config_manager()
    existing_templates = config_manager.find({
        'X_type': 'device',
        'id': plugin})
    return len(existing_templates) > 0
