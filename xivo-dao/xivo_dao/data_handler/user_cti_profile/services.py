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

from xivo_dao.data_handler.user_cti_profile import validator, dao, notifier
from xivo_dao.data_handler.user_cti_profile.model import UserCtiProfile
from xivo_dao.data_handler.user_cti_profile.exceptions import UserCtiProfileNotExistsError


def associate(user_cti_profile):
    validator.validate_association(user_cti_profile)
    dao.associate(user_cti_profile)
    notifier.associated(user_cti_profile)
    return user_cti_profile


def get(user_id):
    cti_profile = dao.find_profile_by_userid(user_id)
    if cti_profile is None:
        raise UserCtiProfileNotExistsError('user_cti_profile')
    return UserCtiProfile(user_id=user_id, cti_profile_id=cti_profile.id)


def dissociate(user_cti_profile):
    validator.validate_dissociation(user_cti_profile)
    dao.dissociate(user_cti_profile)
    notifier.dissociated(user_cti_profile)
