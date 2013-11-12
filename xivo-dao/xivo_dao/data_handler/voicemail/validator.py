# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from xivo_dao.data_handler.voicemail import dao as voicemail_dao
from xivo_dao.data_handler.language import dao as language_dao
from xivo_dao.data_handler.exception import MissingParametersError, \
    InvalidParametersError, ElementAlreadyExistsError, ElementNotExistsError, \
    ElementDeletionError, ElementEditionError, NonexistentParametersError

from xivo_dao.helpers import validator


def validate_create(voicemail):
    validate_model(voicemail)
    validate_number_context(voicemail)


def validate_edit(voicemail):
    validate_model(voicemail)
    validate_existing_number_context(voicemail)
    _check_if_voicemail_linked_on_edit(voicemail)


def validate_delete(voicemail):
    _check_if_voicemail_linked_on_delete(voicemail)


def validate_model(voicemail):
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
    if voicemail.number is not None and not validator.is_positive_number(voicemail.number):
        invalid_parameters.append('number')
    if voicemail.max_messages is not None and not validator.is_positive_number(voicemail.max_messages):
        invalid_parameters.append('max_messages')
    if voicemail.password is not None and not validator.is_positive_number(voicemail.password):
        invalid_parameters.append('password')
    if voicemail.attach_audio is not None and not isinstance(voicemail.attach_audio, bool):
        invalid_parameters.append('attach_audio')
    if voicemail.delete_messages is not None and not isinstance(voicemail.delete_messages, bool):
        invalid_parameters.append('delete_messages')
    if voicemail.ask_password is not None and not isinstance(voicemail.ask_password, bool):
        invalid_parameters.append('ask_password')
    if invalid_parameters:
        raise InvalidParametersError(invalid_parameters)


def _check_nonexistent_parameters(voicemail):
    nonexistent_parameters = {}
    if not validator.is_existing_context(voicemail.context):
        nonexistent_parameters['context'] = voicemail.context
    if voicemail.language is not None and voicemail.language not in language_dao.find_all():
        nonexistent_parameters['language'] = voicemail.language
    if voicemail.timezone is not None and voicemail.timezone not in voicemail_dao.find_all_timezone():
        nonexistent_parameters['timezone'] = voicemail.timezone
    if nonexistent_parameters:
        raise NonexistentParametersError(**nonexistent_parameters)


def validate_number_context(voicemail):
    try:
        if voicemail_dao.get_by_number_context(voicemail.number, voicemail.context):
            number_at_context = voicemail.number_at_context
            raise ElementAlreadyExistsError('Voicemail', number_at_context)
    except ElementNotExistsError:
        return


def validate_existing_number_context(voicemail):
    existing_voicemail = voicemail_dao.get(voicemail.id)
    if voicemail.number_at_context != existing_voicemail.number_at_context:
        validate_number_context(voicemail)


def _check_if_voicemail_linked_on_delete(voicemail):
    if voicemail_dao.is_voicemail_linked(voicemail):
        raise ElementDeletionError('voicemail', 'Cannot delete a voicemail associated to a user')


def _check_if_voicemail_linked_on_edit(voicemail):
    if voicemail_dao.is_voicemail_linked(voicemail):
        raise ElementEditionError('voicemail', 'Cannot edit a voicemail associated to a user')
