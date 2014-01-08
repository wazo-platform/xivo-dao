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

from xivo_dao.data_handler.line import dao as line_dao
from xivo_dao.data_handler.user_line import validator, dao, notifier
from xivo_dao.data_handler.line_extension import dao as line_extension_dao
from xivo_dao.data_handler.user_line_extension import helper as ule_helper


def get_by_user_id_and_line_id(user_id, line_id):
    return dao.get_by_user_id_and_line_id(user_id, line_id)


def find_all_by_user_id(user_id):
    return dao.find_all_by_user_id(user_id)


def find_all_by_line_id(line_id):
    return dao.find_all_by_line_id(line_id)


def associate(user_line):
    validator.validate_association(user_line)
    _adjust_optional_parameters(user_line)
    dao.associate(user_line)
    make_user_line_associations(user_line)
    notifier.associated(user_line)
    return user_line


def make_user_line_associations(user_line):
    main_user_line = dao.find_main_user_line(user_line.line_id)
    line_extension = line_extension_dao.find_by_line_id(user_line.line_id)
    extension_id = line_extension.extension_id if line_extension else None
    ule_helper.make_associations(main_user_line.user_id, user_line.line_id, extension_id)


def dissociate(user_line):
    validator.validate_dissociation(user_line)
    dao.dissociate(user_line)
    notifier.dissociated(user_line)
    delete_user_line_associations(user_line)


def delete_user_line_associations(user_line):
    line_extension = line_extension_dao.find_by_line_id(user_line.line_id)
    main_user_line = dao.find_main_user_line(user_line.line_id)

    if not main_user_line:
        line_dao.delete_user_references(user_line.line_id)
        if line_extension:
            ule_helper.delete_extension_associations(line_extension.line_id, line_extension.extension_id)


def _adjust_optional_parameters(user_line):
    user_line_main_user = dao.find_main_user_line(user_line.line_id)
    if user_line_main_user is not None:
        user_line.main_user = (user_line.user_id == user_line_main_user.user_id)
