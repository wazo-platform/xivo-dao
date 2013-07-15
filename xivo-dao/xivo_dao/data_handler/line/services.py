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

from . import notifier
from . import dao
from xivo_dao.data_handler.exception import MissingParametersError, \
    InvalidParametersError
from urllib2 import URLError
from xivo_dao.helpers import provd_connector
from xivo_dao.data_handler.device import services as device_services


def get(line_id):
    return dao.get(line_id)


def get_by_user_id(user_id):
    return dao.get_by_user_id(user_id)


def get_by_number_context(number, context):
    return dao.get_by_number_context(number, context)


def create(line):
    _validate(line)
    line = dao.create(line)
    notifier.created(line)
    return line


def delete(line):
    dao.delete(line)
    if hasattr(line, 'deviceid') and line.deviceid is not None:
        try:
            device_services.remove_line_from_device(line.deviceid, line.num)
        except URLError as e:
            raise provd_connector.ProvdError(str(e))
    notifier.deleted(line)


def _validate(line):
    _check_missing_parameters(line)
    _check_invalid_parameters(line)


def _check_missing_parameters(line):
    missing = line.missing_parameters()
    if missing:
        raise MissingParametersError(missing)


def _check_invalid_parameters(line):
    invalid_parameters = []
    if invalid_parameters:
        raise InvalidParametersError(invalid_parameters)
