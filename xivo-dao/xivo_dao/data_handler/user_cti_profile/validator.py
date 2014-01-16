# -*- coding: utf-8 -*-
#
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
from xivo_dao.data_handler.exception import MissingParametersError, \
    ElementNotExistsError, NonexistentParametersError, InvalidParametersError
from xivo_dao.data_handler.cti_profile import dao as cti_profile_dao
from xivo_dao.data_handler.user import dao as user_dao
from xivo_dao.data_handler.user_cti_profile import dao as user_cti_profile_dao

def validate_association(user_cti_profile):
    _validate_missing_params(user_cti_profile)
    _validate_cti_profile_exists(user_cti_profile)
    _validate_user_exists(user_cti_profile)
    _validate_user_has_no_profile(user_cti_profile)

def _validate_missing_params(user_cti_profile):
    missing = user_cti_profile.missing_parameters()
    if len(missing) > 0:
        raise MissingParametersError(missing)

def _validate_cti_profile_exists(user_cti_profile):
    try:
        cti_profile_dao.get(user_cti_profile.cti_profile_id)
    except ElementNotExistsError:
        raise NonexistentParametersError(cti_profile=user_cti_profile.cti_profile_id)

def _validate_user_exists(user_cti_profile):
    try:
        user_dao.get(user_cti_profile.user_id)
    except ElementNotExistsError:
        raise NonexistentParametersError(user=user_cti_profile.user_id)

def _validate_user_has_no_profile(user_cti_profile):
    try:
        user_cti_profile_dao.get_profile_by_userid(user_cti_profile.user_id)
        raise InvalidParametersError(['user with id %s already has a CTI profile' % user_cti_profile.user_id])
    except ElementNotExistsError:
        return
