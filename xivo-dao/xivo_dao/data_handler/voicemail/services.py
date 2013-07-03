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

from xivo_dao.data_handler.voicemail import dao as voicemail_dao
from xivo_dao.helpers import sysconfd_connector
from xivo_dao.data_handler.context import services as context_services
from xivo_dao.data_handler.voicemail import notifier
from xivo_dao.helpers.sysconfd_connector import SysconfdError
from xivo_dao.data_handler.exception import MissingParametersError, \
    InvalidParametersError, ElementAlreadyExistsError


def find_all():
    return voicemail_dao.find_all()


def find_by_number_context(number, context):
    return voicemail_dao.find_voicemail(number, context)


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


def _check_missing_parameters(voicemail):
    missing = voicemail.missing_parameters()
    if missing:
        raise MissingParametersError(missing)


def _check_invalid_parameters(voicemail):
    invalid_parameters = []
    if not voicemail.name:
        invalid_parameters.append('name')
    if not voicemail.number.isdigit():
        invalid_parameters.append('number')
    if not context_services.find_by_name(voicemail.context):
        invalid_parameters.append('context')
    if invalid_parameters:
        raise InvalidParametersError(invalid_parameters)


def _check_for_existing_voicemail(voicemail):
    if voicemail_dao.find_voicemail(voicemail.number, voicemail.context):
        number_at_context = voicemail.number_at_context
        raise ElementAlreadyExistsError('Voicemail', number_at_context)
