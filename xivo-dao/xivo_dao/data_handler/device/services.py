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

from xivo_dao.data_handler.device import dao as device_dao
from xivo_dao.helpers import provd_connector


def get(device_id):
    return device_dao.get(device_id)


def get_by_deviceid(session, device_id):
    return device_dao.get_by_deviceid(device_id)


def remove_line_from_device(device_id, linenum):
    device = device_dao.get(device_id)
    config = provd_connector.config_manager.get(device.deviceid)
    del config["raw_config"]["sip_lines"][str(linenum)]
    if len(config["raw_config"]["sip_lines"]) == 0:
        # then we reset to autoprov
        _reset_config(config)
        reset_to_autoprov(device.deviceid)
    provd_connector.config_manager.update(config)


def reset_to_autoprov(deviceid):
    device = provd_connector.device_manager.get(deviceid)
    new_configid = provd_connector.config_manager.autocreate()
    device["config"] = new_configid
    provd_connector.device_manager.update(device)


def _reset_config(config):
    del config["raw_config"]["sip_lines"]
    if "funckeys" in config["raw_config"]:
        del config["raw_config"]["funckeys"]
