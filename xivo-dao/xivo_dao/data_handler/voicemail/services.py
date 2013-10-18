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

from xivo_dao.data_handler.language import dao as language_dao
from xivo_dao.data_handler.voicemail import dao as voicemail_dao
from xivo_dao.helpers import sysconfd_connector
from xivo_dao.data_handler.voicemail import notifier
from xivo_dao.helpers.sysconfd_connector import SysconfdError
from xivo_dao.data_handler.exception import MissingParametersError, \
    InvalidParametersError, ElementAlreadyExistsError, ElementNotExistsError, \
    NonexistentParametersError
from xivo_dao.helpers.validator import is_positive_number, is_context_exist


def find_all(skip=None, limit=None, order=None, direction=None, search=None):
    return voicemail_dao.find_all(skip=skip, limit=limit, order=order, direction=direction, search=search)


def find_all_timezone():
    return voicemail_dao.find_all_timezone()


def get_by_number_context(number, context):
    return voicemail_dao.get_by_number_context(number, context)


def get(voicemail_id):
    return voicemail_dao.get(voicemail_id)


def create(voicemail):
    _validate(voicemail)
    _check_for_existing_voicemail(voicemail)
    voicemail = voicemail_dao.create(voicemail)
    notifier.created(voicemail)
    return voicemail


def edit(voicemail):
    _validate(voicemail)
    voicemail_dao.edit(voicemail)
    notifier.edited(voicemail)


def delete(voicemail):
    voicemail_dao.delete(voicemail)
    notifier.deleted(voicemail)
    try:
        sysconfd_connector.delete_voicemail_storage(voicemail.number, voicemail.context)
    except Exception as e:
        raise SysconfdError(str(e))


def _validate(voicemail):
    _check_missing_parameters(voicemail)
    _check_invalid_parameters(voicemail)
    _check_nonexistent_parameters(voicemail)


def _check_missing_parameters(voicemail):
    missing = voicemail.missing_parameters()
    if missing:
        raise MissingParametersError(missing)


def _check_invalid_parameters(voicemail):
    invalid_parameters = []
    if voicemail.name is not None and not voicemail.name:
        invalid_parameters.append('name')
    if voicemail.number is not None and not is_positive_number(voicemail.number):
        invalid_parameters.append('number')
    if voicemail.max_messages is not None and not is_positive_number(voicemail.max_messages):
        invalid_parameters.append('max_messages')
    if voicemail.password is not None and not is_positive_number(voicemail.password):
        invalid_parameters.append('password')
    if invalid_parameters:
        raise InvalidParametersError(invalid_parameters)


def _check_nonexistent_parameters(voicemail):
    nonexistent_parameters = {}
    if not is_context_exist(voicemail.context):
        nonexistent_parameters['context'] = voicemail.context
    if voicemail.language is not None and voicemail.language not in language_dao.find_all():
        nonexistent_parameters['language'] = voicemail.language
    if voicemail.timezone is not None and voicemail.timezone not in voicemail_dao.find_all_timezone():
        nonexistent_parameters['timezone'] = voicemail.timezone
    if nonexistent_parameters:
        raise NonexistentParametersError(**nonexistent_parameters)


def _check_for_existing_voicemail(voicemail):
    try:
        if voicemail_dao.get_by_number_context(voicemail.number, voicemail.context):
            number_at_context = voicemail.number_at_context
            raise ElementAlreadyExistsError('Voicemail', number_at_context)
    except ElementNotExistsError:
        return
