# -*- coding: utf-8 -*-

# Copyright (C) 2014-2015 Avencall
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
from xivo_bus.ctl.producer import BusProducer
from xivo_dao.helpers import config

_once = moresynchro.Once()
_bus_client = BusProducer()


def _init_bus():
    _bus_client.connect()
    _bus_client.declare_exchange(config.BUS_EXCHANGE_NAME,
                                 config.BUS_EXCHANGE_TYPE,
                                 durable=config.BUS_EXCHANGE_DURABLE)


def send_bus_event(event, routing_key):
    _once.once(_init_bus)
    _bus_client.publish_event(config.BUS_EXCHANGE_NAME,
                              routing_key,
                              event)
