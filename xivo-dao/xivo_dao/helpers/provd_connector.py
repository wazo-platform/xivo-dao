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

from provd.rest.client.client import new_provisioning_client


def config_manager():
    provisioning_client = _provd_client()
    return provisioning_client.config_manager()


def device_manager():
    provisioning_client = _provd_client()
    return provisioning_client.device_manager()


def plugin_manager():
    provisioning_client = _provd_client()
    return provisioning_client.plugin_manager()


def _provd_client():
    provd_config = _get_provd_config()
    provd_url = "http://%s:%s/provd" % (provd_config['XIVO_PROVD_REST_NET4_IP'], provd_config['XIVO_PROVD_REST_PORT'])
    return new_provisioning_client(provd_url)


def _get_provd_config():
    config = {}
    with open('/etc/xivo/common.conf', 'r') as fobj:
        for line in fobj:
            if not line.startswith('#') and line.startswith('XIVO_PROVD'):
                (key, _, value) = line.partition("=")
                config[key] = value.replace('"', '')
    return config
