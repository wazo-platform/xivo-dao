# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
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

from xivo import moresynchro
from xivo_bus.ctl.client import BusCtlClient
from xivo_dao.helpers import config

_once = moresynchro.Once()
bus_client = BusCtlClient()


def _init_bus():
    bus_client.connect()
    bus_client.declare_exchange(config.BUS_EXCHANGE_NAME,
                                config.BUS_EXCHANGE_TYPE,
                                durable=config.BUS_EXCHANGE_DURABLE)


def send_bus_command(command):
    # TODO rename to send_bus_event
    _once.once(_init_bus)
    bus_client.publish_event(config.BUS_EXCHANGE_NAME,
                             config.BUS_BINDING_KEY,
                             command)
