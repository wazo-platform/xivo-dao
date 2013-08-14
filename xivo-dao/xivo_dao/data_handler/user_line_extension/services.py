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

import dao
import notifier
import validator

from xivo_dao.data_handler.exception import ElementNotExistsError
from xivo_dao.data_handler.line import services as line_services
from xivo_dao.data_handler.line import dao as line_dao
from xivo_dao.data_handler.user import services as user_services
from xivo_dao.data_handler.extension import services as extension_services
from xivo_dao.data_handler.extension import dao as extension_dao
from xivo import caller_id


def get(ule_id):
    return dao.get(ule_id)


def find_all():
    return dao.find_all()


def find_all_by_user_id(user_id):
    return dao.find_all_by_user_id(user_id)


def find_all_by_extension_id(extension_id):
    return dao.find_all_by_extension_id(extension_id)


def find_all_by_line_id(line_id):
    return dao.find_all_by_line_id(line_id)


def create(ule):
    user, line, extension = validator.validate_create(ule)
    main_user = dao.find_main_user(ule)
    _adjust_optional_parameters(ule, main_user)

    ule = dao.create(ule)

    _make_secondary_associations(user, main_user, line, extension)
    notifier.created(ule)

    return ule


def edit(ule):
    validator.validate(ule)
    dao.edit(ule)
    notifier.edited(ule)


def delete(ule):
    validator.validate(ule)
    dao.delete(ule)
    notifier.deleted(ule)


def delete_everything(ule):
    user, line, extension = validator.validate(ule)
    dao.delete(ule)
    _remove_user(user)
    _remove_line(line)
    _remove_exten(extension)
    notifier.deleted(ule)


def _adjust_optional_parameters(ule, main_user):
    ule.main_line = True
    ule.main_user = (ule.user_id == main_user.id)


def _make_secondary_associations(user, main_user, line, extension):
    _associate_extension(user, extension)
    _associate_line(line, extension, main_user)


def _associate_extension(user, extension):
    extension.type = 'user'
    extension.typeval = str(user.id)
    extension_dao.edit(extension)


def _associate_line(line, extension, main_user):
    line.number = extension.exten
    line.context = extension.context
    callerid, _, _ = caller_id.build_caller_id('', main_user.fullname, extension.exten)
    line.callerid = callerid
    line_dao.edit(line)


def _remove_user(user):
    try:
        user_services.delete(user)
    except ElementNotExistsError:
        return


def _remove_line(line):
    try:
        line_services.delete(line)
    except ElementNotExistsError:
        return


def _remove_exten(extension):
    try:
        extension_services.delete(extension)
    except ElementNotExistsError:
        return
