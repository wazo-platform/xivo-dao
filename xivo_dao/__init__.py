# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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

from xivo_dao.helpers import db_manager
from xivo_dao.helpers import bus_manager
from xivo.config_helper import ConfigParser, ErrorHandler


class BusContext(object):

    def __init__(self, bus_config):
        self._bus_config = bus_config

    def new_producer(self):
        from xivo_bus.ctl.producer import BusProducer
        return BusProducer(self._bus_config)

    def exchange_name(self):
        return self._bus_config.exchange_name

    def exchange_type(self):
        return self._bus_config.exchange_type

    def exchange_durable(self):
        return self._bus_config.exchange_durable

    @classmethod
    def new_from_config(cls, config):
        from xivo_bus.ctl.config import BusConfig
        bus_config = BusConfig(**config['bus'])
        return cls(bus_config)


class DBContext(object):

    def __init__(self, url):
        self._url = url

    def new_engine(self):
        from sqlalchemy import create_engine
        return create_engine(self._url)

    @classmethod
    def new_from_config(cls, config):
        url = config.get('db_uri', 'postgresql://asterisk:proformatique@localhost/asterisk')
        return cls(url)


def init_bus(bus_context):
    bus_manager.on_bus_context_update(bus_context)


def init_db(db_context):
    db_manager.on_db_context_update(db_context)


def init_bus_from_config(config):
    init_bus(BusContext.new_from_config(config))


def init_db_from_config(config):
    init_db(DBContext.new_from_config(config))


def new_default_config():
    original_config = {
        'config_file': '/etc/xivo-dao/config.yml',
        'extra_config_files': '/etc/xivo-dao/conf.d',
    }
    config_parser = ConfigParser(ErrorHandler())
    return config_parser.read_config_file_hierarchy(original_config)


init_db(DBContext.new_from_config(new_default_config()))
