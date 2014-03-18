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

from xivo_dao.data_handler.exception import MissingParametersError, InvalidParametersError

LIVE_RELOAD_PARAM = 'enabled'


def validate_live_reload_data(data):
    _validate_data_has_param(data, LIVE_RELOAD_PARAM)
    _validate_no_extra_params(data, LIVE_RELOAD_PARAM)


def _validate_data_has_param(data, mandatory_param):
    if mandatory_param not in data:
        raise MissingParametersError(mandatory_param)


def _validate_no_extra_params(data, LIVE_RELOAD_PARAM):
    if len(data) > 1:
        raise InvalidParametersError('A single parameter %s is expected' % LIVE_RELOAD_PARAM)
