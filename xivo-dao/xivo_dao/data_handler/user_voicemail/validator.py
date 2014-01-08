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

from xivo_dao.data_handler.exception import MissingParametersError, ElementNotExistsError, NonexistentParametersError, \
    InvalidParametersError
from xivo_dao.data_handler.user import dao as user_dao
from xivo_dao.data_handler.user_voicemail import dao as user_voicemail_dao
from xivo_dao.data_handler.user_line_extension import dao as ule_dao
from xivo_dao.data_handler.voicemail import dao as voicemail_dao


def validate_association(user_voicemail):
    _validate_missing_parameters(user_voicemail)
    _validate_invalid_parameters(user_voicemail)
    _validate_user_id(user_voicemail)
    _validate_voicemail_id(user_voicemail)
    _validate_user_has_line(user_voicemail)
    _validate_user_does_not_have_a_voicemail(user_voicemail)


def _validate_missing_parameters(user_voicemail):
    missing = user_voicemail.missing_parameters()
    if len(missing) > 0:
        raise MissingParametersError(missing)


def _validate_invalid_parameters(user_voicemail):
    if not isinstance(user_voicemail.enabled, bool):
        raise InvalidParametersError(['enabled must be a boolean'])


def _validate_user_id(user_voicemail):
    try:
        return user_dao.get(user_voicemail.user_id)
    except ElementNotExistsError:
        raise NonexistentParametersError(user=user_voicemail.user_id)


def _validate_voicemail_id(user_voicemail):
    try:
        return voicemail_dao.get(user_voicemail.voicemail_id)
    except ElementNotExistsError:
        raise NonexistentParametersError(voicemail=user_voicemail.voicemail_id)


def _validate_user_has_line(user_voicemail):
    user_lines = ule_dao.find_all_by_user_id(user_voicemail.user_id)
    if len(user_lines) == 0:
        raise InvalidParametersError(['user with id %s does not have any line' % user_voicemail.user_id])


def _validate_user_does_not_have_a_voicemail(user_voicemail):
    try:
        user_voicemail_dao.get_by_user_id(user_voicemail.user_id)
        raise InvalidParametersError(['user with id %s already has a voicemail' % user_voicemail.user_id])
    except ElementNotExistsError:
        pass


def validate_dissociation(user_voicemail):
    _validate_user_id(user_voicemail)
    _validate_voicemail_id(user_voicemail)
