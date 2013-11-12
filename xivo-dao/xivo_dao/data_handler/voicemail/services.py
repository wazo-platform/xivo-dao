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


from xivo_dao.data_handler.voicemail import dao as voicemail_dao
from xivo_dao.data_handler.voicemail import notifier
from xivo_dao.data_handler.voicemail import validator

from xivo_dao.helpers import sysconfd_connector
from xivo_dao.helpers.sysconfd_connector import SysconfdError


def find_all(skip=None, limit=None, order=None, direction=None, search=None):
    return voicemail_dao.find_all(skip=skip, limit=limit, order=order, direction=direction, search=search)


def find_all_timezone():
    return voicemail_dao.find_all_timezone()


def get_by_number_context(number, context):
    return voicemail_dao.get_by_number_context(number, context)


def get(voicemail_id):
    return voicemail_dao.get(voicemail_id)


def create(voicemail):
    validator.validate_create(voicemail)
    voicemail = voicemail_dao.create(voicemail)
    notifier.created(voicemail)
    return voicemail


def edit(voicemail):
    validator.validate_edit(voicemail)
    voicemail_dao.edit(voicemail)
    notifier.edited(voicemail)


def delete(voicemail):
    validator.validate_delete(voicemail)
    voicemail_dao.delete(voicemail)
    notifier.deleted(voicemail)
    try:
        sysconfd_connector.delete_voicemail_storage(voicemail.number, voicemail.context)
    except Exception as e:
        raise SysconfdError(str(e))
